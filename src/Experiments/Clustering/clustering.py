from ClusteringConcepts import *
from distanceMatrix import *
import csv


def write_clusters_to_csv(gran_cluster_list: list[list[str]], path: str):
    """
    Writes all the clusterised objects, allong with their cluster ids, in a CSV file.
    The format for each row is:
    object_as_string, cluster_number

    :param cluster_list: A 2D list of clusters, cluster_list[1] is the list of all ids in cluster 2
    :type cluster_list: list[list[str]]
    :param path: The path to the desired csv file
    :type path: str
    """
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"')
        writer.writerow(['element', 'clusterNB'])
        for i in range(len(cluster_list)):
            for element in cluster_list[i]:
                writer.writerow([element, i])

if __name__ == "__main__":
    GRAPH_NAME = "th15_graph"

    MATRIX_PATH = f"distance_matrix_{GRAPH_NAME}.csv"
    DATABASE = "TEATIME-Exp"
    HOST = "http://localhost:8529"
    USER = "root"
    PASSWORD = "test"
    '''G = fetch_from_arango(GRAPH_NAME, DATABASE)

    if G is None:
        print(f"Graph '{GRAPH_NAME}' is not in the database {DATABASE}")
        exit()

    matrix = compute_matrix(G)

    write_matrix_to_file(MATRIX_PATH, list(G.nodes._nodes.keys()), matrix)'''

    NB_CLUSTERS = [16, 32]

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    ids, clusters = compute_clusters(MATRIX_PATH, NB_CLUSTERS)

    id_to_cluster_mapping : dict = {}

    for i in range(len(clusters)):
        for j in range(len(ids)):
            if not ids[j] in id_to_cluster_mapping:
                id_to_cluster_mapping[ids[j]] = []
            id_to_cluster_mapping[ids[j]].append(int(clusters[i][j]))

        # fetched_cluster = populate_clusters(NB_CLUSTERS, clusters, ids, "TEATIME", "root", "test")

    add_cluster_back_to_db(id_to_cluster_mapping, HOST, DATABASE, USER, PASSWORD)
    # write_clusters_to_csv(cluster_with_ids, f"/Users/marwan/Code/TEATIME_PhD_Experiments/data/Clustering/{GRAPH_NAME}_clusters.csv")