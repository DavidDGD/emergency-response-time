import pandas as pd
import numpy as np


# translate columns to English
def translate_columns(a_df):
    """
    Translate the columns in the dataframe
    """
    translation_map = {
        "Latitude (WGS84)": "lat",
        "Longitude (WGS84)": "lon",
        "Gebruiksdoel": "usage",
        "Naam openbare ruimte": "streetname",
        "Huisnummer": "street_number",
        "Huisletter": "street_number_additional_letter",
        "Huisnummertoevoeging": "street_number_addition",
        "Postcode": "zipcode",
        "Naam stadsdeel": "subcity name",
        "Naam Wijk": "subsubcity name",
        "Naam buurt": "subsubsubcity name",
        "Ligging": "surrounding_type",
        "Oorspronkelijk bouwjaar": "year_built",
        "Oppervlakte (m2)": "internal_area",
        "Aantal bouwlagen": "number_of_layers",
        "Hoogste bouwlaag": "highest_layer",
        "Laagste bouwlaag": "lowest_layer",
        "Toegang": "entry_type",
        "Aantal kamers": "number_of_rooms",
        "Aantal eenheden complex": "number_of_units",
        "Openbareruimte-identificatie": "public_space_id",
        "Pandidentificatie": "property_id",
        "Verblijfsobjectidentificatie": "residental_object_id",
        "Ligplaatsidentificatie": "boat_place_id",
        "Standplaatsidentificatie": "caravan_place_id",
        "Nummeraanduidingidentificatie": "number_id",
        "Objecttype": "object_type"
    }

    df = a_df[translation_map.keys()]
    df = df.rename(columns=translation_map, errors='ignore')

    return df

# function that makes sure that number_of_layers contains the highest number
def layers(col1, col2):
    if col1 < col2:
        col1 = col2
        return col1
    else:
        return col1




def clean(df):
    """
    Remove irrelevant rows and clean
    """

    # Remove all non commercial properties
    df = df[df['usage'] != 'woonfunctie']

    # Convert coordinates to floats
    df['lat'] = df['lat'].str.replace(',', '.').astype(float)
    df['lon'] = df['lon'].str.replace(',', '.').astype(float)

    # Fix missing and incorrect values
    subset = df[(df["internal_area"] != 1.0)]
    mean = round(subset["internal_area"].mean(), 1)

    # replacing all the 1.0 values with the mean
    df['internal_area'] = df['internal_area'].replace(1.0, mean)
    df['internal_area'] = df['internal_area'].replace(np.nan, mean)

    # replacing nan values with 1.0
    df['number_of_layers'] = df['number_of_layers'].replace(np.nan, 1.0)

    # select highest from number of layers and highest layer
    df['number_of_layers'] = df.apply(lambda x: layers(x.number_of_layers, x.highest_layer), axis=1)

    return df


def preprocess():
    # data set obtained from https://www.amsterdam.nl/stelselpedia/bag-index/producten-bag/csv-objectlevering-'actueel'/
    df = pd.read_csv('Model/Data/export_20201110_170438.csv', sep=';', low_memory=False)

    # df = df.head(10) # @TODO remove this line

    df = translate_columns(df)
    df = clean(df)

    return df
