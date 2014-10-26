#!/usr/bin/env python
import argparse

import utils


def parse_args():
    description = "Add foreign currency to my collection."
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("country",
                           type=str,
                           help="Country this currency is from.")
    argparser.add_argument("value",
                           type=int,
                           help="Face value of the currency (integer)")
    argparser.add_argument("denomination",
                           type=str,
                           help=("Plural Denomination of the currency (e.g. "
                                 "cents, dollars, etc.)"))
    argparser.add_argument("year",
                           type=int,
                           nargs='?',
                           default=0,
                           help="Year the currency was printed/minted.")
    argparser.add_argument("--bill", "-b",
                           required=False,
                           default=False,
                           action="store_true",
                           help="This currency is a bill.")
    argparser.add_argument("--obsolete", "-o",
                           required=False,
                           default=False,
                           action="store_true",
                           help="This currency is obsolete.")
    argparser.add_argument("--owner",
                           type=str,
                           required=False,
                           default="Joel Friedly",
                           help="Name of the owner of this currency.")

    return argparser.parse_args()


def validate(args, country):
    """ Checks that the denomination exists. """
    assert args.denomination in country['denominations'], ("Denomination "
        "does not exist")


def create_currency_unit(args):
    """ Creates the dict that will be saved for this unit of currency. """
    currency_type = "coin"
    if args.bill:
        currency_type = "bill"
    currency_unit = {
        "value": args.value,
        "denomination": args.denomination,
        "year": args.year,
        "type": currency_type,
        "owner": args.owner,
        "obsolete": args.obsolete
    }
    return currency_unit


def main():
    args = parse_args()
    country = utils.load_country(args.country)
    validate(args, country)
    country['inventory'].append(create_currency_unit(args))
    utils.save_country(country)


if __name__ == "__main__":
    main()
