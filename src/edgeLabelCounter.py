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
    return [name for name in cursor]


def count_labels(db: database.StandardDatabase, col : str) -> dict:
    """
    Count the occurences of each label name in a given edge collections
    
    """
    cursor = db.aql.execute(
        "FOR doc IN @@name\
         RETURN doc.`label`",
         bind_vars={'@name': col})
    coutingDictionary : dict = {}
    for label in cursor:
        if label in coutingDictionary:
            coutingDictionary[label] += 1
        else:
            coutingDictionary[label] = 1
    return coutingDictionary

if __name__ == "__main__":
    client : ArangoClient = ArangoClient("http://localhost:8529")

    db : database.StandardDatabase = client.db("TEATIME", "Marwan", password="Dragon74")
    colnames : list = get_all_edge_col_names(db)
    
    results : dict = {}
    for name in colnames :
        countedLabels : dict = count_labels(db, name)
        results[name] = countedLabels
    
    print(results)

    with open("results.csv", 'w') as f:
        for name in results:
            for res in results[name]:
                f.write(name + ',' + res + ',' + str(results[name][res]) + '\r')