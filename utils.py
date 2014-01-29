import json
import os


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def load_country(country_name):
    """ Loads the JSON definition of my inventory for a given country. """
    path = os.path.join(DATA_DIR, "%s.json" % country_name)
    try:
        with open(path, 'r') as json_file:
            return json.loads(json_file.read())
    except IOError:
        return []


def save_country(country):
    """ Saves a new JSON definition of my inventory for a given country. """
    path = os.path.join(DATA_DIR, "%s.json" % country['country_name'])
    with open(path, 'w+') as json_file:
        json_file.write(json.dumps(country, indent=4))


def canadian_coin():
    return {
        "type": "coin",
        "owner": "Joel Friedly",
        "denomination": "cents",
        "obsolete": False
    }


def insert_canadian_coin(value):
    while True:
        coin = canadian_coin()
        coin['value'] = int(value)
        coin['year'] = int(raw_input("Year?  "))
        canada = load_country('canada')
        canada['inventory'].append(coin)
        save_country(canada)
