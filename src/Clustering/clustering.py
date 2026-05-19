import os

from ClusteringConcepts import *
from DistanceMatrix import *
from TermAssociation import *
import csv, logging, time
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
    load_dotenv(".env")
    GRAPH_NAME = os.getenv("CONCEPTS_GRAPH")

    MATRIX_PATH = f"distance_matrix_{GRAPH_NAME}.csv"
    DATABASE = os.getenv("DB_NAME")
    HOST = os.getenv("DB_ADDRESS")
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASSWORD")
    NB_CLUSTERS = [int(os.getenv("NB_CLUSTERS"))]

    logging.log(logging.INFO, f"Starting clustering on graph {GRAPH_NAME}, in database {DATABASE}, with {NB_CLUSTERS} cluster")

    """G = fetch_from_arango(GRAPH_NAME, DATABASE)

    if G is None:
        logging.log(logging.ERROR,f"Graph '{GRAPH_NAME}' is not in the database {DATABASE}")
        exit()

    matrix = compute_concept_matrix(G)

    write_matrix_to_file(MATRIX_PATH, list(G.nodes._nodes.keys()), matrix)

    # These create a list, where clusters_X[i] returns the cluster number of item i in the original ids list
    id_to_cluster_mapping= compute_clusters(MATRIX_PATH, NB_CLUSTERS)

        # fetched_cluster = populate_clusters(NB_CLUSTERS, clusters, ids, "TEATIME", "root", "test")

    if os.getenv("RESULT_FORMAT") == "DB":
        add_cluster_back_to_db(id_to_cluster_mapping, HOST, DATABASE, USER, PASSWORD)

    # write_clusters_to_csv(cluster_with_ids, f"/Users/marwan/Code/TEATIME_PhD_Experiments/data/Clustering/{GRAPH_NAME}_clusters.csv")"""

    client: ArangoClient = ArangoClient(hosts=os.getenv("DB_ADDRESS"))
    db: database.StandardDatabase = client.db(os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD"))

    print("Starting concept matrix fetching...")
    start = time.time()
    ids, matrix = fetch_distance_matrix("distance_matrix_InterTheso_graph.csv")
    print(f"Concept matrix fetched, took {time.time() - start}seconds")
    print("Starting object concept mapping...")
    start = time.time()
    object_maping = create_object_concept_map(db, os.getenv("NODE_COLLECTION"), os.getenv("ASSOCIATION_GRAPH"), ids)
    print(f"Finished, took {time.time() - start}seconds")
    print("Starting object distance matrix...")
    start = time.time()
    object_matrix = compute_object_matrix(matrix, ids, object_maping)
    print(f"Finished, took {time.time() - start}seconds")
    write_matrix_to_file("aioli_distance_matrix.csv", list(object_maping.keys()), object_matrix)