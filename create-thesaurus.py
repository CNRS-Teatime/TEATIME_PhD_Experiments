""" 
Create two new collections from an opentheso database graph
The scripts takes a json config file in entry
"""
import json, requests
from arango import ArangoClient
from jsonschema import validate, ValidationError

"""
Parse the configuration file and validate it against the JSON schema.
"""
def getConfig(configPath):
    with open(configPath) as file:
        configList = json.load(file)
        with open("theso-config-schema.json") as schemafile:
            schema = json.load(schemafile)
            try :
                validate(configList, schema)
            except ValidationError:
                print("YOUR CONFIG FILE IS INVALID")
                raise 
            return configList
            
"""  
Goes throught the list of thesaurus configuration and fetches each one individually via a REST GET request
"""
def fetchThesaurus(thesoriConfigList):
    thesoList = []
    for thesaurus in thesoriConfigList:
        api_url = thesaurus["source"]
        print(f"Requesting thesaurus {api_url} ...")
        response = requests.get(api_url)
        if response.status_code == 200:
            thesoList.append(response.json())
            print(f"Thesaurus {thesaurus['source']} succesfully fetched from remote")
        else :
            print(f"Error fetching thesaurus {thesaurus['source']}")
    return thesoList



config = getConfig("config.json")
credentials = config['credentials']
thesoList = fetchThesaurus(config["thesauri"])
client = ArangoClient(hosts=credentials['host'])
interThesaurusEdges = []
all_nodes = []

for i in range(len(thesoList)):
    curr_thesoconfig = config["thesauri"][i]

    # Connect to "_system" database as root user.
    # This returns an API wrapper for "_system" database.
    sys_db = client.db('_system', username='root', password='test')

    # Create the database associated with the thesaurus if it does not exist yet
    if not sys_db.has_database(curr_thesoconfig['database']):
        sys_db.create_database(curr_thesoconfig['database'])

    curr_db = client.db(curr_thesoconfig['database'], username=credentials['username'], password=credentials['password'])

    # Chekc if collection already exists
    # Otherwise we create it
    if curr_db.has_collection(curr_thesoconfig['name']):
        nodes = curr_db.collection(curr_thesoconfig['name'])
        edges = curr_db.collection(curr_thesoconfig['name'] + "_EDGES")
    else:
        nodes = curr_db.create_collection(curr_thesoconfig['name'])
        edges = curr_db.create_collection(curr_thesoconfig['name'] + "_EDGES", edge=True)

    nodes.truncate()
    edges.truncate()

    print("Processing nodes...")

    new_nodes = nodes.insert_many(thesoList[i]['nodes'], return_new=True)

    all_nodes += new_nodes

    print("Processing edges...")

    skip = 0

    for edge in thesoList[i]['relationships']:
        start = next((item for item in new_nodes if item['new']['id'] == edge["start"]), False) # Searching for node wich original id was the edge start
        to = next((item for item in new_nodes if item['new']['id'] == edge["end"]), False)

        if start and to:
            edge["_from"] = start['_id']
            del edge["start"]
            
            edge["_to"] = to['_id']
            del edge["end"]

        else:
            skip += 1
            interThesaurusEdges.append(edge)
            del edge

    print(f"Skipped {skip} edges out of {len(thesoList[i]['relationships'])}")

    result = edges.insert_many(thesoList[i]['relationships'], silent=True, raise_on_document_error=True)

    if result:
        print(f"Succesfully imported thesaurus {curr_thesoconfig['name']}")

# Here we take into account the inter-thesauri edges, the objective is to be able to create a "master" graph that links all thesaurus graphs
# increasing exhaustivity and interconnection
for edge in interThesaurusEdges :
    start = next((item for item in all_nodes if item['new']['id'] == edge["start"]), False) # Searching for node wich original id was the edge start
    to = next((item for item in all_nodes if item['new']['id'] == edge["end"]), False)

    if start and to:
        edge["_from"] = start['_id']
        del edge["start"]
        
        edge["_to"] = to['_id']
        del edge["end"]

    else:
        del edge

edges = curr_db.create_collection("Shared_EDGES", edge=True)
edges.insert_many(interThesaurusEdges, silent=True, raise_on_document_error=True)