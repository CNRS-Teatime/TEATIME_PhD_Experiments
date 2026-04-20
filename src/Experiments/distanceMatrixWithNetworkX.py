from arango import ArangoClient, database
import networkx as nx
from time import time

def fetch_from_arango(doc_collections : list, edge_collections : list, database_name : str) -> tuple[list, nx.DiGraph]:
    client = ArangoClient(hosts="http://localhost:8529")
    db: database.StandardDatabase = client.db(database_name, username="root", password="test")

    document_ids: list = []

    for coll in doc_collections:
        thesaurus_documents: database.StandardCollection = db.collection(coll)

        documents_cursor = thesaurus_documents.all()
        document_ids.extend([doc['_id'] for doc in documents_cursor])

    edges_as_list : list = []

    for coll in edge_collections:
        edge_coll: database.StandardCollection = db.collection(coll)
        edge_cursor = edge_coll.all()
        edges_as_list.extend([(edge['_from'], edge['_to'], int(edge['weight'])) for edge in edge_cursor])

    G: nx.DiGraph = nx.DiGraph()
    G.add_nodes_from(document_ids)
    G.add_weighted_edges_from(edges_as_list)

    return document_ids, G


def compute_matrix(G : nx.DiGraph, document_ids_as_list) -> list:
    length = dict(nx.all_pairs_bellman_ford_path_length(G, weight='weight'))
    n = len(document_ids_as_list)

    fail = 0

    matrix = [[0 for i in range(n)] for j in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            if i != j:
                if document_ids_as_list[i] in length:
                    if document_ids_as_list[j] in length[document_ids_as_list[i]]:
                        distance = length[document_ids_as_list[i]][document_ids_as_list[j]]
                    else:
                        distance = 10000000
                        fail += 1
                else:
                    raise ArithmeticError
            else:
                distance = 0

            matrix[i][j] = matrix[j][i] = distance

    print(f"Fails {(fail/(n*n)) * 100}%")
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
    DATABASE = "TEATIME-Exp"
    DOCUMENT_COLLECTIONS = ["th12",
                        "th13",
                        "th15",
                        "th16",
                        "th18",
                        "th21",
                        "th52",
                        "th53",
                        "th56",
                        "th57",
                        "th58",
                        "th59"]
    EDGE_COLLECTIONS = ["intraTheso_relations",
                        "th12_relations",
                        "th13_relations",
                        "th15_relations",
                        "th16_relations",
                        "th18_relations",
                        "th21_relations",
                        "th52_relations",
                        "th53_relations",
                        "th56_relations",
                        "th57_relations",
                        "th58_relations",
                        "th59_relations"
                        ]
    GRAPH_NAME = "IntraTheso"

    doc_id_list, G = fetch_from_arango(DOCUMENT_COLLECTIONS, EDGE_COLLECTIONS, DATABASE)

    matrix = compute_matrix(G, doc_id_list)

    print(f"{len(matrix)} x {len(matrix[0])} matrix produced")

    write_matrix_to_file(f"distance_matrix_{GRAPH_NAME}.csv", doc_id_list)
