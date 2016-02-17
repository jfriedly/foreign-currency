#!/usr/bin/env python
""" Generate a map of all the countries that we have currency for

This script uses data from Natural Earth for country borders and plots them
onto a map using Cartopy with matplotlib.

http://www.naturalearthdata.com/
"""
import argparse
from cartopy import crs
from cartopy.io import shapereader
from matplotlib import pyplot

import constants
import models
import total


COLOR_NOT_PRESENT = (1.0, 1.0, 1.0)
COLOR_OBSOLETE = (0.4, 0.4, 0.8)
COLOR_PRESENT = (0.2, 0.2, 0.9)


def _get_long_name(country):
    """ Retrieve the long name of a country from Natural Earth data

    Their low-res (110m) data uses the attribute name 'name_long', while
    their high-res (10m) data uses the attribute name 'NAME_LONG'.
    """
    try:
        return country.attributes['name_long']
    except KeyError:
        return country.attributes['NAME_LONG']


def parse_args():
    description = "Generate a map of countries that I have currency pieces for"
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("--med-res", "-m", "-M",
                           required=False,
                           default=False,
                           action="store_true",
                           help="use medium resolution map data")
    argparser.add_argument("--high-res", "-H",
                           required=False,
                           default=False,
                           action="store_true",
                           help="use high resolution map data")
    return argparser.parse_args()


def load_countries():
    """ Loads countries from the data dir and returns them

    :returns:  a dictionary of country names mapped to non-obsolete totals
    """
    countries = models.Country.load_all()
    country_totals = {c.long_name: total.total(c) for c in countries}

    # This map would look pretty silly if the US wasn't blue.
    country_totals["United States"] = 1.00
    return country_totals


def correct_for_mapping(countries):
    """ Convert currency-oriented data to map-oriented data

    Euros are used by all of the countries in the Eurozone, but Natural Earth
    treats them all as different countries instead of one.  So we pop the
    Eurozone "country" here and add in all the real Eurozone countries.

    Natural Earth treats Greenland as separate from Denmark, but Greenland uses
    the Danish krone, so we add Greenland if Denmark is present.

    The British colony of East Africa, the East Africa Protectorate, no
    longer exists.  It was basically the same area as modern Kenya though, so
    we count it as obsolete Kenyan currency for the map.

    Macau can also be spelled Macao, and Natural Earth uses the second form.

    The Dutch East Indies no longer exist; Indonesia won independence from the
    Dutch in 1949.  I count the Dutch East Indies currency that I have as
    obsolete Indonesian currency for the purpose of mapping.

    The Common Monetary Area of southern Africa is a Eurozone-like entity where
    multiple countries share a currency.  In this case, they share the South
    African rand.  Namibia is no longer a member of the CMA, but the rand is
    still legal tender there and is exchanged on par with the Namibian dollar,
    so I also count Namibia as blue.
    """
    if "Eurozone" in countries:
        eu_total = countries.pop("Eurozone")
        for country in constants.EUROZONE_COUNTRIES:
            countries[country] = eu_total

    if "Denmark" in countries:
        countries["Greenland"] = countries["Denmark"]

    if "East Africa Protectorate" in countries:
        countries.pop("East Africa Protectorate")
        countries.setdefault("Kenya", 0)

    if "Macau" in countries:
        countries["Macao"] = countries.pop("Macau")

    if "Dutch East Indies" in countries:
        countries.pop("Dutch East Indies")
        countries.setdefault("Indonesia", 0)

    if "South Africa" in countries:
        for country in constants.COMMON_MONETARY_AREA_COUNTRIES:
            countries[country] = countries["South Africa"]
        countries["Namibia"] = countries["South Africa"]

    return countries


def iter_country_shapes(args):
    """ Get an iterator of shapereader Records for all Natural Earth countries
    """
    if args.med_res:
        resolution = "50m"
    elif args.high_res:
        resolution = "10m"
    else:
        resolution = "110m"

    geodata = shapereader.natural_earth(resolution=resolution,
                                        category='cultural',
                                        name='admin_0_countries')
    georeader = shapereader.Reader(geodata)
    return georeader.records()


def natural_earth_country_list():
    """ Name every country according to Natural Earth

    This function is unused in the code; it's for debugging only.
    """
    country_names = []
    for country in iter_country_shapes():
        country_names.append(_get_long_name(country))
    return country_names


def create_world_map(args, countries_owned):
    """ Creates a plot object of a world map with present countries highlighted

    :param countries_owned:  A dictionary of country names mapped to boolean
                             values.  Falsey boolean values indicate that the
                             country is present, but all present currency is
                             obsolete.
    """
    # based on http://stackoverflow.com/questions/13397022
    plot = pyplot.axes(projection=crs.PlateCarree())
    for country in iter_country_shapes(args):
        color = COLOR_NOT_PRESENT
        long_name = _get_long_name(country)
        if long_name in countries_owned:
            if countries_owned[long_name]:
                color = COLOR_PRESENT
            else:
                color = COLOR_OBSOLETE
        plot.add_geometries(country.geometry, crs.PlateCarree(),
                            facecolor=color, edgecolor='gray')
    plot.coastlines()
    # Use a larger figure size for more pixels.  4:3 is a nice ratio though
    plot.figure.set_size_inches(16, 12)
    pyplot.savefig("map.png", bbox_inches='tight')


def main():
    args = parse_args()
    countries_owned = load_countries()
    mappable_countries = correct_for_mapping(countries_owned)
    create_world_map(args, mappable_countries)


if __name__ == "__main__":
    main()
