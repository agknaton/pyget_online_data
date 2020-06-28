#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch official exchange rate quote for a given period from European Central Bank into a pandas dataframe

consider for header style upgrade: https://medium.com/@rukavina.andrei/how-to-write-a-python-script-header-51d3cec13731
"""

import requests
import pandas
import xmltodict
import datetime

_ENTRYPOINT    = 'https://sdw-wsrest.ecb.europa.eu/service/'    # Using protocol 'https'
_RESOURCE      = 'data'                                         # The resource for data is 'data'
_FLOW_REF      = 'EXR'                                          # Defines exchange rates as data to returned


def _retrieve_xml (
    start_period    = None, 
    end_period      = None, 
    curr_meas_key   = 'USD', 
    curr_base_key   = 'EUR', 
    freq_key        = 'D', 
    series_var_key  = 'A'):
    """
    Get XML with required data
    (datetime)  start_period    : Start of date range
    (datetime)  end_period      : End of date range
    (char)      freq_key        : the frequency at which they are measured (e.g.: on a daily basis - code D)
    (string)    curr_meas_key   : the currency being measured (e.g.: US dollar - code USD)
    (string)    curr_base_key   : the currency against which a currency is being measured (e.g.: Euro - code EUR)
    (char)      series_var_key  : the series variation (such as average or standardised measure for given frequency, code A)
    """

    # Get start_period = today - ~1 year and end_period = today if undefined
    if end_period is None:
        end_period = datetime.date.today()
    if start_period is None:
        start_period = end_period - datetime.timedelta(days = 365)
    if start_period > end_period:
        start_period = end_period

    # Construct query key
    type_key = 'SP00'           # the type of exchange rates (Foreign exchange reference rates - code SP00) 
    key = ".".join([freq_key, curr_meas_key, curr_base_key, type_key, series_var_key])

    # Construct the URL: https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.CHF.EUR.SP00.A
    request_url = _ENTRYPOINT + _RESOURCE + '/' + _FLOW_REF + '/' + key

    # Put parameters together in the request format
    parameters = {
        'startPeriod'   : start_period.strftime("%Y-%m-%d"),
        'endPeriod'     : end_period.strftime("%Y-%m-%d")
    }

    # Make the HTTP request
    response = requests.get(request_url, params=parameters)
    
    # Check if the response returns succesfully with response code 200
    if response.status_code != 200:
        raise Exception("Query failed")
    
    # Return the XML reply
    return response.text


def _xml2pandas(in_xml):
    """
    Convert the XML response from ECB to a pandas dataframe with date index
    """

    # Convert XML to dictionary
    in_dict     = xmltodict.parse(in_xml)

    # Extract Series
    series_dict = in_dict['message:GenericData']['message:DataSet']['generic:Series']

    # Extract observed data and key information from full dictionary
    obs_lst     = series_dict['generic:Obs']
    key_lst     = series_dict['generic:SeriesKey']['generic:Value']

    # Parse observed data to dictionary formatted as {date: observed_value} with a list comprehension
    obs_dict    = {
        data_point['generic:ObsDimension']['@value'] : float(data_point['generic:ObsValue']['@value']) 
        for data_point in obs_lst
    } 

    # Parse relevant information from key_lst and create column name
    key_dict    = {
        id_value['@id'] : id_value['@value']
        for id_value in key_lst
    }
    col_name = key_dict['CURRENCY'] + '/' + key_dict['CURRENCY_DENOM']

    # Convert dictionary to pandas dataframe with date as index
    df = pandas.DataFrame(obs_dict.items(), columns = ['Date', col_name])
    df['Date'] = pandas.to_datetime(df['Date'])
    df = df.set_index('Date')
    return df


def get_ecb_quote(start_period = None, end_period = None, curr_meas_key = 'USD', curr_base_key = 'EUR'):
    """
    Access the European Central Bank database and return the requested exchange rates for the requested period
    (datetime)  start_period    : Start of date range
    (datetime)  end_period      : End of date range
    (char)      freq_key        : the frequency at which they are measured (e.g.: on a daily basis - code D)
    (string)    curr_meas_key   : the currency being measured (e.g.: US dollar - code USD)
    (string)    curr_base_key   : the currency against which a currency is being measured (e.g.: Euro - code EUR)
    """

    xml = _retrieve_xml(start_period, end_period, curr_meas_key, curr_base_key)
    df  = _xml2pandas(xml)
    return df

