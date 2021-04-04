import requests


def get_repo_tags(api):
    for _ in requests.get(api).json():
        yield _['name']
