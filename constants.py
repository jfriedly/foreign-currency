import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
COUNTRY_DIR = DATA_DIR
EUROZONE_COUNTRIES = set([
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
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Portugal",
    "Slovakia",
    "Slovenia",
    "Spain",
])
CEMAC_LONG_NAME = u"Communaut\xe9 \xc9conomique et Mon\xe9taire de l'Afrique Centrale"
CEMAC_COUNTRIES = set([
    "Cameroon",
    "Central African Republic",
    "Chad",
    "Republic of Congo",
    "Equatorial Guinea",
    "Gabon",
])
COMMON_MONETARY_AREA_COUNTRIES = set([
    "South Africa",
    "Namibia",
    "Kingdom of eSwatini",
    "Lesotho",
])
