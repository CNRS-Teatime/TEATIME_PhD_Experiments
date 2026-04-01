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
    linkage_matrix = create_linkage_matrix(model)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)

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


if __name__ == "__main__":
    ids, matrix = fetch_distance_matrix("distance_matrix_th15_graph.csv")

    clustering = AgglomerativeClustering(metric="precomputed", linkage="average", distance_threshold=0, n_clusters=None)

    clustering = clustering.fit(matrix)

    linkage_matrix = create_linkage_matrix(clustering)

    nb_clusters = 8

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    clusters = fcluster(linkage_matrix, nb_clusters, criterion='maxclust')

    cluster_with_ids = [[] for _ in range(nb_clusters)]

    for i in range(len(ids)):
        cluster_with_ids[clusters[i] - 1].append(ids[i])
        cluster_with_ids[clusters[i] - 1].append(ids[i])

    print(len(cluster_with_ids[1]))

    client = ArangoClient(hosts="http://localhost:8529")
    db: database.StandardDatabase = client.db("TEATIME", username="root", password="test")
    thesaurus_documents: database.StandardCollection = db.collection("th15")

    for cluster in cluster_with_ids:
        test = thesaurus_documents.get_many(cluster)
        test = [doc['name'] for doc in test]

        print(len(test))
        print(test)

"""
plt.title("Hierarchical Clustering Dendrogram")
# plot the top three levels of the dendrogram
plot_dendrogram(clustering, truncate_mode="level", p=4)
plt.xlabel("Number of points in node (or index of point if no parenthesis).")
plt.show()"""
