import threading
from arango import database


def create_object_concept_map(db : database.StandardDatabase, collection_name : str, graph_name : str) -> dict[str, list[str]]:
    """
    For a given collection name and semantic graph search the graph for object - concept associations
    :param db: An arango database API wrapper
    :type db: arango.database.StandardDatabase
    :param collection_name: The name of the object collection for which you want to fin associations
    :type collection_name: str
    :param graph_name: The name of the graph containing information about associations
    :type graph_name: str
    :returns: A dict with document ids from `collection_name` as keys and the list of associated concept ids as value
    """

    collection = db.collection(collection_name)

    documents = collection.all()

    mapping : dict[str, list[str]] = {}

    def query(doc_id: str, datab):
        result = datab.aql.execute("\
                                FOR v IN 1..1 INBOUND @document\
                                    GRAPH @graphname\
                                    OPTIONS {order: 'bfs'}\
                                    SORT v._id\
                                    RETURN v._id",
                                   bind_vars={'graphname': graph_name, 'document': doc_id})

        mapping[doc_id] = []

        for identifier in result:
            mapping[doc_id].append(identifier)

    threads = []

    for doc in documents:
        t = threading.Thread(target=query, args=(doc['_id'], db))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    return mapping