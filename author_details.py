import requests


def get_author_details(author_id):
    r = requests.get("https://api.openalex.org/authors/" + author_id)
    return r.json()