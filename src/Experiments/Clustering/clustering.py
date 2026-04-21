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
    GRAPH_NAME = "IntraTheso"

    MATRIX_PATH = f"distance_matrix_{GRAPH_NAME}.csv"
    DATABASE = "TEATIME-Exp"
    DOCUMENT_COLLECTIONS = ["th12",
                            "th13",
                            "th15",
                            "th16",
                            "th18",
                            "th21",
                            "th52",
                            "th53",
                            "th56",
                            "th57",
                            "th58",
                            "th59"]
    EDGE_COLLECTIONS = ["intraTheso_relations",
                        "th12_relations",
                        "th13_relations",
                        "th15_relations",
                        "th16_relations",
                        "th18_relations",
                        "th21_relations",
                        "th52_relations",
                        "th53_relations",
                        "th56_relations",
                        "th57_relations",
                        "th58_relations",
                        "th59_relations"
                        ]
    G = fetch_from_arango( EDGE_COLLECTIONS, DATABASE)

    matrix = compute_matrix(G)

    write_matrix_to_file(MATRIX_PATH, list(G.nodes._nodes.keys()), matrix)

    NB_CLUSTERS = 128

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    ids, clusters = compute_clusters(MATRIX_PATH, NB_CLUSTERS)

    cluster_with_ids = [[] for _ in range(NB_CLUSTERS)]

    for i in range(len(ids)):
        cluster_with_ids[clusters[i] - 1].append(ids[i])

    # fetched_cluster = populate_clusters(NB_CLUSTERS, clusters, ids, "TEATIME", "root", "test")

    write_clusters_to_csv(cluster_with_ids, "/Users/marwan/Code/TEATIME_PhD_Experiments/data/Clustering/IntraThesoCluster.csv")