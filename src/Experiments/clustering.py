from ClusteringConcepts import *
from distanceMatrixWithNetworkX import *
import csv


def write_clusters_to_csv(cluster_list, path):
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"')
        writer.writerow(['element', 'clusterNB'])
        for i in range(len(cluster_list)):
            for element in cluster_list[i]:
                writer.writerow([element, i])

if __name__ == "__main__":
    DOCUMENT_COLLECTION = "th15"
    EDGE_COLLECTION = "th15_relations"
    GRAPH_NAME = "th15_graph"
    MATRIX_PATH = "distance_matrix_IntraTheso.csv"

    """doc_id_list, G = fetch_from_arango(DOCUMENT_COLLECTION, EDGE_COLLECTION)

    matrix = compute_matrix(G, doc_id_list)

    write_matrix_to_file(f"distance_matrix_{GRAPH_NAME}.csv", doc_id_list)"""

    NB_CLUSTERS = 64

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    ids, clusters = compute_clusters(MATRIX_PATH, NB_CLUSTERS)

    cluster_with_ids = [[] for _ in range(NB_CLUSTERS)]

    for i in range(len(ids)):
        cluster_with_ids[clusters[i] - 1].append(ids[i])

    # fetched_cluster = populate_clusters(NB_CLUSTERS, clusters, ids, "TEATIME", "root", "test")

    write_clusters_to_csv(cluster_with_ids, "IntraThesoCluster.csv")