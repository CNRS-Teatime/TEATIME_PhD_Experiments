import os

from ClusteringConcepts import *
from distanceMatrix import *
import csv, logging
from dotenv import load_dotenv


def write_clusters_to_csv(gran_cluster_list: list[list[str]], path: str):
    """
    Writes all the clusterised objects, allong with their cluster ids, in a CSV file.
    The format for each row is:
    object_as_string, cluster_number

    :param gran_cluster_list: A 2D list of clusters, cluster_list[1] is the list of all ids in cluster 2
    :type gran_cluster_list: list[list[str]]
    :param path: The path to the desired csv file
    :type path: str
    """
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"')
        writer.writerow(['element', 'clusterNB'])
        for i in range(len(gran_cluster_list)):
            for element in gran_cluster_list[i]:
                writer.writerow([element, i])

if __name__ == "__main__":
    logging.basicConfig(
        filename="clustering.log",
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.INFO
    )
    GRAPH_NAME = os.getenv("GRAPHNAME")

    MATRIX_PATH = f"distance_matrix_{GRAPH_NAME}.csv"
    DATABASE =os.getenv("DB_NAME")
    HOST = os.getenv("DB_ADDRESS")
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASSWORD")
    NB_CLUSTERS = [int(os.getenv("NB_CLUSTERS"))]

    logging.log(logging.INFO, f"Starting clustering on graph {GRAPH_NAME}, in database {DATABASE}, with {NB_CLUSTERS} cluster")

    G = fetch_from_arango(GRAPH_NAME, DATABASE)

    if G is None:
        logging.log(logging.ERROR,f"Graph '{GRAPH_NAME}' is not in the database {DATABASE}")
        exit()

    matrix = compute_matrix(G)

    write_matrix_to_file(MATRIX_PATH, list(G.nodes._nodes.keys()), matrix)

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    id_to_cluster_mapping= compute_clusters(MATRIX_PATH, NB_CLUSTERS)

        # fetched_cluster = populate_clusters(NB_CLUSTERS, clusters, ids, "TEATIME", "root", "test")

    add_cluster_back_to_db(id_to_cluster_mapping, HOST, DATABASE, USER, PASSWORD)
    # write_clusters_to_csv(cluster_with_ids, f"/Users/marwan/Code/TEATIME_PhD_Experiments/data/Clustering/{GRAPH_NAME}_clusters.csv")