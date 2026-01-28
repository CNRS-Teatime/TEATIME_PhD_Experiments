"""
This package will read every thesaurus edges contained inside the database and return a csv with the names and counts (per thesaurus)
"""

from arango import ArangoClient, database

# AQL does not let us dynamicaly iterate over collections when querying so we need to get the collections name and iterate on the client
def get_all_edge_col_names(db: database.StandardDatabase) -> list:
    cursor = db.aql.execute(
        "FOR c IN COLLECTIONS() \
            FILTER LIKE(c.name, '%_EDGES') \
            RETURN c.name")
    return [name for _ in cursor]


def count_labels(db: database.StandardDatabase, col : str) -> dict:
    """
    Count the occurences of each label name in a given edge collections
    
    """
    cursor = db.aql.execute(
        "FOR doc IN @@name\
         RETURN doc.`label`",
         bind_vars={'@name': col})
    counting_dictionary : dict = {}
    for label in cursor:
        if label in counting_dictionary:
            counting_dictionary[label] += 1
        else:
            counting_dictionary[label] = 1
    return counting_dictionary

if __name__ == "__main__":
    client : ArangoClient = ArangoClient("http://localhost:8529")

    currentdb : database.StandardDatabase = client.db("TEATIME", "Marwan", password="Dragon74")
    colnames : list = get_all_edge_col_names(currentdb)
    
    results : dict = {}
    for name in colnames :
        countedLabels : dict = count_labels(currentdb, name)
        results[name] = countedLabels

    with open("results.csv", 'w') as f:
        for name in results:
            for res in results[name]:
                f.write(name + ',' + res + ',' + str(results[name][res]) + '\r')