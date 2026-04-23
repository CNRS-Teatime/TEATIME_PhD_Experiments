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
    """
    Fetch the distance matrix created by distanceMatrix.py
    :param file_path: the path to the distance matrix csv file
    :returns: The list of matrix, and a numpy 2D array representing the matrix as a tupple
    """
    with open(file_path, 'r') as f:
        ids = f.readline()
        ids = ids.split(',')
        size = len(ids)

        matrix : list = []

        for i in range(size):
            line = [int(d) for d in f.readline().split(',')]
            matrix.append(line[:size])


        return ids, np.asarray(matrix)


def compute_clusters(matrix_csv : str, nb_clusters: int) -> tuple[list[str], np.ndarray]:
    """
    Based on a distance matrix csv file and a target number of cluster, computes
    the clusters. If the target number of clusters is higher than the number of objects, returns each object as its own
    cluster.

    :param matrix_csv: The path to the csv file containing a distance matrix
    :type matrix_csv: str
    :param nb_clusters: The target number of clusters # TODO : Allow choosing multiple target numbers (multi-granularity)
    :type nb_clusters: int

    :returns: The list of ids, and a numpy 1D array of the same size containing the cluster number. Where ids[i] and cluster[i] are the id and cluster number of an object
    """
    ids, matrix = fetch_distance_matrix(matrix_csv)

    clustering = AgglomerativeClustering(metric="precomputed", linkage="average", distance_threshold=0, n_clusters=None)

    clustering = clustering.fit(matrix)

    linkage_matrix = create_linkage_matrix(clustering)

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    return ids, fcluster(linkage_matrix, nb_clusters, criterion='maxclust')

def add_cluster_back_to_db(collection_name: str, clusters: np.ndarray, ids: list[str], db_name: str, db_user: str, db_password: str) -> None:
    """
    Push back cluster numbers to arangoDB. The credentials are usually defined in a .env, fetched by the main function.
    TODO : Use a graph name, which could be inside the matrix csv, to know which collections are targeted instead of a single collection name
    :param collection_name: The name of the arangoDB collection in which to push the changes
    :type collection_name: str
    :param clusters: a 1D numpy array containing cluster numbers Where ids[i] and cluster[i] are the id and cluster number of an object
    :type clusters: np.ndarray
    :param ids: A list of ids, associated with the clusters array
    :type ids: list[str]
    :param db_name: name of the associated database
    :type db_name: str
    :param db_user: usename to use for credentials
    :type db_user: str
    :param db_password: password associated with the username
    :type db_password: str
    """
    nb_clusters: int = clusters.max()
    cluster_with_ids = [[] for _ in range(nb_clusters)]

    for i in range(len(ids)):
        cluster_with_ids[clusters[i] - 1].append({'_id' : ids[i], 'cluster' : int(clusters[i])})

    client = ArangoClient(hosts="http://localhost:8529")
    db: database.StandardDatabase = client.db(db_name, username=db_user, password=db_password)
    thesaurus_documents: database.StandardCollection = db.collection(collection_name)

    for i in range(nb_clusters):
        thesaurus_documents.update_many(cluster_with_ids[i])


if __name__ == "__main__":

    NB_CLUSTERS = 16

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    ids, clusters = compute_clusters("/Users/marwan/Code/TEATIME_PhD_Experiments/data/Clustering/clean_distance_matrix_th15_graph.csv", NB_CLUSTERS)

    # add_cluster_back_to_db( "th15", clusters, ids, "TEATIME", "root", "test")