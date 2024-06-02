#!/usr/bin/env python3
import argparse

import models


def parse_args():
    description = "Validate all country data"
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument(
        "--overwrite",
        "-o",
        required=False,
        default=False,
        action="store_true",
        help="Overwrite the current data file after validating")

    return argparser.parse_args()


def main():
    args = parse_args()
    countries = models.Country.load_all()

    for country in countries:
        print("Validating {}".format(country.long_name))
        country.validate()
        if args.overwrite:
            country.save()


if __name__ == "__main__":
    main()
