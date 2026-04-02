
import sys, os
from thesaurusCreator import get_config
from arango import ArangoClient, database, graph

def create_graph(db : database.StandardDatabase, graph_list : list) -> None:
    """Creates the desired graph from a JSON configuration file stored as a dict"""
    for g in graph_list:
        if db.has_graph(g["name"]):
            db.delete_graph(g["name"])

        curr_graph = db.create_graph(g["name"])

        #Creating the edge definitions
        for definition in g["relations"]:
            curr_graph.create_edge_definition(
                edge_collection = definition["edge_collection"],
                from_vertex_collections = definition["from_vertex_collections"],
                to_vertex_collections = definition["to_vertex_collections"]
            )
        print(f"Created graph {g["name"]}")

def create_graph_from_config(config_path : str):
    config: dict = get_config(config_path, "config/graph-config-schema.json")
    graphs: list = config["graphs"]

    client: ArangoClient = ArangoClient(hosts=os.getenv("DB_ADDRESS"))
    curr_db: database.StandardDatabase = client.db(name=os.getenv("DB_NAME"), username=os.getenv("DB_USER"),
                                                   password=os.getenv("DB_PASSWORD"))

    create_graph(curr_db, graphs)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Please provide config file path as first argument")
        sys.exit()

    create_graph_from_config(sys.argv[1])
