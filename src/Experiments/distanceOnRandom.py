from arango import ArangoClient, database
from random import randint

client = ArangoClient(hosts="http://localhost:8529")
db : database.StandardDatabase = client.db("TEATIME", username="root", password="test")
thesaurus_documents : database.StandardCollection = db.collection("th15")
graph_name = "th15_graph"
#%%
documents_cursor = thesaurus_documents.all()
thesaurus_doc_id_as_list : list = [doc['_id'] for doc in documents_cursor] # Pour choisir deux concepts au hasard dans notre query
print(thesaurus_doc_id_as_list[:10])

id1 = thesaurus_doc_id_as_list[randint(0, len(thesaurus_doc_id_as_list))]
id2 = thesaurus_doc_id_as_list[randint(0, len(thesaurus_doc_id_as_list))]

while id1 == id2:
    id2 = thesaurus_doc_id_as_list[randint(0, len(thesaurus_doc_id_as_list))]

result = db.aql.execute("FOR node, edge \
                IN ANY SHORTEST_PATH \
                @ID_1 TO @ID_2 \
                GRAPH @Graph_name \
                RETURN [node.name, edge.type, edge.weight]",
               bind_vars={"ID_1": id1, "ID_2" : id2, "Graph_name" : graph_name})

print("")
print("Shortest path without weights taken into account :")
print("")

print(f"({result.next()[0]})", end='')

nbEdge = 0
distance = 0

for thing in result:
    distance += thing[2]
    nbEdge += 1
    print(f" <--{thing[1]}--", end='')
    if thing[1] != "narrower" and thing[1] != "broader":
        print(f">", end='')

    print(f" ({thing[0]})", end='')

print("")
print(f"Distance = {distance}, nombre de relations = {nbEdge}")

result = db.aql.execute("FOR node, edge \
                IN ANY SHORTEST_PATH \
                @ID_1 TO @ID_2 \
                GRAPH @Graph_name \
                OPTIONS { \
                  weightAttribute : 'weight' \
                }\
                RETURN [node.name, edge.type, edge.weight]",
               bind_vars={"ID_1": id1, "ID_2" : id2, "Graph_name" : graph_name})
print("")
print("Shortest path with weights taken into account :")
print("")
print(f"({result.next()[0]})", end='')

distance = 0
nbEdge = 0

for thing in result:
    distance += thing[2]
    nbEdge += 1
    print(f" <--{thing[1]}--", end='')
    if thing[1] != "narrower" and thing[1] != "broader":
        print(f">", end='')

    print(f" ({thing[0]})", end='')

print("")
print(f"Distance = {distance}, nombre de relations = {nbEdge}")