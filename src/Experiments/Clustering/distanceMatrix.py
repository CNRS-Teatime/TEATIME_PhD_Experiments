from arango import ArangoClient, database
import networkx as nx

def fetch_from_arango(edge_collections : list[str], database_name : str) -> nx.DiGraph:
    """
    From a list of edge collection, fetches the objects in those collection in the associated database.
    Those edges are inserted inside a networkx directed graph, which is returned by the function

    :param edge_collections: A list of collection name
    :type edge_collections: list[str]
    :param database_name: The name of the database the funciton will use to fetch the collections
    :type database_name: str
    :returns: A networkx directed graph with the fetched edges and arangodb document ids as node labels.
    """

    client = ArangoClient(hosts="http://localhost:8529")
    db: database.StandardDatabase = client.db(database_name, username="root", password="test")

    edges_as_list : list = []

    for coll in edge_collections:
        edge_coll: database.StandardCollection = db.collection(coll)
        edge_cursor = edge_coll.all()
        edges_as_list.extend([(edge['_from'], edge['_to'], int(edge['weight'])) for edge in edge_cursor])

    Gr: nx.DiGraph = nx.DiGraph()
    Gr.add_weighted_edges_from(edges_as_list)

    return Gr


def compute_matrix(graph : nx.DiGraph) -> list[list[int]]:
    """
    Computes a pairwise distance matrix for all the nodes in the given networkx Directed graph.

    :param graph: Any networkX directed graph with labeled nodes
    :type graph: networkx.DiGraph
    :return: A 2D matrix in the form of a list of list of ints
    """
    bf_path_length_dict : dict = dict(nx.all_pairs_bellman_ford_path_length(graph, weight='weight'))
    document_ids_as_list : list[str] = list(graph.nodes._nodes.keys())
    n = len(document_ids_as_list) # number of nodes

    fail = 0

    # Initializing an n by n zero matrix where n is the number of nodes in the graph
    distance_matrix : list[list[int]] = [[0 for i in range(n)] for j in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            if i != j:
                if document_ids_as_list[i] in bf_path_length_dict:
                    if document_ids_as_list[j] in bf_path_length_dict[document_ids_as_list[i]]: # The dictionary returned only has keys for reachable node pairs.
                        distance = bf_path_length_dict[document_ids_as_list[i]][document_ids_as_list[j]]
                    else: # The node pair is not reachable
                        distance = 10000000 # TODO : I need to find a better way
                        fail += 1
                else: # All nodes must have an outgoing entry in the matrix
                    raise ArithmeticError
            else: # Same node so no distance
                distance = 0

            distance_matrix[i][j] = distance_matrix[j][i] = distance

    print(f"Fails {(fail/(n*n)) * 100}%") # TODO : Maybe log this into a log file for safekeeping
    return distance_matrix

def write_matrix_to_file(file_name : str, document_id_list : list[str], mat: list[list[int]]) -> None:
    """
    Write the distance matrix as a csv into a given file.
    The first row is the list of document ids.
    The others contain a row of commas separated ints, for each row in the matrix.
    The matrix can take a long time to compute, but we will reuse it a lot later on so this is useful

    :param file_name: The name of the file
    :type file_name: str
    :param document_id_list: A vector of document ids, in the same order they appear in the matrix
    :type document_id_list: list[str]
    :param mat: A 2D distance matrix
    :type mat: list[list[int]]
    """

    with open(file_name, 'w') as f:
        id_string: str = ""
        for i in range(len(document_id_list)):
            if i == len(document_id_list) - 1:
                id_string += str(document_id_list[i]) + '\n'
            else:
                id_string += str(document_id_list[i]) + ','
        f.write(id_string)

        for line in mat :
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

    G = fetch_from_arango( EDGE_COLLECTIONS, DATABASE)



    matrix = compute_matrix(G)

    print(f"{len(matrix)} x {len(matrix[0])} matrix produced")

    write_matrix_to_file(f"distance_matrix_{GRAPH_NAME}.csv", list(G.nodes._nodes.keys()), matrix)
