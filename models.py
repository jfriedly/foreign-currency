import json
import os
import sys

import constants


class Country(object):
    """ Class to represent one country, handling many denominations """
    def __init__(self,
                 short_name='',
                 long_name='',
                 denominations=None,
                 inventory=None):
        # A short, typable name for the country.  The data filename will be
        # based on this, and all UI components will use this name.
        self.short_name = short_name
        # We use data from Natural Earth to draw the maps based on country name
        self.long_name = long_name
        # This will be a list of Denomination objects, ordered by date
        self.denominations = denominations or []
        # Inventory of CurrencyPieces for this country.
        self.inventory = inventory or []

    def get_denomination(self, denom_name):
        """ Given the name of a denomination for this country, return it """
        for denom in self.denominations:
            if denom_name == denom.name:
                return denom
        else:  # pylint: disable=W0120
            raise KeyError("Denomination '%s' not found" % denom_name)

    def validate(self):
        """ Validates the data in a country object.

        We explicitly allow countries to not have natural earth names.
        We explicitly allow all denominations to be obsolete (think Eurozone).
        We explicitly allow a country to have no an empty inventory.

        We do not check types.  That would add lots of boilerplate.
        """
        assert self.short_name, "Missing short name"
        assert len(self.denominations), "Must have at least one denomination"
        for denom in self.denominations:
            denom.validate()
        non_obsolete = [d for d in self.denominations if not d.obsolete]
        for piece in self.inventory:
            piece.validate()
            # Ensure that the piece's denomination exists
            denom = self.get_denomination(piece.denomination)
            assert piece.subunit in denom.subunits, (
                "Piece's subunit not in denomination")

    @classmethod
    def from_dict(cls, dictionary):
        for i, piece_dict in enumerate(dictionary['inventory']):
            dictionary['inventory'][i] = CurrencyPiece.from_dict(piece_dict)
        for i, denom_dict in enumerate(dictionary['denominations']):
            dictionary['denominations'][i] = Denomination.from_dict(denom_dict)
        return cls(**dictionary)

    def to_dict(self):
        inventory = [piece.to_dict() for piece in self.inventory]
        denominations = [denom.to_dict() for denom in self.denominations]
        return dict(short_name=self.short_name,
                    long_name=self.long_name,
                    denominations=denominations,
                    inventory=inventory)

    def save(self):
        self.validate()
        path = os.path.join(constants.COUNTRY_DIR, "%s.json" % self.short_name)
        # Serialize before opening the file.  That way if serialization fails,
        # we don't truncate the file
        json_serialized = json.dumps(self.to_dict(), indent=4)
        with open(path, 'w') as json_file:
            json_file.write(json_serialized)

    @classmethod
    def load(cls, short_name):
        path = os.path.join(constants.COUNTRY_DIR, "%s.json" % short_name)
        try:
            with open(path, 'r') as json_file:
                json_data = json.loads(json_file.read())
        except IOError as e:
            if e.errno == 2:
                print("Could not find country data for %s in %s" %
                      (short_name, constants.COUNTRY_DIR))
                sys.exit(1)
            raise
        return cls.from_dict(json_data)

    @classmethod
    def load_all(cls):
        """ For every file in the country data dir, load the country and return
        them all in a list
        """
        countries = []
        for filename in os.listdir(constants.COUNTRY_DIR):
            # Ignore hidden files -- vim creates hidden temporary swap files
            if filename.startswith('.'):
                continue
            # Strip the ".json" suffix
            short_name = filename[:-5]
            countries.append(cls.load(short_name))
        return countries


class CurrencyPiece(object):
    """ Class to represent one piece of currency:  a bill or a coin """
    def __init__(self,
                 piece_type='bill',
                 obsolete=False,
                 denomination='',
                 value=0,
                 subunit='',
                 year=0,
                 owner="Joel Friedly"):
        # Either the string "bill" or "coin"
        self.piece_type = piece_type
        # A boolean indicating whether or not this piece is obsolete
        self.obsolete = obsolete
        # The country-unique name for the denomination this piece belongs to
        # Ex:  "pesos ley" or "pesos argentino", but *not* "pesos"
        self.denomination = denomination
        # The face value of this piece, usually an integer
        # Ex:  a dime would have a value of 10 and a subunit of "cents"
        self.value = value
        # The subunit this piece is valued in terms of
        # Ex:  a dime would have a value of 10 and a subunit of "cents"
        self.subunit = subunit
        # The year that this piece was printed/minted, if available
        self.year = year
        # The owner of this piece (a few pieces in my collection aren't
        # actually mine)
        self.owner = owner

    def validate(self):
        """ Validate a piece of currency

        We explicitly allow floating point piece values.
        We explicitly allow years to be zero.
        We do not check types.  That would add lots of boilerplate.
        """
        assert self.piece_type == "coin" or self.piece_type == "bill", (
            "Piece type must be 'coin' or 'bill'")
        assert self.obsolete is True or self.obsolete is False, (
            "Piece's obsolete attribute must be True or False")
        assert self.denomination, "Piece must have a denomination"
        assert self.value > 0, "Piece must have a nonnegative value"
        assert self.subunit, "Piece must have a subunit"
        assert self.year >= 0, "Piece year must be nonnegative"
        assert self.owner, "Piece must have an owner"

    @classmethod
    def from_dict(cls, dictionary):
        return cls(**dictionary)

    def to_dict(self):
        return dict(piece_type=self.piece_type,
                    obsolete=self.obsolete,
                    denomination=self.denomination,
                    value=self.value,
                    subunit=self.subunit,
                    year=self.year,
                    owner=self.owner)


