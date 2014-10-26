#!/usr/bin/env python
import os

from cartopy import crs
from cartopy.io import shapereader
from matplotlib import pyplot

import total
import utils


COLOR_NOT_PRESENT = (1.0, 1.0, 1.0)
COLOR_OBSOLETE = (0.4, 0.4, 0.8)
COLOR_PRESENT = (0.2, 0.2, 0.9)

EUROZONE_COUNTRIES = [
    "Austria",
    "Belgium",
    "Cyprus",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Ireland",
    "Italy",
    "Latvia",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Portugal",
    "Slovakia",
    "Slovenia",
    "Spain",
]


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
    # Handle the Eurozone
    eu_total = countries.pop("Eurozone")
    for country in EUROZONE_COUNTRIES:
        countries[country] = eu_total
    countries['United States'] = 1.00
    return countries


def create_world_map(countries_owned):
    """ Creates a plot object of a world map with present countries highlighted

    :param countries_owned:  A dictionary of country names mapped to boolean
                             values.  Falsey boolean values indicate that the
                             country is present, but all present currency is
                             obsolete.
    """
    # based on http://stackoverflow.com/questions/13397022
    plot = pyplot.axes(projection=crs.PlateCarree())
    geodata = shapereader.natural_earth(resolution='110m', category='cultural',
                                        name='admin_0_countries')
    georeader = shapereader.Reader(geodata)
    for country in georeader.records():
        color = COLOR_NOT_PRESENT
        if country.attributes['name_long'] in countries_owned:
            if countries_owned[country.attributes['name_long']]:
                color = COLOR_PRESENT
            else:
                color = COLOR_OBSOLETE
        plot.add_geometries(country.geometry, crs.PlateCarree(),
                            facecolor=color, edgecolor='gray')
    plot.coastlines()
    plot.figure.set_size_inches(16, 12)
    pyplot.savefig("map.png", bbox_inches='tight')


def main():
    countries_owned = load_countries()
    create_world_map(countries_owned)


if __name__ == "__main__":
    main()
