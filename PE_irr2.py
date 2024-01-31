import streamlit as st
import pandas as pd
from scipy.optimize import fsolve
import numpy as np
import datetime as dt

def npv(irr, cfs, yrs):  
    return np.sum(cfs / (1. + irr) ** yrs)

def irr(cfs, yrs, x0, **kwargs):
    return fsolve(npv, x0=x0, args=(cfs, yrs), **kwargs)
###########################

def csv_irr (df, initial_irr):
	date_column_by_index = df.iloc[:, 0]
	casflow_column_by_index = df.iloc[:, 1]

	#  extract the cash flow from the second column.  Address the different format of cashflow, such $, 
	casflow_column_by_index =casflow_column_by_index.str.replace('[$,)]','', regex=True)
	casflow_column_by_index =casflow_column_by_index.str.replace('[(]','-', regex=True)
	cash_flow = [float(x) for x in casflow_column_by_index.values]

	####   the following section process the date time column of the csv file
	dateList = date_column_by_index		#  -------- these two are the same, need to be factored. 
	valueDate = dateList[0]   # --- IRR cal starting date
	vDate = dt.datetime.strptime(valueDate, '%m/%d/%Y') 
	years_passed =[]

	for i in range (len(dateList)):
		current = dt.datetime.strptime(dateList[i], '%m/%d/%Y') 
		# print ('date :', i, current)
		difference = current-vDate
		d_in_years = difference.days /365.25
		years_passed.append (d_in_years)
		# print ('difference in terms =', d_in_years)

	years_ago = np.array (years_passed)

	initial_irr = float (initial_irr)
	xirr = irr(cash_flow, years_ago, x0=initial_irr, maxfev=10000)
	return xirr[0]

#### the following is the Streamlit UI 

st.subheader ("IRR calculate demo :wave:")
st.info ("This web application is designed to calculate the Internal Rate of Return (IRR) for your financial data. You can upload your data in a CSV file format from your computer. The first column of the CSV should contain the dates of your cash flows. The second column contains the cash flow for each corresponding date. The last row contain the valuation date and the net asset value (NAV) and this tool will handle the calculations.")

file = st.file_uploader('upload your CSV file')

a,b,c = st.columns ([1,1,1])

with c:
	inital_estimate = st.text_input ('Estimated IRR', '0.1')
	cal_button = st.button ('Calculate')

if file and cal_button:
	df = pd.read_csv (file)
	xirr = csv_irr (df, inital_estimate)*100
	result = 'IRR = ' + str(round (xirr, 2)) +" %"
	st.subheader (result)
	st.dataframe(df)
	df.to_csv ('sourcedate_temp.csv')


