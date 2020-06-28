#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update EUR/USD and USD/BRL quotes on the excel spreadsheet with salaries
"""

import sys, datetime, openpyxl

sys.path.insert(0, '../')

import pyget_online_data

EXCEL_SALARY_FILENAME = './brazilian_taxes_belgian_income_salary.xlsx'
EXCEL_BANK_FILENAME = './brazilian_taxes_belgian_income_assets.xlsx'
TAX_YEAR = 2019

# Fetch quotes for declaration year
start_period    = datetime.date(TAX_YEAR - 1, 12, 1)
end_period      = datetime.date(TAX_YEAR, 12, 31) 

df_usd_eur = pyget_online_data.get_ecb_quote(start_period, end_period, 'USD', 'EUR')
df_brl_usd = pyget_online_data.get_bcb_quote(start_period, end_period, 10813)
df_brl_eur = pyget_online_data.get_bcb_quote(start_period, end_period, 21620)

"""
UPDATE QUOTES IN THE SALARY EXCEL SPREADSHEET
"""
# open sheet
workbook = openpyxl.load_workbook(EXCEL_SALARY_FILENAME)
sheet = workbook['irpf']

# loop over rows and update quotes
for i in range(12):
    row = 3 + i
    # Date of USD/EUR quote (last work day of month)
    date = df_usd_eur[:'{:04}-{:02}'.format(TAX_YEAR, i+1)].index[-1]
    sheet.cell(row, 2).value = date

    # USD/EUR quote for that date
    value = df_usd_eur[:'{:04}-{:02}'.format(TAX_YEAR, i+1)]['USD/EUR'][-1]
    sheet.cell(row, 3).value = value

    # Date of BRL/USD quote (last work day of the first half of the previous month)
    year  = TAX_YEAR - 1
    month = 12 + i
    if month > 12:
        year  += 1
        month %= 12
    date = df_brl_usd[:'{:04}-{:02}-{}'.format(year, month, 15)].index[-1]
    sheet.cell(row, 4).value = date

    # BRL/USD quote for that date
    value = df_brl_usd[:'{:04}-{:02}-{}'.format(year, month, 15)]['value'][-1]
    sheet.cell(row, 5).value = value

# Save salary excel sheet
workbook.save(EXCEL_SALARY_FILENAME)

# Close file
workbook.close() 


"""
UPDATE QUOTE IN THE BANK BALANCES SPREADSHEET
"""
# open sheet
workbook = openpyxl.load_workbook(EXCEL_BANK_FILENAME)
sheet = workbook['Sheet1']

# update dates (last working day of year)
date0 = df_brl_eur[:'{:04}-{:02}-{}'.format(TAX_YEAR - 1, 12, 31)].index[-1]
date1 = df_brl_eur[:'{:04}-{:02}-{}'.format(TAX_YEAR, 12, 31)].index[-1]
sheet['B2'].value = date0
sheet['B3'].value = date1

# update quotes
sheet['C2'].value = df_brl_eur[date0:date0]['value'][-1]
sheet['C3'].value = df_brl_eur[date1:date1]['value'][-1]

# Save bank balances excel sheet
workbook.save(EXCEL_BANK_FILENAME)

# Close file
workbook.close() 


