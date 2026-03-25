from arango import ArangoClient, database
import networkx as nx
from time import time

DOCUMENT_COLLECTION = "th15"
EDGE_COLLECTION = "th15_relations"
GRAPH_NAME = "th15_graph"

client = ArangoClient(hosts="http://localhost:8529")
db : database.StandardDatabase = client.db("TEATIME", username="root", password="test")
thesaurus_documents : database.StandardCollection = db.collection(DOCUMENT_COLLECTION)

documents_cursor = thesaurus_documents.all()
doc_id_list : list = [doc['_id'] for doc in documents_cursor]
nb_concepts = len(doc_id_list)

edge_collection : database.StandardCollection = db.collection(EDGE_COLLECTION)
edge_cursor = edge_collection.all()
edges_as_list : list = [(edge['_from'], edge['_to'], int(edge['weight'])) for edge in edge_cursor]

G : nx.DiGraph = nx.DiGraph()
G.add_nodes_from(doc_id_list)
G.add_weighted_edges_from(edges_as_list)

print(f"Document list is of length {len(doc_id_list)} and edge list is of lenght {len(edges_as_list)}")
print(f"The graph contains {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

start = time()

length = dict(nx.all_pairs_bellman_ford_path_length(G, weight='weight'))

"""
The length dictionnary is of form {
'ID1' : {'ID2' : NUMBER, 'ID3' : NUMBER, ... },
'ID2 : {'ID1' : NUMBER, 'ID3' : NUMBER, ...},
...
}
"""

end = time()

matrix = [[0 for i in range(nb_concepts)] for j in range(nb_concepts)]

for i in range(nb_concepts):
    for j in range(i + 1, nb_concepts):
        if i != j :
            if doc_id_list[i] in length:
                if doc_id_list[j] in length[doc_id_list[i]]:
                    distance = length[doc_id_list[i]][doc_id_list[j]]
                else:
                    distance = 10000000
            else:
                raise ArithmeticError
        else:
            distance = 0

        matrix[i][j] = matrix[j][i] = distance

print(f"Total runtime : {end - start}s")

with open(f"distance_matrix_{GRAPH_NAME}.csv", 'w') as f:
    id_string: str = ""
    for i in range(nb_concepts):
        if i == nb_concepts - 1:
            id_string += str(doc_id_list[i]) + '\n'
        else:
            id_string += str(doc_id_list[i]) + ','
    f.write(id_string)

    for line in matrix :
        line_string : str = ""
        for i in range(len(line)):
            if i == len(line) - 1:
                line_string += str(line[i]) + '\n'
            else:
                line_string += str(line[i]) + ','
        f.write(line_string)