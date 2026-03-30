"""
Hierarchical clustering on concepts using a precomputed distance matrix
"""
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

def plot_dendrogram(model, **kwargs):
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

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


# Rebuilding the matrix from a csv
with open("distance_matrix_th15_graph.csv", 'r') as f:
    ids = f.readline()
    ids = ids.split(',')
    size = len(ids)

    matrix : list = []

    for i in range(size):
        line = [int(d) for d in f.readline().split(',')]
        matrix.append(line[:size])


"""linkage_matrix = linkage(matrix, method='average')

# Extract clusters at different levels by specifying the number of clusters
clusters_2 = fcluster(linkage_matrix, 2, criterion='maxclust')
clusters_8 = fcluster(linkage_matrix, 8, criterion='maxclust')

# Count points in each cluster for both clusterings
cluster_counts_2 = np.unique(clusters_2, return_counts=True)
cluster_counts_4 = np.unique(clusters_8, return_counts=True)

print(cluster_counts_2)
print(cluster_counts_4)
"""

clustering = AgglomerativeClustering(metric="precomputed", linkage="average", distance_threshold=0, n_clusters=None)

clustering = clustering.fit(matrix)

plt.title("Hierarchical Clustering Dendrogram")
# plot the top three levels of the dendrogram
plot_dendrogram(clustering, truncate_mode="level", p=4)
plt.xlabel("Number of points in node (or index of point if no parenthesis).")
plt.show()
