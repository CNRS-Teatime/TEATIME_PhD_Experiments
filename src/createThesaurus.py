""" 
Create two new collections from an opentheso database graph
The scripts takes a JSON config file in entry
"""
import json, requests, sys
from arango import ArangoClient, database
from jsonschema import validate, ValidationError


def get_config(config_path: str) -> dict:
    """
    Parse the configuration file and validate it against the JSON schema.

    :param config_path: A path to the configuration file
    :type config_path: str

    :return: A dictionary containing the validated configuration JSON
    """
    with open(config_path) as file:
        config_list = json.load(file)
        with open("theso-config-schema.json") as schemafile:
            schema = json.load(schemafile)
            try :
                validate(config_list, schema)
            except ValidationError:
                print("YOUR CONFIG FILE IS INVALID")
                raise 
            return config_list


def insert_thesaurus(db : database.StandardDatabase, thesaurus_config : dict, thesaurus : dict):
    """
    Insert a thesaurus into a designated Arango Database using its configuration and JSON. If the insertion is unsuccesful, the tuple will contain two empty lists.
    
    :param db: The arango database API wrapper
    :type db: arango.database.StandardDatabase
    :param thesaurus_config: (part of) the JSON config for the desired thesaurus, containing its name and source
    :type thesaurus_config: dict
    :param thesaurus: The full JSON of the desired thesaurus, with an entry for each node and edge.
    :type thesaurus: dict

    :return: The list of skipped edges, and the list of added edges, in this order.
    """ 
    skipped_edges = []

    # Chekc if collection already exists
    # Otherwise we create it
    if db.has_collection(thesaurus_config['name']):
        nodes = db.collection(thesaurus_config['name'])
        edges = db.collection(thesaurus_config['name'] + "_EDGES")
    else:
        nodes = db.create_collection(thesaurus_config['name'])
        edges = db.create_collection(thesaurus_config['name'] + "_EDGES", edge=True)

    nodes.truncate()
    edges.truncate()

    print("Processing nodes...")

    new_nodes = nodes.insert_many(thesaurus['nodes'], return_new=True)

    print("Processing edges...")

    skip = 0

    for edge in thesaurus['relationships']:

        start = next((item for item in new_nodes if item['new']['id'] == edge["start"]), False) # Searching for node wich original id was the edge start
        to = next((item for item in new_nodes if item['new']['id'] == edge["end"]), False)

        if start and to:
            edge["_from"] = start['_id']
            del edge["start"]
            
            edge["_to"] = to['_id']
            del edge["end"]

        else:
            skip += 1
            skipped_edges.append(edge)
            del edge

    print(f"Skipped {skip} edges out of {len(thesaurus['relationships'])}")

    result = edges.insert_many(thesaurus['relationships'], silent=True, raise_on_document_error=True)

    if result:
        print(f"Succesfully imported thesaurus {thesaurus_config['name']}")
        return skipped_edges, new_nodes
    
    return [], [] #Import was unsuccessful so we return nothing


def fetch_thesaurus(thesori_config_list: dict):
    """  
    Goes throught the list of thesaurus configuration and fetches each one individually via a REST GET request
    """
    theso_list = []
    for thesaurus in thesori_config_list:
        api_url = thesaurus["source"]
        print(f"Requesting thesaurus {api_url} ...")
        response = requests.get(api_url)
        if response.status_code == 200:
            theso_list.append(response.json())
            print(f"Thesaurus {thesaurus['source']} succesfully fetched from remote")
        else :
            print(f"Error fetching thesaurus {thesaurus['source']}")
    return theso_list


def generate_inter_thesauri_edges(db : database.StandardDatabase, all_nodes : list, edges : list):
    """
    Here we take into account the inter-thesauri edges, the objective is to be able to create a "master" graph that links all thesaurus graphs
    increasing exhaustivity and interconnection. The edges are put in their own separate Shared_EDGES collection. This is the only edges collection
    that is not exclusively linking nodes from a single NODES collection.

    :param db: The arango database API wrapper
    :type db: arango.database.StandardDatabase
    :param all_nodes: A list of all nodes that exists in the database, this is necessary to get the internal ArangoDB IDs
    :type all_nodes: list
    :param edges: A list of all the edges we need to create
    :type edges: list
    """
    for edge in edges :
        if not edge:
            break

        start = next((item for item in all_nodes if item['new']['id'] == edge["start"]), False) # Searching for node wich original id was the edge start
        to = next((item for item in all_nodes if item['new']['id'] == edge["end"]), False)

        if start and to:
            edge["_from"] = start['_id']
            del edge["start"]
            
            edge["_to"] = to['_id']
            del edge["end"]

        else:
            del edge

    # Check if collection already exists
    # Otherwise we create it
    if db.has_collection("Shared_EDGES"):
        edges = db.collection("Shared_EDGES")
    else:
        edges = db.create_collection("Shared_EDGES", edge=True)

    edges.insert_many(edges, silent=True, raise_on_document_error=True)





if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Please provide config file path as first argument")
        sys.exit()

    config = get_config(sys.argv[1])
    credentials = config['credentials']
    thesoList = fetch_thesaurus(config["thesauri"])
    client = ArangoClient(hosts=credentials['host'])
    all_new_nodes = []
    interThesaurusEdges = []

    # Connect to "_system" database as root user.
    # This returns an API wrapper for "_system" database.
    sys_db = client.db('_system', username='root', password='test')

    # Create the database associated with the thesaurus if it does not exist yet
    if not sys_db.has_database(credentials['database']):
        sys_db.create_database(credentials['database'])

    database = client.db(credentials['database'], username=credentials['username'], password=credentials['password'])


    for i in range(len(thesoList)):
        skipped, added = insert_thesaurus(database, config["thesauri"][i], thesoList[i])
        interThesaurusEdges += skipped
        all_new_nodes += added

    if interThesaurusEdges != [[]] and all_new_nodes != []:
        generate_inter_thesauri_edges(database, all_new_nodes, interThesaurusEdges)