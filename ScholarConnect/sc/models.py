from django.db import models
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def author_to_compare(author_id):
    r = requests.get(f"https://api.openalex.org/authors/{author_id}")
    return r.json()


def build_dataframe(author):
    records = [author]
    concept_ids = [concept["id"] for concept in author["x_concepts"][:5]]
    country_code = (
        author["last_known_institution"]["country_code"]
        if author["last_known_institution"]
        else None
    )
    institution_type = (
        author["last_known_institution"]["type"]
        if author["last_known_institution"]
        else None
    )

    # build filter
    filter_string = "filter="
    for concept_id in concept_ids:
        filter_string += f"concepts.id:{concept_id},"
    if country_code:
        filter_string += f"last_known_institution.country_code:{country_code},"
    if institution_type:
        filter_string += f"last_known_institution.type:{institution_type},"
    filter_string = filter_string[:-1]

    for page in range(1, 25):
        print(f"Fetching results page {page} of 25")
        url = (
            f"https://api.openalex.org/authors?{filter_string}&per-page=200&page={page}"
        )
        r = requests.get(url)
        results = r.json()["results"]
        total_results = r.json()["meta"]["count"]
        for result in results:
            records.append(result)
    print(f"Total results is {total_results}")

    return pd.DataFrame.from_records(records)


def build_concept_list(df):
    x_concept_0 = []
    x_concept_1 = []
    for index, row in df.iterrows():
        concepts = row["x_concepts"]
        for concept in concepts:
            concept_name = concept["display_name"]
            concept_level = concept["level"]
            if concept_level == 0 and concept_name not in x_concept_0:
                x_concept_0.append(concept_name)
            if concept_level == 1 and concept_name not in x_concept_1:
                x_concept_1.append(concept_name)

    x_concept = x_concept_0 + x_concept_1
    x_concept_dist = []

    for index, row in df.iterrows():
        concepts = row["x_concepts"]
        x_concept_dist_0 = np.zeros(len(x_concept))

        for concept in concepts:
            concept_name = concept["display_name"]
            if concept_name in x_concept:
                concept_index = x_concept.index(concept_name)
                concept_score = concept["score"]
                x_concept_dist_0[concept_index] = concept_score

        if index == 0:
            x_concept_dist = x_concept_dist_0
        else:
            x_concept_dist = np.vstack((x_concept_dist, x_concept_dist_0))
    return x_concept_dist


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
    closest_indices = np.argsort(-similarities)[0][1 : num_closest + 1]

    # Get the corresponding distances (similarities)
    distances = similarities[0][closest_indices]

    # Retrieve the closest rows from the matrix
    closest_rows = matrix[closest_indices]

    return closest_rows, distances, closest_indices


def get_closest_author(author_id):
    author = author_to_compare(author_id)
    df = build_dataframe(author)
    x_concept_dist = build_concept_list(df)

    # person compared
    person_row = x_concept_dist[0]

    # result
    closest_rows, distances, closest_indices = find_closest_rows(
        x_concept_dist, person_row, num_closest=10
    )
    print("Closest Rows:")
    print(closest_rows)
    print("Distances:")
    print(distances)
    print("Indices:")
    print(closest_indices)
    print(df.iloc[closest_indices]["id"])

    closest_author_id = df.iloc[closest_indices[1]]["id"]
    r = requests.get(f"https://api.openalex.org/authors/{closest_author_id}")
    closest_author = r.json()
    return closest_author


if __name__ == "__main__":
    print(get_closest_author("A2794320938"))