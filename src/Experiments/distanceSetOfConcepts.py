"""
We will import a pre-computed distance matrix, and calculate the distance between a two (not necessarily disjoints) sets
of concepts. This will be usefull for calculating the distance between documents represented by sets of concepts
"""
import random
from random import sample

with open("../../data/Clustering/clean_distance_matrix_th15_graph.csv", 'r') as f:
    ids = f.readline()
    ids = ids.split(',')
    size = len(ids)

    matrix : list = []

    for i in range(size):
        line = [int(d) for d in f.readline().split(',')]
        matrix.append(line)

avg_all_dist = 0

nb_iter = 100000
nb_concepts_by_set_min = 10
nb_concepts_by_set_max = 100


for i in range(nb_iter):
    # We could use random.sample if we want unique
    set1 = sample(range(0, size), random.randint(nb_concepts_by_set_min, nb_concepts_by_set_max))
    set2 = sample(range(0, size), random.randint(nb_concepts_by_set_min, nb_concepts_by_set_max))

    distance = 0
    for id1 in set1:
        for id2 in set2:
            distance += matrix[id1][id2]

    distance = distance/(len(set1) * len(set2))

    avg_all_dist += distance

avg_all_dist /= nb_iter

print(avg_all_dist)

# Expected value with 10 : 12.3