"""
Cleanup procedure for our thesaurus collections
It will check for invalid relations and properties, to reduce friction in the use of the data
"""

from arango import database, exceptions, ArangoClient

def cleanup_edge_collection(db : database.StandardDatabase, collection_name : str):
    """
    TODO : Docstring
    """
    to_delete = []

    if not db.has_collection(collection_name):
        print(f"Collection {collection_name} does not exist")
    else:
        if db.collection(collection_name).properties()['edge'] :
            print("Fetching...")
            #Now we want to test every document in the edges to see if they exist
            #It feels very trashy tho
            all = db.collection(collection_name).all()
            print("Now checking...")
            for edge in all :
                try :
                    _to = db.document(edge['_to'])
                    _from = db.document(edge['_from'])
                    if _to is None or _from is None:
                        to_delete.append(edge)

                except (exceptions.DocumentGetError, exceptions.DocumentRevisionError) as e:
                    to_delete.append(edge)
        else:
            print(f"{collection_name} is not an edge collection, cannot perform this type of cleanup")

        print("Deleting now...")

        db.collection(collection_name).delete_many(to_delete)


    return

def cleanup_database(host: str, db_name: str, user: str, password: str):
    client: ArangoClient = ArangoClient(hosts=host)
    db: database.StandardDatabase = client.db(db_name, username=user,
                                              password=password)

    collections = db.collections()

    for coll in collections:
        if not coll['system']:
            if db.collection(coll['name']).properties()['edge']:
                cleanup_edge_collection(db, coll['name'])

if __name__ == "__main__":
    testclient = ArangoClient("http://localhost:8529")

    testdatabase = testclient.db("TEATIME","root","test")

    cleanup_edge_collection(testdatabase, "intraTheso_relations")