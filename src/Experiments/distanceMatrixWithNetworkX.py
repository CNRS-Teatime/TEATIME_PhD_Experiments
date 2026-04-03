from arango import ArangoClient, database
import networkx as nx
from time import time

def fetch_from_arango(doc_collection : str, edge_collection : str) -> tuple[list, nx.DiGraph]:
    client = ArangoClient(hosts="http://localhost:8529")
    db: database.StandardDatabase = client.db("TEATIME", username="root", password="test")
    thesaurus_documents: database.StandardCollection = db.collection(doc_collection)

    documents_cursor = thesaurus_documents.all()
    document_ids: list = [doc['_id'] for doc in documents_cursor]

    edge_coll: database.StandardCollection = db.collection(edge_collection)
    edge_cursor = edge_coll.all()
    edges_as_list: list = [(edge['_from'], edge['_to'], int(edge['weight'])) for edge in edge_cursor]

    G: nx.DiGraph = nx.DiGraph()
    G.add_nodes_from(document_ids)
    G.add_weighted_edges_from(edges_as_list)

    return document_ids, G


def compute_matrix(G : nx.DiGraph, document_ids_as_list) -> list:
    length = dict(nx.all_pairs_bellman_ford_path_length(G, weight='weight'))
    n = len(document_ids_as_list)

    matrix = [[0 for i in range(n)] for j in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            if i != j:
                if document_ids_as_list[i] in length:
                    if document_ids_as_list[j] in length[document_ids_as_list[i]]:
                        distance = length[document_ids_as_list[i]][document_ids_as_list[j]]
                    else:
                        distance = 10000000
                else:
                    raise ArithmeticError
            else:
                distance = 0

            matrix[i][j] = matrix[j][i] = distance

    return matrix

def write_matrix_to_file(file_name, document_id_list) -> None:

    with open(file_name, 'w') as f:
        id_string: str = ""
        for i in range(len(document_id_list)):
            if i == len(document_id_list) - 1:
                id_string += str(document_id_list[i]) + '\n'
            else:
                id_string += str(document_id_list[i]) + ','
        f.write(id_string)

        for line in matrix :
            line_string : str = ""
            for i in range(len(line)):
                if i == len(line) - 1:
                    line_string += str(line[i]) + '\n'
                else:
                    line_string += str(line[i]) + ','
            f.write(line_string)

if __name__ == "__main__":
    DOCUMENT_COLLECTION = "th15"
    EDGE_COLLECTION = "th15_relations"
    GRAPH_NAME = "th15_graph"

    doc_id_list, G = fetch_from_arango(DOCUMENT_COLLECTION, EDGE_COLLECTION)

    matrix = compute_matrix(G, doc_id_list)

    write_matrix_to_file(f"distance_matrix_{GRAPH_NAME}.csv", doc_id_list)
