import frappe

def ensure_currency_exists(currency_code):
    """
    Vérifie si une devise existe dans le DocType Currency. Si elle n'existe pas, la crée.
    """
    if not frappe.db.exists('Currency', currency_code):
        currency_doc = frappe.new_doc('Currency')
        currency_doc.name = currency_code
        currency_doc.enabled = 1
        currency_doc.fraction = 'Cent'  # Ajustez selon la devise
        currency_doc.insert(ignore_permissions=True)
        frappe.db.commit()
    else:
        frappe.db.set_value('Currency', currency_code, 'enabled', 1)

@frappe.whitelist(allow_guest=True)
def populate_country_currency():
    """
    Insère toutes les associations pays-devise dans le DocType Country Currency.
    Retourne un dictionnaire des associations créées.
    """
    # Liste complète des associations pays-devise
    country_currency_map = {
        "Afghanistan": "AFN",
        "Åland Islands": "EUR",
        "Albania": "ALL",
        "Algeria": "DZD",
        "American Samoa": "USD",
        "Andorra": "EUR",
        "Angola": "USD",  # AOA non disponible
        "Anguilla": "XCD",
        "Antarctica": "USD",
        "Antigua and Barbuda": "XCD",
        "Argentina": "ARS",
        "Armenia": "AMD",
        "Aruba": "AWG",
        "Australia": "AUD",
        "Austria": "EUR",
        "Azerbaijan": "USD",  # AZN non disponible
        "Bahamas": "BSD",
        "Bahrain": "BHD",
        "Bangladesh": "BDT",
        "Barbados": "BBD",
        "Belarus": "USD",  # BYN non disponible
        "Belgium": "EUR",
        "Belize": "BZD",
        "Benin": "XOF",
        "Bermuda": "BMD",
        "Bhutan": "BTN",
        "Bolivia, Plurinational State of": "BOB",
        "Bonaire, Sint Eustatius and Saba": "USD",
        "Bosnia and Herzegovina": "BAM",
        "Botswana": "BWP",
        "Bouvet Island": "NOK",
        "Brazil": "BRL",
        "British Indian Ocean Territory": "USD",
        "Brunei Darussalam": "BND",
        "Bulgaria": "BGN",
        "Burkina Faso": "XOF",
        "Burundi": "BIF",
        "Cambodia": "KHR",
        "Cameroon": "XAF",
        "Canada": "CAD",
        "Cape Verde": "CVE",
        "Cayman Islands": "KYD",
        "Central African Republic": "XAF",
        "Chad": "XAF",
        "Chile": "CLP",
        "China": "CNY",
        "Christmas Island": "AUD",
        "Cocos (Keeling) Islands": "AUD",
        "Colombia": "COP",
        "Comoros": "KMF",
        "Congo": "XAF",
        "Congo, The Democratic Republic of the": "CDF",
        "Cook Islands": "NZD",
        "Costa Rica": "CRC",
        "Croatia": "HRK",
        "Cuba": "CUP",
        "Curaçao": "USD",  # ANG non disponible
        "Cyprus": "EUR",
        "Czech Republic": "CZK",
        "Denmark": "DKK",
        "Djibouti": "DJF",
        "Dominica": "XCD",
        "Dominican Republic": "DOP",
        "Ecuador": "USD",
        "Egypt": "EGP",
        "El Salvador": "USD",
        "Equatorial Guinea": "XAF",
        "Eritrea": "ERN",
        "Estonia": "EUR",
        "Ethiopia": "ETB",
        "Falkland Islands (Malvinas)": "FKP",
        "Faroe Islands": "DKK",
        "Fiji": "FJD",
        "Finland": "EUR",
        "France": "EUR",
        "French Guiana": "EUR",
        "French Polynesia": "USD",  # XPF non disponible
        "French Southern Territories": "EUR",
        "Gabon": "XAF",
        "Gambia": "GMD",
        "Georgia": "USD",  # GEL non disponible
        "Germany": "EUR",
        "Ghana": "GHS",
        "Gibraltar": "GIP",
        "Greece": "EUR",
        "Greenland": "DKK",
        "Grenada": "XCD",
        "Guadeloupe": "EUR",
        "Guam": "USD",
        "Guatemala": "GTQ",
        "Guernsey": "GBP",
        "Guinea": "GNF",
        "Guinea-Bissau": "XOF",
        "Guyana": "GYD",
        "Haiti": "HTG",
        "Heard Island and McDonald Islands": "AUD",
        "Holy See (Vatican City State)": "EUR",
        "Honduras": "HNL",
        "Hong Kong": "HKD",
        "Hungary": "HUF",
        "Iceland": "ISK",
        "India": "INR",
        "Indonesia": "IDR",
        "Iran": "IRR",
        "Iraq": "IQD",
        "Ireland": "EUR",
        "Isle of Man": "GBP",
        "Israel": "ILS",
        "Italy": "EUR",
        "Ivory Coast": "XOF",
        "Jamaica": "JMD",
        "Japan": "JPY",
        "Jersey": "GBP",
        "Jordan": "JOD",
        "Kazakhstan": "KZT",
        "Kenya": "KES",
        "Kiribati": "AUD",
        "Korea, Democratic Peoples Republic of": "KPW",
        "Korea, Republic of": "KRW",
        "Kuwait": "KWD",
        "Kyrgyzstan": "KGS",
        "Lao Peoples Democratic Republic": "LAK",
        "Latvia": "EUR",
        "Lebanon": "LBP",
        "Lesotho": "LSL",
        "Liberia": "LRD",
        "Libya": "LYD",
        "Liechtenstein": "CHF",
        "Lithuania": "EUR",
        "Luxembourg": "EUR",
        "Macao": "MOP",
        "Macedonia": "MKD",
        "Madagascar": "USD",  # MGA non disponible
        "Malawi": "MWK",
        "Malaysia": "MYR",
        "Maldives": "MVR",
        "Mali": "XOF",
        "Malta": "EUR",
        "Marshall Islands": "USD",
        "Martinique": "EUR",
        "Mauritania": "MRO",
        "Mauritius": "MUR",
        "Mayotte": "EUR",
        "Mexico": "MXN",
        "Micronesia, Federated States of": "USD",
        "Moldova, Republic of": "MDL",
        "Monaco": "EUR",
        "Mongolia": "MNT",
        "Montenegro": "EUR",
        "Montserrat": "XCD",
        "Morocco": "MAD",
        "Mozambique": "MZN",
        "Myanmar": "MMK",
        "Namibia": "NAD",
        "Nauru": "AUD",
        "Nepal": "NPR",
        "Netherlands": "EUR",
        "New Caledonia": "USD",  # XPF non disponible
        "New Zealand": "NZD",
        "Nicaragua": "NIO",
        "Niger": "XOF",
        "Nigeria": "NGN",
        "Niue": "NZD",
        "Norfolk Island": "AUD",
        "Northern Mariana Islands": "USD",
        "Norway": "NOK",
        "Oman": "OMR",
        "Pakistan": "PKR",
        "Palau": "USD",
        "Palestinian Territory, Occupied": "ILS",
        "Panama": "USD",  # PAB non disponible
        "Papua New Guinea": "PGK",
        "Paraguay": "PYG",
        "Peru": "PEN",
        "Philippines": "PHP",
        "Pitcairn": "NZD",
        "Poland": "PLN",
        "Portugal": "EUR",
        "Puerto Rico": "USD",
        "Qatar": "QAR",
        "Réunion": "EUR",
        "Romania": "RON",
        "Russian Federation": "RUB",
        "Rwanda": "RWF",
        "Saint Barthélemy": "EUR",
        "Saint Helena, Ascension and Tristan da Cunha": "SHP",
        "Saint Kitts and Nevis": "XCD",
        "Saint Lucia": "XCD",
        "Saint Martin (French part)": "EUR",
        "Saint Pierre and Miquelon": "EUR",
        "Saint Vincent and the Grenadines": "XCD",
        "Samoa": "WST",
        "San Marino": "EUR",
        "Sao Tome and Principe": "STD",
        "Saudi Arabia": "SAR",
        "Senegal": "XOF",
        "Serbia": "RSD",
        "Seychelles": "SCR",
        "Sierra Leone": "SLL",
        "Singapore": "SGD",
        "Sint Maarten (Dutch part)": "USD",  # ANG non disponible
        "Slovakia": "EUR",
        "Slovenia": "EUR",
        "Solomon Islands": "SBD",
        "Somalia": "SOS",
        "South Africa": "ZAR",
        "South Georgia and the South Sandwich Islands": "GBP",
        "South Sudan": "USD",  # SSP non disponible
        "Spain": "EUR",
        "Sri Lanka": "LKR",
        "Sudan": "SDG",
        "Suriname": "SRD",
        "Svalbard and Jan Mayen": "NOK",
        "Swaziland": "SZL",
        "Sweden": "SEK",
        "Switzerland": "CHF",
        "Syria": "SYP",
        "Taiwan": "TWD",
        "Tajikistan": "USD",  # TJS non disponible
        "Tanzania": "TZS",
        "Thailand": "THB",
        "Timor-Leste": "USD",
        "Togo": "XOF",
        "Tokelau": "NZD",
        "Tonga": "TOP",
        "Trinidad and Tobago": "TTD",
        "Tunisia": "TND",
        "Türkiye": "TRY",
        "Turkmenistan": "TMM",
        "Turks and Caicos Islands": "USD",
        "Tuvalu": "AUD",
        "Uganda": "UGX",
        "Ukraine": "UAH",
        "United Arab Emirates": "AED",
        "United Kingdom": "GBP",
        "United States": "USD",
        "United States Minor Outlying Islands": "USD",
        "Uruguay": "UYU",
        "Uzbekistan": "UZS",
        "Vanuatu": "VUV",
        "Venezuela, Bolivarian Republic of": "VEF",
        "Vietnam": "VND",
        "Virgin Islands, British": "USD",
        "Virgin Islands, U.S.": "USD",
        "Wallis and Futuna": "USD",  # XPF non disponible
        "Western Sahara": "MAD",
        "Yemen": "YER",
        "Zambia": "ZMW",
        "Zimbabwe": "ZWL"
    }

    # Récupérer tous les pays du DocType Country pour vérification
    countries = frappe.get_all('Country', fields=['name'])
    country_names = {country.name for country in countries}

    # Dictionnaire pour stocker les associations créées
    created_mappings = {}

    # Parcourir la liste des associations
    for country, currency in country_currency_map.items():
        # Vérifier si le pays existe dans le DocType Country
        if country not in country_names:
            frappe.msgprint(f"Pays {country} non trouvé dans le DocType Country. Ignoré.")
            continue

        # Vérifier que la devise existe
        ensure_currency_exists(currency)

        # Vérifier si une association existe déjà
        existing_mapping = frappe.get_all(
            'Country Currency',
            filters={'country': country},
            fields=['name']
        )

        if not existing_mapping:
            # Créer un nouvel enregistrement
            mapping_doc = frappe.new_doc('Country Currency')
            mapping_doc.country = country
            mapping_doc.currency = currency
            mapping_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.msgprint(f"Association ajoutée : {country} -> {currency}")
            created_mappings[country] = currency
        else:
            frappe.msgprint(f"Association déjà existante pour {country}")
            created_mappings[country] = currency

    return created_mappings

def get_country_currency_mapping():
    """
    Récupère toutes les associations pays-devise depuis le DocType Country Currency.
    Retourne un dictionnaire avec les pays comme clés et les devises comme valeurs.
    """
    mappings = frappe.get_all(
        'Country Currency',
        fields=['country', 'currency'],
        filters={}
    )
    return {mapping.country: mapping.currency for mapping in mappings}