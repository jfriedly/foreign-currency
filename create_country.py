#!/usr/bin/env python
import utils


def create_subdivision(big_unit, small_unit, value):
    """ Create a subdivision dict for totalling

    For more info on subdivision dicts, see the module docs for ``total``,
    but the tl;dr is there are <value> <small_units> in a <big_unit>.
    Ex:  There are <100> <cents> in a <dollar>.
    """
    division = {
        big_unit: {
            "denomination": small_unit,
            "value": value
        }
    }
    return division


def main():
    name = raw_input("Country name (short):  ")
    name_long = name.replace('-', ' ').title()
    name_long_prompt = "Country name (long) [%s]:  " % name_long
    name_long = raw_input(name_long_prompt) or name_long

    denominations = raw_input("Denominations (biggest first):  ").split()
    smallest_unit = denominations[-1]
    divisions = create_subdivision(smallest_unit, smallest_unit, 1)
    denominations.reverse()
    for i, unit in enumerate(denominations[:-1]):
        bigger_unit = denominations[i+1]
        value = int(raw_input("How many %s in %s?  " % (unit, bigger_unit)))
        divisions.update(create_subdivision(bigger_unit, unit, value))
    denominations.reverse()

    country = dict(name=name,
                   name_long=name_long,
                   denominations=denominations,
                   divisions=divisions,
                   inventory=[])
    utils.save_country(country)


if __name__ == "__main__":
    main()
