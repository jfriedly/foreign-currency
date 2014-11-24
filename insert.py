#!/usr/bin/env python
import argparse

import models


def parse_args():
    description = "Add foreign currency to my collection."
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("country",
                           type=str,
                           help="Country this currency is from.")
    argparser.add_argument("value",
                           type=int,
                           help="Face value of the currency (integer)")
    argparser.add_argument("subunit",
                           type=str,
                           help=("Plural subunit of the currency (e.g. "
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
    argparser.add_argument("--denomination", "-d",
                           required=False,
                           default='',
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


def create_currency_unit(args):
    """ Creates the dict that will be saved for this unit of currency. """
    piece_type = "coin"
    if args.bill:
        piece_type = "bill"
    currency_unit = {
        "value": args.value,
        "subunit": args.subunit,
        "denomination": args.denomination,
        "year": args.year,
        "piece_type": piece_type,
        "owner": args.owner,
        "obsolete": args.obsolete
    }
    return models.CurrencyPiece.from_dict(currency_unit)


def main():
    args = parse_args()
    country = models.Country.load(args.country)
    if not args.denomination:
        args.denomination = country.denominations[0].name
    country.inventory.append(create_currency_unit(args))
    country.save()


if __name__ == "__main__":
    main()
