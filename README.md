# pyget_online_data

Python library of functions to get data from online sources. 

The method to obtain the information (webscrapping, API requests, etc) is transparent to the user. The return data format depends on the data itself but a the following is preferred:
* pandas dataframe for time series like exchange quotes over a period
* dictionary for everything else like weather forecast data for 1 day

These are the functions implemented so far:
1. get_bcb_quote: retrieve data series from the Central Bank of Brazil. Example: daily quotes for US dollars to Brazilian reais exchange rates
2. get_ecb_quote: retrieve data series from the European Central Bank. Example: daily quotes for Euros to US dollars exchange rates

Some examples included:
1. Helper script and spreadsheets for doing the exchange rate conversion of income and assets from Belgium for the tax declaration for Brazilian tax authority.
