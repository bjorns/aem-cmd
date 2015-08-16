# coding: utf-8
import requests


def get_json(server, path):
    url = server.url(path)
    r = requests.get(url, auth=(server.username, server.password))
    if r.status_code != 200:
        raise Exception("Failed to get " + url)
    return r.json()

def post_form(server, path, form_data):
    url = server.url(path)
    r = requests.post(url, auth=(server.username, server.password), data=form_data)
    if r.status_code != 200:
        raise Exception("Failed to post " + url)
    return r.json()
