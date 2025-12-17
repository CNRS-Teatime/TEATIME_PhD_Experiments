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

    """ for node in thesoList[i]['nodes']:
        node["_id"] = curr_thesoconfig['name'] + '/' + node["id"]
        del node["id"] """ 

    print(nodes.insert_many(thesoList[i]['nodes']))

    print("Processing edges")

    # FIXME : Apply correct vertexKeys
    for edge in thesoList[i]['relationships']:
        edge["_from"] = curr_thesoconfig['name'] + '/' + edge["start"]
        del edge["start"]
        edge["_to"] = curr_thesoconfig['name'] + '/' + edge["end"]
        del edge["end"]

    print(thesoList[i]['relationships'])

    print(edges.insert_many(thesoList[i]['relationships']))
