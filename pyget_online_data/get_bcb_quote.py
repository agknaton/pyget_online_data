#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch official exchange rate quote for a given period from Central Bank of Brazil (Banco Central do Brasil) into a pandas dataframe

consider for header style upgrade: https://medium.com/@rukavina.andrei/how-to-write-a-python-script-header-51d3cec13731
"""

import requests
import pandas
import datetime
from string import Template

_ENTRYPOINT     = r'http://api.bcb.gov.br/'
_RESOURCE       = r'dados/serie'
_QUERY_TEMPLATE = Template(r'bcdata.sgs.$series_code/dados')


def _retrieve_json (
    start_period    = None, 
    end_period      = None, 
    series_code     = 10813     # Exchange rate - Free - United States dollar (buy), required for Brazilian tax declaration
    ):
    """
    Get JSON with required data
    (datetime)  start_period    : Start of date range
    (datetime)  end_period      : End of date range
    (int)       series_code     : Code for the requested series (https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries)
    """

    # Get start_period = today - ~1 year and end_period = today if undefined
    if end_period is None:
        end_period = datetime.date.today()
    if start_period is None:
        start_period = end_period - datetime.timedelta(days = 365)
    if start_period > end_period:
        start_period = end_period

    # Construct query key
    key = _QUERY_TEMPLATE.substitute(series_code = str(series_code))

    # Construct the URL
    request_url = _ENTRYPOINT + _RESOURCE + '/' + key

    # Put parameters together in the request format
    parameters = {
        'formato'       : 'json',
        'dataInicial'   : start_period.strftime("%d/%m/%Y"),
        'dataFinal'     : end_period.strftime("%d/%m/%Y")
    }

    # Make the HTTP request
    response = requests.get(request_url, params=parameters)
    
    # Check if the response returns succesfully with response code 200
    if response.status_code != 200:
        raise Exception("Query failed")
    
    # Return the JSON reply
    return response.text


def _json2pandas(in_json):
    """
    Convert the JSON response from BCB to a pandas dataframe with date index
    """

    # Read JSON into a pandas dataframe
    df = pandas.read_json(in_json)

    # Rename column names from Portuguese to English (for consistency with other functions)
    df.rename(columns={'data': 'Date', 'valor' : 'value'}, inplace=True)

    # Convert Date column to datetime format
    df['Date'] = pandas.to_datetime(df['Date'], dayfirst=True)

    # Make Date column the index
    df = df.set_index('Date')

    return df


def get_bcb_quote(start_period = None, end_period = None, series_code = 10813):
    """
    Access the Central Bank of Brazil database and return the requested quotes for the requested period
    (datetime)  start_period    : Start of date range
    (datetime)  end_period      : End of date range
    (int)       series_code     : Code for the requested series (https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries)
    """

    json    = _retrieve_json(start_period, end_period, series_code)
    df      = _json2pandas(json)
    return df