class Denomination(object):
    """ Class to represent one denomination of currency for a country.

    Summary
    -------

    Let's start with a few examples:

    * The United States has exactly one denomination, the US dollar (USD)
    * Argentina has had several denominations:  the peso ley (ARL), the peso
    argentino (ARP), the austral (ARA), and the peso convertible (ARS).

    These denominations are tracked by ISO-4217 and this class contains methods
    for extracting metadata about these denominations from the published
    ISO-4217 XML.  I'm keeping the XML files in data/iso-4217, and I've made a
    few minor edits to the historical XML data file, so diff it against new
    ones before using them.  They are published at
    http://www.currency-iso.org/en/home/tables.html

    Subunits
    --------

    Subunits (e.g. "cents") of a denomination are not handled very well by
    ISO-4217, so I'm using a custom tracking system for those.

    The data format for subunits is defined as follows:  "divisions" must map
    to a dictionary which will have one key for each unit.  These keys must map
    to dictionaries that contain two keys:

    * "denomination": the name of the next smaller unit, or None if this is the
                      smallest
    * "value": the number of the next smallest unit in this unit, or 1 if this
               is the smallest unit.

    For example::

        "divisions": {
            "dollars": {
                "subunit": "cents",
                "value": 100
            },
            "cents": {
                "subunit": "cents",
                "value": 1
            }
        }

    The first sub dict above means that there are 100 cents in a dollar, and
    the second subdict means that there are 1 cent in a cent (this is our
    recursive exit condition).

    For a more complex example handling three tiers of subdivisions in an
    obsolete denomination, see the Australia data file.  The total for any
    denomination may be computed by calling total with the desired
    `Denomination`_ object.

        total(australia, desired_unit="pounds", count_obsolete=True)
    """
    def __init__(self,
                 name='',
                 code='',
                 subunits=None,
                 divisions=None,
                 obsolete=False):
        # A country-unique name for this denomination.
        # Ex:  "pesos ley" or "pesos argentino", but *not* "pesos"
        self.name = name
        # The three-letter ISO-4217 code for this denomination, if one exists
        self.code = code
        # A list of the subunits of this denomination, sorted from largest
        # value to smallest.  Ex: ['pesos', 'centavos']
        self.subunits = subunits or list()
        # A dictionary that maps larger units to smaller units with multipliers
        # indicating how many of a smaller unit is in a larger unit.
        # See the docstring above for more info.
        self.divisions = divisions or dict()
        # A boolean indicating if this denomination is obsolete
        self.obsolete = obsolete

    def validate(self):
        """ Validate a denomination

        We explicitly allow denominations to not have ISO-4217 codes.
        We explicitly allow divisions to be floating point numbers

        We do not check types.  That would add lots of boilerplate.
        """
        assert self.name, "Denomination missing name"
        assert self.subunits, "Must have at least one subunit"
        assert self.divisions, "Must have at least one division"
        assert set(self.subunits) == set(self.divisions.keys()), (
            "Subunits do not perfectly match division keys")
        subunits_seen = set()
        for subunit_key, division in self.divisions.items():
            assert 'value' in division, "Division must have a value"
            assert 'subunit' in division, "Division must have a subunit"
            subunit = division['subunit']
            value = division['value']
            assert value > 0, "Division's value must be nonnegative"
            assert subunit in self.subunits, "Division's subunit DNE"
            if subunit == subunit_key:
                assert value == 1, (
                    "Self-mapping division must have a value of 1")
            subunits_seen.add(subunit)
        assert set(self.subunits[1:]) == subunits_seen, (
            "Subunits do not perfectly match division values")
        assert self.obsolete is True or self.obsolete is False, (
            "Denomination's obsolete attribute must be True or False")

    @classmethod
    def from_dict(cls, dictionary):
        return cls(**dictionary)

    def to_dict(self):
        return dict(name=self.name,
                    code=self.code,
                    subunits=self.subunits,
                    divisions=self.divisions,
                    obsolete=self.obsolete)
