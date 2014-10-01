#!/usr/bin/env python
import argparse
import utils


def parse_args():
    description = ("Print the total value of the currency that I have for a "
                   "country.")
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("country",
                           type=str,
                           help="Country to sum.")
    return argparser.parse_args()


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


def main():
    args = parse_args()
    country = utils.load_country(args.country)
    totals = {denomination: 0 for denomination in country['denominations']}
    for unit in country['inventory']:
        if not unit['obsolete']:
            totals[unit['denomination']] += unit['value']
    # The country's denominations should be ordered from largest to smallest
    biggest_unit = country['denominations'][0]
    total = sum_units(biggest_unit, totals, country['divisions'], 1)
    print "%f %s" % (total, biggest_unit)


if __name__ == "__main__":
    main()
