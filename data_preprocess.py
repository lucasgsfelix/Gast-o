
import datetime
import pandas as pd
import numpy as np
import streamlit as st

from dateutil.relativedelta import relativedelta


def verify_surpassed_limit(value):

	if value:

		return 'red'

	return 'black'


def download_google_drive_sheet(link):

	link = "https://docs.google.com/spreadsheets/d/1iPDOgYOE6KL6FWMaToQ5fiQw5VtxbSyhSxDBLwLqiZ4/edit?usp=sharing"

	sheet_id = link.split('/')[-2]

	sheet_url = "https://docs.google.com/spreadsheets/d/" + sheet_id + "/edit#gid=0"

	url_1 = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')

	df = pd.read_table(url_1, sep=',', decimal=',')

	return df


@st.cache(allow_output_mutation=True, show_spinner=False)
def read_data(user_info, link=None):

	user_sheet = download_google_drive_sheet(link)

	user_sheet['Data'] = pd.to_datetime(user_sheet['Data'], format='%d/%m/%Y')

	user_sheet['Mês'] = user_sheet['Data'].dt.month

	return user_sheet


@st.cache(allow_output_mutation=True, show_spinner=False)
def define_user_data():

	user_data = {"User Name": "Lucas Félix", "User ID": 0, "Income": 8500, "Last Income": 8500,
				 "Budget Categories": {}, "Investiments": {}}


	return user_data


def define_limits_table(df, user_info):

	# visualization filters
	# by week, by month, by year, specific year, specific month

	# What info will be shown:
	# expenses per group
	category_mean = df.groupby('Categoria').mean()
	category_std = df.groupby('Categoria').std()
	category_sum = df.groupby('Categoria').sum()

	category_summary = category_mean.join(category_std, lsuffix=' std.')
	category_summary = category_summary.join(category_sum, lsuffix=' sum').reset_index()

	user_budget = pd.DataFrame(user_info["Budget Categories"].items(), columns=['Categoria', 'Limite'])

	limits_df = user_budget.set_index("Categoria").join(category_sum, how='outer')

	# filling quantia and limite
	limits_df = limits_df.fillna(0)

	# the sum of expenses is bigger than the budget?
	limits_df['Ultrapassou'] = limits_df['Quantia'] >= limits_df['Limite']

	limits_df['Color'] = limits_df['Ultrapassou'].apply(lambda value: verify_surpassed_limit(value))

	limits_df.reset_index(inplace=True)

	return limits_df


def mesuare_filtered_quanty(df, query, expenses=True, savings_categories=['Poupança', 'Investimentos']):
	"""
		If expenses, then do not consider the savings categories
		Else, only consider savings coluns

	"""

	if expenses:

		filtered_df = df[(query) & (~df['Categoria'].isin(savings_categories))]

	else:

		filtered_df = df[(query) & (df['Categoria'].isin(savings_categories))]

	return filtered_df['Quantia'].sum().round(2)


def measure_kpis(df):

	current_date = datetime.datetime.now()

	last_date = current_date - relativedelta(months=1)

	metrics = {
			    "Current Expenses": mesuare_filtered_quanty(df, (df['Data'].dt.year == current_date.year), True),
				"Current Savings": mesuare_filtered_quanty(df, (df['Data'].dt.year == current_date.year), False),
				"Last Expenses": mesuare_filtered_quanty(df, (df['Data'].dt.year == last_date.year - 1), True),
				"Last Savings": mesuare_filtered_quanty(df, (df['Data'].dt.year == last_date.year - 1), False),
				"Total Saved": 0
			  }


	metrics['Percentage Expend'] = (metrics['Current Expenses']/metrics['Last Expenses']) * 100
	metrics['Diff'] = np.abs(metrics['Current Expenses'] - metrics['Last Expenses']).round(2)

	monthly_metrics = {
					    "Current Expenses": mesuare_filtered_quanty(df, (df['Data'].dt.month == current_date.month) & (df['Data'].dt.year == current_date.year), True),
						"Current Savings": mesuare_filtered_quanty(df, (df['Data'].dt.month == current_date.month) & (df['Data'].dt.year == current_date.year), False),
						"Last Expenses": mesuare_filtered_quanty(df, (df['Data'].dt.month == last_date.month) & (df['Data'].dt.year == last_date.year), True),
						"Last Savings": mesuare_filtered_quanty(df, (df['Data'].dt.month == last_date.month) & (df['Data'].dt.year == last_date.year), False)
					  }

	monthly_metrics['Percentage Expend'] = (monthly_metrics['Current Expenses']/monthly_metrics['Last Expenses']) * 100
	monthly_metrics['Diff'] = np.abs(monthly_metrics['Current Expenses'] - monthly_metrics['Last Expenses']).round(2)


	return metrics, monthly_metrics
