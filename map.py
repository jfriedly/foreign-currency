#!/usr/bin/env python
""" Generate a map of all the countries that we have currency for

This script uses data from Natural Earth for country borders and plots them
onto a map using Cartopy with matplotlib.

http://www.naturalearthdata.com/
"""
import os

from cartopy import crs
from cartopy.io import shapereader
from matplotlib import pyplot

import total
import utils


COLOR_NOT_PRESENT = (1.0, 1.0, 1.0)
COLOR_OBSOLETE = (0.4, 0.4, 0.8)
COLOR_PRESENT = (0.2, 0.2, 0.9)


def load_countries():
    """ Loads countries from the data dir and returns them

    :returns:  a dictionary of country names mapped to non-obsolete totals
    """
    countries = dict()
    for filename in os.listdir(utils.DATA_DIR):
        # Ignore hidden files -- vim creates hidden temporary swap files
        if filename.startswith('.'):
            continue
        # Strip the ".json" suffix
        country = utils.load_country(filename[:-5])
        countries[country['name_long']] = total.total(country)

    # This map would look pretty silly if the US wasn't blue.
    countries["United States"] = 1.00
    return countries


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
    """
    if "Eurozone" in countries:
        eu_total = countries.pop("Eurozone")
        for country in utils.EUROZONE_COUNTRIES:
            countries[country] = eu_total

    if "Denmark" in countries:
        countries["Greenland"] = countries["Denmark"]

    if "East Africa Protectorate" in countries:
        countries.pop("East Africa Protectorate")
        countries.setdefault("Kenya", 0)

    if "Macau" in countries:
        countries["Macao"] = countries.pop("Macau")

    return countries


def iter_country_shapes():
    """ Get an iterator of shapereader Records for all Natural Earth countries
    """
    # Use a resolution of 50m or 10m for better precision
    geodata = shapereader.natural_earth(resolution='110m', category='cultural',
                                        name='admin_0_countries')
    georeader = shapereader.Reader(geodata)
    return georeader.records()


def natural_earth_country_list():
    """ Name every country according to Natural Earth

    This function is unused in the code; it's for debugging only.
    """
    country_names = []
    for country in iter_country_shapes():
        country_names.append(country.attributes['name_long'])
    return country_names


def create_world_map(countries_owned):
    """ Creates a plot object of a world map with present countries highlighted

    :param countries_owned:  A dictionary of country names mapped to boolean
                             values.  Falsey boolean values indicate that the
                             country is present, but all present currency is
                             obsolete.
    """
    # based on http://stackoverflow.com/questions/13397022
    plot = pyplot.axes(projection=crs.PlateCarree())
    for country in iter_country_shapes():
        color = COLOR_NOT_PRESENT
        if country.attributes['name_long'] in countries_owned:
            if countries_owned[country.attributes['name_long']]:
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
    countries_owned = load_countries()
    mappable_countries = correct_for_mapping(countries_owned)
    create_world_map(mappable_countries)


if __name__ == "__main__":
    main()
