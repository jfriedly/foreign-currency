#!/usr/bin/env python
""" Compute and print the total value of present currency for a country

Since denominations often have subunits, we need a way to add these up
correctly.  The ``total`` function in this module does that by calling the
recursive function ``sum_units`` appropriately.  The ``sum_units`` function
inspects a denomination's subunits, and adds up the total in the largest unit
available.

See the docstring for models.Denomination for documentation on the subunit
data structure.
"""
import argparse
import copy
import os

import constants
import models


def parse_args():
    description = ("Print the total value of the currency that I have for a "
                   "country.")
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("country",
                           type=str,
                           help="Country to sum.")
    argparser.add_argument("--verbose", "-v",
                           required=False,
                           default=False,
                           action="store_true",
                           help="Print totals for all denominations.")
    args = argparser.parse_args()

    # Allow file paths
    args.country = os.path.basename(args.country)
    if args.country.endswith(".json"):
        args.country = args.country[:-5]
    return args


def sum_units(desired_unit, totals, divisions, divisor):
    """ Given a mapping of how a country's currency units are divided along
    with the totals of each currency unit and a desired unit, print out the
    sum of all the currency in the desired unit.

    See the docstring for `models.Denomination` for more info on the divisions
    data structure.
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
    if desired_unit == breakdown['subunit']:
        if breakdown['value'] == 1:
            return this_denomination
        else:
            raise ValueError("Denomination '%s' is broken down into %s %s!" %
                             (desired_unit, breakdown['value'],
                              breakdown['subunit']))
    return this_denomination + sum_units(breakdown['subunit'],
                                         totals,
                                         divisions,
                                         divisor * breakdown['value'])


def total(country, denomination=None, count_obsolete=False):
    """ Calculates the total value of a country's inventory of one denomination

    :param country:  A `Country`_ object
    :param denomination:  The denomination that should be counted.  Defaults
                          to the most recent denomination.
    :param count_obsolete:  A boolean that indicates that only obsolete pieces
                            from the denomination should be counted If the
                            denomination is obsolete, this parameter will
                            default to True.
    :returns:  The total for this denomination of this country, in terms of
               the denomination's principal unit
    """
    denomination = denomination or country.denominations[0]
    count_obsolete |= denomination.obsolete
    totals = {subunit: 0 for subunit in denomination.subunits}
    for piece in country.inventory:
        if piece.denomination == denomination.name:
            if not piece.obsolete and denomination.obsolete:
                print ("WARN:  piece is not obsolete, but it's "
                       "denomination is:\n%s" % piece.to_dict())
            # A piece may be from the current denomination, but be completely
            # removed from circulation and practically speaking obsolete.  Ex:
            # the 2 fen Chinese bill that I have.  We'll skip counting those.
            if piece.obsolete == count_obsolete:
                totals[piece.subunit] += piece.value
    # The denomination's subunits should be ordered from largest to smallest
    desired_unit = denomination.subunits[0]
    divisions = copy.deepcopy(denomination.divisions)
    return sum_units(desired_unit, totals, divisions, 1)


def _format_country(country, denomination=None, count_obsolete=False):
    """ String format the total for one denomination of one country """
    denomination = denomination or country.denominations[0]
    out = "%(currency_total).2f %(denom_name)s"
    currency_total = total(country, denomination, count_obsolete)
    if denomination.obsolete or count_obsolete:
        out = "(obsolete) " + out
    if denomination.code:
        out += " (%(code)s)"
    out = out % dict(currency_total=currency_total,
                     denom_name=denomination.name,
                     code=denomination.code)
    return out


def format_country(country, verbose=False):
    out = "%(name_long)s:  %(current_total)s %(eurozone_total)s"
    current_total = _format_country(country)
    # Currency from Eurozone countries is all obsolete, but I have Euros
    if country.long_name in constants.EUROZONE_COUNTRIES:
        eurozone = models.Country.load('eurozone')
        eurozone_total = "[Eurozone:  %s]" % _format_country(eurozone)
    else:
        eurozone_total = ''
    if verbose:
        if not country.denominations[0].obsolete:
            if total(country, count_obsolete=True) != 0.00:
                out += "\n    %s" % _format_country(country,
                                                    count_obsolete=True)
        for denomination in country.denominations[1:]:
            out += "\n    %s" % _format_country(country, denomination)
    return out % dict(name_long=country.long_name,
                      current_total=current_total,
                      eurozone_total=eurozone_total)


def main():
    args = parse_args()
    country = models.Country.load(args.country)
    print format_country(country, verbose=args.verbose)


if __name__ == "__main__":
    main()
