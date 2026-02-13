""" 
Create two new collections from an opentheso database graph
The scripts takes a JSON config file in entry
"""
import json, requests, sys
from arango import ArangoClient, database
from jsonschema import validate, ValidationError


def get_config(config_path: str, schema_path: str = None) -> dict:
    """
    Parse the configuration file and validate it against the JSON schema.

    :param config_path: A path to the JSON configuration file
    :type config_path: str

    :param schema_path: A path to the JSON schema (optional)
    :type schema_path: str

    :return: A dictionary containing the validated configuration JSON
    """
    with open(config_path) as file:
        config_list = json.load(file)

        if schema_path is None:
            return config_list
        # If we've got a schema we validate against it
        with open(schema_path) as schemafile:
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

    # Chekc if collection already exists we delete it
    if db.has_collection(thesaurus_config['name']):
        db.delete_collection(thesaurus_config['name'])
        db.delete_collection(thesaurus_config['name'] + "_EDGES")

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


def fetch_thesaurus(thesori_config_list: dict) -> list:
    """  
    Goes throught the list of thesaurus configuration and fetches each one individually via a REST GET request
    """
    theso_list : list = []
    for thesaurus in thesori_config_list:
        api_url : str = thesaurus["source"]
        print(f"Requesting thesaurus {api_url} ...")
        response : requests.models.Response  = requests.get(api_url)
        if response.status_code == 200:
            theso_list.append(response.json())
            print(f"Thesaurus {thesaurus['source']} succesfully fetched from remote")
        else :
            print(f"Error fetching thesaurus {thesaurus['source']}")
    return theso_list


def generate_inter_thesauri_edges(db : database.StandardDatabase, all_nodes : list, edges : list) -> list:
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
    i = 0
    length = len(edges)
    while i < length:
        if not edges[i]:
            del edges[i]
            break

        start : dict = {}
        to : dict = {}
        for item in all_nodes:
            if item['new']['id'] == edges[i]['start']:
                start = item
            if item['new']['id'] == edges[i]['end']:
                to = item

        if start != {} and to != {}:
            edges[i]["_from"] = start['_id']
            del edges[i]["start"]
            
            edges[i]["_to"] = to['_id']
            del edges[i]["end"]
        else:
            del edges[i]
            length -= 1
            i -= 1

        i += 1

    # Check if collection already exists
    # Otherwise we create it
    if db.has_collection("Shared_EDGES"):
        db.delete_collection("Shared_EDGES")

    edges_collection : database.StandardCollection = db.create_collection("Shared_EDGES", edge=True)

    print("Inserted Shared_EDGES")
    return edges_collection.insert_many(edges, return_new=True)

# These two functions work on a different kind of import, which is much more detailed

