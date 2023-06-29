import openalexnet as oanet
import pandas as pd
from tqdm.auto import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

openalex = oanet.OpenAlexAPI()

filterData = {
        "concepts.id": "C2779161974",
        #"concepts.id": "C118552586",
        "last_known_institution.country_code": "jp"
    }


entityType = "authors"
entities = openalex.getEntities(entityType, filter=filterData)
entitiesList = []
for entity in tqdm(entities, desc="Retrieving entries"):
    entitiesList.append(entity)

df = pd.DataFrame.from_records(entitiesList)

# Assemble list of concepts
x_concept_0 = []
x_concept_1 = []
for index, row in df.iterrows():
  concepts = row['x_concepts']
  for concept in concepts:
    concept_name = concept['display_name']
    concept_level = concept['level']
    if concept_level == 0 and concept_name not in x_concept_0:
        x_concept_0.append(concept_name)
    if concept_level == 1 and concept_name not in x_concept_1:
        x_concept_1.append(concept_name)


x_concept = x_concept_0 + x_concept_1
print(x_concept)
x_concept_dist = []

for index, row in df.iterrows():
    print(index)
    concepts = row['x_concepts']
    x_concept_dist_0 = np.zeros(len(x_concept))

    for concept in concepts:
        concept_name = concept['display_name']
        if concept_name in x_concept:
            concept_index = x_concept.index(concept_name)
            concept_score = concept['score']
            x_concept_dist_0[concept_index] = concept_score

    if index == 0:
        x_concept_dist = x_concept_dist_0
    else:
        x_concept_dist = np.vstack((x_concept_dist, x_concept_dist_0))


def find_closest_rows(matrix, person_row, num_closest=10):
    """
    Finds the closest rows in a matrix to an arbitrary person (row) based on cosine similarity.


    Args:
        matrix (np.ndarray): Matrix of people (rows).
        person_row (np.ndarray): Arbitrary person (row).
        num_closest (int): Number of closest rows to retrieve (default: 10).


    Returns:
        closest_rows (np.ndarray): Closest rows to the person (excluding the original row).
        distances (np.ndarray): Similarity distances (cosine similarity) corresponding to the closest rows.
    """

    # Compute cosine similarity between the person and all other rows
    similarities = cosine_similarity([person_row], matrix)

    # Get the indices of the closest rows (excluding the original row)
    closest_indices = np.argsort(-similarities)[0][1:num_closest + 1]

    # Get the corresponding distances (similarities)
    distances = similarities[0][closest_indices]

    # Retrieve the closest rows from the matrix
    closest_rows = matrix[closest_indices]

    return closest_rows, distances, closest_indices


person_row = x_concept_dist[0]  # Example: using the first row
print(df.iloc[0]['id'])

closest_rows, distances, closest_indices = find_closest_rows(x_concept_dist, person_row, num_closest=10)

print("Closest Rows:")
print(closest_rows)
print("Distances:")
print(distances)
print("Indices:")
print(closest_indices)

print(df.iloc[closest_indices]['id'])