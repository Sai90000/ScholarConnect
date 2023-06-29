import pandas as pd
import requests


def get_authors(author_id):
    url = f"https://api.openalex.org/authors/{author_id}"
    r = requests.get(url)
    first_author = r.json()
    first_concept = first_author["x_concepts"][0].get('id')
    second_concept = first_author["x_concepts"][1].get('id')
    third_concept = first_author["x_concepts"][2].get('id')
    first_three_concepts = [concept['id'] for concept in first_author["x_concepts"][:3]]
    last_known_institution = first_author["last_known_institution"]
    print(last_known_institution['country_code'])

    # filter by the same country and institution type
    for page in range(1, 25):
        url = f"https://api.openalex.org/authors?filter=concepts.id:{first_concept},concepts.id:{second_concept},concepts.id:{third_concept},last_known_institution.country_code:{last_known_institution['country_code']},last_known_institution.type:{last_known_institution['type']}&per-page=200&page={page}"
        r = requests.get(url)
        results = r.json()["results"]
        for result in results:
            # check if first three concepts match the first three concepts for the original author
            if [concept['id'] for concept in result["x_concepts"][:3]] == first_three_concepts:
                print(f"found a match: {result['id']}")


if __name__ == "__main__":
    get_authors("A4356737211")