def create_thesaurus_dict(parsed_thesaurus : dict) -> list:

    thesaurus : list = []

    for entry in parsed_thesaurus:
        # Here we prepare the schema for each annotation
        # Comments next to key value pairs are the URI's associated with them in the original data
        annotation: dict = {
            "_key": entry.split("/")[-1],  # The id is the last element of the URI separated by /
            "labels": [],  # http://www.w3.org/2004/02/skos/core#prefLabel Remove the type from this one
            "type": None,  # http://www.w3.org/1999/02/22-rdf-syntax-ns#type
            "created": None,  # http://purl.org/dc/terms/created
            "modified": None,  # http://purl.org/dc/terms/modified
            "description": None,  # http://purl.org/dc/terms/description Remove the type
            "ark": entry,  # The key value of the entry
            "name": None,  # The first label value
            "note": None,  # "http://www.w3.org/2004/02/skos/core#scopeNote"
            "definition": None,  # http://www.w3.org/2004/02/skos/core#definition
        }

        # The data being semi-structured we have to check if the key exists before doing anything with it

        if "http://www.w3.org/2004/02/skos/core#prefLabel" in parsed_thesaurus[entry]:
            annotation["labels"] = parsed_thesaurus[entry]["http://www.w3.org/2004/02/skos/core#prefLabel"]
        for label in annotation["labels"]:
            del label["type"]

            # We do not have a name without a label so we define it here
            annotation["name"] = annotation["labels"][0]["value"]

        if "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in parsed_thesaurus[entry]:
            try:  # We only want the skos types
                annotation["type"] = parsed_thesaurus[entry]["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"][0]["value"].split("#")[1]
                pass
            except IndexError:  # Otherwise we skip the entry
                print(parsed_thesaurus[entry]["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"][0]["value"])
                continue

        if annotation["type"] != "Concept":  # We only want to get concepts
            continue

        if "http://purl.org/dc/terms/created" in parsed_thesaurus[entry]:
            annotation["created"] = parsed_thesaurus[entry]["http://purl.org/dc/terms/created"][0]["value"]

        if "http://purl.org/dc/terms/modified" in parsed_thesaurus[entry]:
            annotation["modified"] = parsed_thesaurus[entry]["http://purl.org/dc/terms/modified"][0]["value"]

        if "http://purl.org/dc/terms/description" in parsed_thesaurus[entry]:
            annotation["description"] = parsed_thesaurus[entry]["http://purl.org/dc/terms/description"][0]
            del annotation["description"]["type"]

        if "http://www.w3.org/2004/02/skos/core#scopeNote" in parsed_thesaurus[entry]:
            annotation["note"] = parsed_thesaurus[entry]["http://www.w3.org/2004/02/skos/core#scopeNote"][0]["value"]

        if "http://www.w3.org/2004/02/skos/core#definition" in parsed_thesaurus[entry]:
            annotation["definition"] = parsed_thesaurus[entry]["http://www.w3.org/2004/02/skos/core#definition"][0]["value"]

        thesaurus.append(annotation)
    return thesaurus

def create_thesaurus_relations(parsed_thesaurus : dict, thesaurus_name : str) -> list:
    # I could have done it all inside of a single function, but I'm splitting for readability (in spite of performance) since
    # we won't do this often, and it is bottlenecked by the internet connexion anyway
    relations_list : list = []

    for entry in parsed_thesaurus:
        to_key : str = thesaurus_name + '/' +  entry.split("/")[-1] # Each entry defines the incoming relations, so we have the same _from key

        # We will create a relation for each entry in the broader, narrower, related, closematch and exactmatch list
        # TODO : demander a violette pour les relations specifiques du TH56

        broader : str = "http://www.w3.org/2004/02/skos/core#broader"
        narrower : str = "http://www.w3.org/2004/02/skos/core#narrower"
        related : str = "http://www.w3.org/2004/02/skos/core#related"
        close_match : str = "http://www.w3.org/2004/02/skos/core#closeMatch"
        exact_match : str = "http://www.w3.org/2004/02/skos/core#exactMatch"


        # The data being semi-structured we have to check if the key exists before doing anything with it

        if broader in parsed_thesaurus[entry]:
            for relation in parsed_thesaurus[entry][broader]:
                relations_list.append({
                    "_from" : thesaurus_name + '/' + relation["value"].split("/")[-1],
                    "_to" : to_key,
                    "type" : "broader"
                })

        if narrower in parsed_thesaurus[entry]:
            for relation in parsed_thesaurus[entry][narrower]:
                relations_list.append({
                    "_from" : thesaurus_name + '/' + relation["value"].split("/")[-1],
                    "_to" : to_key,
                    "type" : "narrower"
                })

        if related in parsed_thesaurus[entry]:
            for relation in parsed_thesaurus[entry][related]:
                relations_list.append({
                    "_from" : thesaurus_name + '/' + relation["value"].split("/")[-1],
                    "_to" : to_key,
                    "type" : "related"
                })

    return relations_list






if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Please provide config file path as first argument")
        sys.exit()

    config = get_config(sys.argv[1], "config/theso-config-schema.json")
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
        print(generate_inter_thesauri_edges(database, all_new_nodes, interThesaurusEdges))