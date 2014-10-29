#!/usr/bin/env python
import argparse
import copy

import utils


def parse_args():
    description = ("Print the total value of the currency that I have for a "
                   "country.")
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("country",
                           type=str,
                           help="Country to sum.")
    args = argparser.parse_args()

    # Allow file paths
    if args.country.startswith("data/"):
        args.country = args.country[5:]
    if args.country.endswith(".json"):
        args.country = args.country[:-5]
    return args


def sum_units(desired_unit, totals, divisions, divisor):
    """ Given a mapping of how a country's currency units are divided along
    with the totals of each currency unit and a desired unit, print out the
    sum of all the currency in the desired unit.
    """
    if len(divisions) == 0 and len(totals) == 0:
        return 0.0
    elif len(divisions) == 0:
        raise ValueError("Divisions is empty but totals is %s" % totals)
    elif len(totals) == 0:
        raise ValueError("Totals is empty but divisions is %s" % divisions)
    breakdown = divisions.pop(desired_unit)
    this_denomination = float(totals.pop(desired_unit)) / divisor
    # Exit when we hit a denomination which is subdivided by one of itself
    if desired_unit == breakdown['denomination']:
        if breakdown['value'] == 1:
            return this_denomination
        else:
            raise ValueError("Denomination '%s' is broken down into %s %s!" %
                             (desired_unit, breakdown['value'],
                              breakdown['denomination']))
    return this_denomination + sum_units(breakdown['denomination'],
                                         totals,
                                         divisions,
                                         divisor * breakdown['value'])


def total(country, count_obsolete=False):
    """ Calculates the non-obsolete total value of a country's inventory

    :param country:  A country dictionary loaded from a file in the data dir
    :param count_obsolete:  Boolean whether or not to count obsolete pieces
    :returns:  The non-obsolete total for this country, expressed in terms of
               the largest unit
    """
    totals = {denomination: 0 for denomination in country['denominations']}
    for unit in country['inventory']:
        if not unit['obsolete'] or count_obsolete:
            totals[unit['denomination']] += unit['value']
    # The country's denominations should be ordered from largest to smallest
    biggest_unit = country['denominations'][0]
    divisions = copy.deepcopy(country['divisions'])
    return sum_units(biggest_unit, totals, divisions, 1)


def format_country(country):
    """ Print one country's total """
    out = "%(name_long)s:  %(currency_total).2f %(biggest_unit)s"
    non_obsolete_total = total(country)
    if non_obsolete_total == 0.0:
        out = "%(name_long)s:  %(currency_total).2f obsolete %(biggest_unit)s"
        obsolete_total = total(country, count_obsolete=True)
    return out % dict(name_long=country['name_long'],
                      currency_total=(non_obsolete_total or obsolete_total),
                      biggest_unit=country['denominations'][0])


def main():
    args = parse_args()
    country = utils.load_country(args.country)
    out = format_country(country)
    # Currency from Eurozone countries is all obsolete, but I have Euros
    if country['name_long'] in utils.EUROZONE_COUNTRIES:
        out = "%s (%s)" % (out, format_country(utils.load_country('eurozone')))
    print out


if __name__ == "__main__":
    main()
