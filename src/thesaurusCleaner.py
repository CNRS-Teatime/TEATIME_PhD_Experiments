"""
Cleanup procedure for our thesaurus collections
It will check for invalid relations and properties, to reduce friction in the use of the data
"""

from arango import database, exceptions, ArangoClient

def cleanup_document_collection(db : database.StandardDatabase, collection_name : str):
    """
    TODO : Docstring
    Cleans all the duplicates in a collection with the given collection name
    """

    if not db.has_collection(collection_name):
        print(f"Collection {collection_name} does not exist")
    else:
        if not db.collection(collection_name).properties()['edge'] :
            db.aql.execute("\
                FOR doc IN @@collection \
                    COLLECT myid = doc.ark INTO keys = doc._key \
                    LET allButFirst = SLICE(keys, 1) // or SHIFT(keys) \
                    FOR k IN allButFirst \
                        REMOVE k IN @@collection",
                bind_vars={"@collection" : collection_name})
        else:
            print(f"{collection_name} is an edge collection, cannot perform this type of cleanup")


def cleanup_edge_collection(db : database.StandardDatabase, collection_name : str):
    """
    TODO : Docstring
    """
    if not db.has_collection(collection_name):
        print(f"Collection {collection_name} does not exist")
    else:
        if db.collection(collection_name).properties()['edge'] :
            """db.aql.execute("\
                        FOR doc IN @@collection \
                            FILTER CONTAINS(doc._to, 'undefined') OR CONTAINS(doc._from, 'undefined')\
                        REMOVE doc IN @@collection",
                        bind_vars={"@collection": collection_name})"""

            #Now we want to test every document in the edges to see if they exist
            #It feels very trashy tho
            for edge in db.collection(collection_name).all() :
                try :
                    _to = db.document(edge['_to'])
                    _from = db.document(edge['_from'])
                    if _to is None or _from is None:
                        print(edge)
                        db.collection(collection_name).delete(edge)

                except (exceptions.DocumentGetError, exceptions.DocumentRevisionError) as e:
                    print(edge)
                    db.collection(collection_name).delete(edge)
        else:
            print(f"{collection_name} is not an edge collection, cannot perform this type of cleanup")


    return

if __name__ == "__main__":
    client = ArangoClient("http://localhost:8529")

    database = client.db("TEATIME","root","test")

    cleanup_edge_collection(database, "th15_relations")