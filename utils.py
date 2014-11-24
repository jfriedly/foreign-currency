""" Shared utility functions

Note:  Some of the functions in here aren't used in any of the scripts.
That's because they're meant to be used from an interactive Python shell.
"""
import models


def canadian_coin():
    return {
        "piece_type": "coin",
        "owner": "Joel Friedly",
        "denomination": "CAD",
        "obsolete": False
    }


def insert_canadian_coin(value):
    while True:
        coin_dict = canadian_coin()
        coin_dict['value'] = int(value)
        coin_dict['year'] = int(raw_input("Year?  "))
        coin = models.CurrencyPiece.from_dict(coin_dict)
        canada = models.Country.load('canada')
        canada.inventory.append(coin)
        canada.save()
