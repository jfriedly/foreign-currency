""" Shared utility functions

Note:  Some of the functions in here aren't used in any of the scripts.
That's because they're meant to be used from an interactive Python shell.
"""
import json
import os
import sys


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def load_country(country_name):
    """ Loads the JSON definition of my inventory for a given country. """
    path = os.path.join(DATA_DIR, "%s.json" % country_name)
    try:
        with open(path, 'r') as json_file:
            return json.loads(json_file.read())
    except IOError as e:
        if e.errno == 2:
            print "Could not find country data for %s in %s" % (country_name,
                                                                DATA_DIR)
            sys.exit(1)
        raise


def save_country(country):
    """ Saves a new JSON definition of my inventory for a given country. """
    path = os.path.join(DATA_DIR, "%s.json" % country['name'])
    with open(path, 'w+') as json_file:
        json_file.write(json.dumps(country, indent=4))


def create_country():
    """ Creates an empty country dictionary """
    return {
        "name": "",
        "name_long": "",
        "divisions": dict(),
        "inventory": [],
        "denominations": []
    }


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
