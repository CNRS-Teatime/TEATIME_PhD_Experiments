"""
Hierarchical clustering on concepts using a precomputed distance matrix
"""
import numpy as np
from arango import ArangoClient, database
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

def create_linkage_matrix(model) -> np.ndarray:
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    return linkage_matrix

def plot_dendrogram(model, **kwargs):
    plt.title("Hierarchical Clustering Dendrogram")
    # plot the top three levels of the dendrogram

    linkage_matrix = create_linkage_matrix(model)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)
    plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    plt.show()

def fetch_distance_matrix(file_path : str) -> tuple[list ,np.ndarray]:
    # Rebuilding the matrix from a csv
    with open(file_path, 'r') as f:
        ids = f.readline()
        ids = ids.split(',')
        size = len(ids)

        matrix : list = []

        for i in range(size):
            line = [int(d) for d in f.readline().split(',')]
            matrix.append(line[:size])


        return ids, np.asarray(matrix)


def compute_clusters(matrix_csv : str, nb_clusters: int):
    ids, matrix = fetch_distance_matrix(matrix_csv)

    clustering = AgglomerativeClustering(metric="precomputed", linkage="average", distance_threshold=0, n_clusters=None)

    clustering = clustering.fit(matrix)

    linkage_matrix = create_linkage_matrix(clustering)

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    return ids, fcluster(linkage_matrix, nb_clusters, criterion='maxclust')

def populate_clusters(nb_clusters, clusters, ids, db_name, db_user, db_password):
    """
    Populate clusters by fetching content from arangoDB
    """
    cluster_with_ids = [[] for _ in range(nb_clusters)]

    for i in range(len(ids)):
        cluster_with_ids[clusters[i] - 1].append(ids[i])

    client = ArangoClient(hosts="http://localhost:8529")
    db: database.StandardDatabase = client.db(db_name, username=db_user, password=db_password)
    thesaurus_documents: database.StandardCollection = db.collection("th15")

    for i in range(nb_clusters):
        cluster_with_ids[i] = thesaurus_documents.get_many(cluster_with_ids[i])
        cluster_with_ids[i] = [doc['name'] for doc in cluster_with_ids[i]]

    return cluster_with_ids

def add_cluster_back_to_db(nb_clusters, collection_name, clusters, ids, db_name, db_user, db_password):
    """
    Populate clusters by fetching content from arangoDB
    """
    cluster_with_ids = [[] for _ in range(nb_clusters)]

    for i in range(len(ids)):
        cluster_with_ids[clusters[i] - 1].append({'_id' : ids[i], 'cluster' : int(clusters[i])})

    client = ArangoClient(hosts="http://localhost:8529")
    db: database.StandardDatabase = client.db(db_name, username=db_user, password=db_password)
    thesaurus_documents: database.StandardCollection = db.collection(collection_name)

    for i in range(nb_clusters):
        thesaurus_documents.update_many(cluster_with_ids[i])


if __name__ == "__main__":

    NB_CLUSTERS = 64

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    ids, clusters = compute_clusters("clean_distance_matrix_th15_graph.csv", NB_CLUSTERS)

    add_cluster_back_to_db(NB_CLUSTERS, "th15", clusters, ids, "TEATIME", "root", "test")

    """fetched_cluster = populate_clusters(NB_CLUSTERS, clusters, ids, "TEATIME", "root", "test")
    for c in fetched_cluster:
        print(c)"""
