#!/usr/bin/env python
import argparse
import os
import sys

import constants
import models


def parse_args():
    description = ("Add a new country to the collection, creating all the "
                   "metadata.")
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("short_name",
                           type=str,
                           nargs='?',
                           default='',
                           help="Short name of country")
    args = argparser.parse_args()
    return args


def parse_bool(instring):
    instring = instring.lower()
    if 'y' in instring and 'n' not in instring:
        return True
    if 'n' in instring and not 'y' in instring:
        return False
    print "Could not parse %s into a boolean" % instring
    prompt = "Try again, or press Ctrl-C to exit [y|n]:  "
    return parse_bool(raw_input(prompt))


def create_subdivision(big_unit, small_unit, value):
    """ Create a subdivision dict for totalling

    For more info on subdivision dicts, see the module docs for ``total``,
    but the tl;dr is there are <value> <small_units> in a <big_unit>.
    Ex:  There are <100> <cents> in a <dollar>.
    """
    division = {
        big_unit: {
            "subunit": small_unit,
            "value": value
        }
    }
    return division


def read_denomination():
    name = raw_input("Denomination names (most recent first):  ")
    if not name:
        return None
    code = raw_input("    ISO-4217 code:  ").upper()
    obsolete = parse_bool(raw_input("    Obsolete?  [y|n]  "))
    subunits = []
    while True:
        subunit = raw_input("    Subunits (largest first):  ")
        if not subunit:
            break
        subunits.append(subunit)
    smallest_unit = subunits[-1]
    divisions = create_subdivision(smallest_unit, smallest_unit, 1)
    subunits.reverse()
    for i, unit in enumerate(subunits[:-1]):
        bigger_unit = subunits[i+1]
        value = int(raw_input("        How many %s in %s?  " %
                              (unit, bigger_unit)))
        divisions.update(create_subdivision(bigger_unit, unit, value))
    subunits.reverse()
    return dict(name=name,
                code=code,
                subunits=subunits,
                divisions=divisions,
                obsolete=obsolete)


def read_input(short_name):
    long_name = short_name.replace('-', ' ').title()
    long_name_prompt = "Country name (long) [%s]:  " % long_name
    long_name = raw_input(long_name_prompt) or long_name

    denominations = []
    while True:
        denomination = read_denomination()
        if not denomination:
            break
        denominations.append(denomination)

    if denominations[0]['obsolete']:
        confirm_prompt = ("Newest denomination is obsolete.  Is this "
                          "correct?  [y|n]  ")
        confirm = parse_bool(raw_input(confirm_prompt))
        if not confirm:
            denominations[0]['obsolete'] = False

    country = models.Country.from_dict(dict(short_name=short_name,
                                            long_name=long_name,
                                            denominations=denominations,
                                            inventory=[]))
    country.save()


def main():
    args = parse_args()
    short_name = args.short_name or raw_input("Country name (short):  ")

    path = os.path.join(constants.COUNTRY_DIR, short_name + ".json")
    if os.path.exists(path):
        print "Country %s already exists!" % short_name
        sys.exit(1)

    read_input(short_name)


if __name__ == "__main__":
    main()
