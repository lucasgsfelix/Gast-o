
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

	sheet_id = link.split('/')[-2]

	sheet_url = "https://docs.google.com/spreadsheets/d/" + sheet_id + "/edit#gid=0"

	url_1 = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')

	df = pd.read_table(url_1, sep=',', decimal=',')

	return df


@st.cache(allow_output_mutation=True, show_spinner=False)
def define_credit_card_expenses(user_sheet):

	user_sheet['Dividido'] = user_sheet['Dividido'].fillna(1)

	mode_columns = 'Modalidade (Cŕedito/Pix/Débito/Boleto)'

	credit_expenses = user_sheet[user_sheet[mode_columns] == 'Crédito']

	credit_expenses['Quantia'] = credit_expenses['Quantia']/credit_expenses['Dividido']

	credit_expenses['Data'] = pd.to_datetime(credit_expenses['Data'], format="%d/%m/%Y")

	treated_expenses = []

	# cumsum of the divided per index
	for index in credit_expenses.index:

		one_expense = credit_expenses[credit_expenses.index == index]

		if one_expense['Dividido'].max() > 1:


			# one dataframe repeated several times, one per time that was divided that bill
			expense = pd.concat([one_expense for _ in range(0, int(one_expense['Dividido'].max()))]).reset_index()

			expense.index = expense.index + 1

			expense['Descrição'] = expense['Descrição'] + ' ' + expense.index.astype(str) + '/' + str(expense.index.max())

			expense['Relative Months'] = list(map(lambda x: relativedelta(months=x), expense.index))


			expense['Data'] = expense.apply(lambda row: row['Data'] + row['Relative Months'], axis=1)

			expense = expense.drop(['Relative Months'], axis=1)


		else:


			expense = one_expense

		treated_expenses.append(expense)

	credit_expenses = pd.concat(treated_expenses)

	credit_expenses['Dividido'] = 1

	# removing that total expense em dividing it in minor expenses
	user_sheet = user_sheet[user_sheet[mode_columns] != 'Crédito']

	return user_sheet.append(credit_expenses).reset_index(drop=True)



@st.cache(allow_output_mutation=True, show_spinner=False)
def read_data(user_info, link):

	user_sheet = download_google_drive_sheet(link)

	user_sheet['Data'] = pd.to_datetime(user_sheet['Data'], format='%d/%m/%Y')

	user_sheet = define_credit_card_expenses(user_sheet)

	user_sheet['Mês'] = user_sheet['Data'].dt.month

	user_sheet['Dividido'] = user_sheet['Dividido'].astype(int)

	return user_sheet


@st.cache(allow_output_mutation=True, show_spinner=False)
def define_user_data():

	user_data = {"User Name": "Lucas Félix", "User ID": 0, "Income": 0, "Last Income": 0,
				 "Budget Categories": {}, "Investiments": {}}


	return user_data


def define_limits_table(df, user_info):

	# visualization filters
	# by week, by month, by year, specific year, specific month

	current_month = datetime.datetime.now().month

	df = df[df['Mês'] == current_month]

	# What info will be shown:
	# expenses per group
	category_mean = df.groupby('Categoria').mean()
	category_std = df.groupby('Categoria').std()
	category_sum = df.groupby('Categoria').sum()

	category_summary = category_mean.join(category_std, lsuffix=' std.')
	category_summary = category_summary.join(category_sum, lsuffix=' sum').reset_index(drop=True)

	user_budget = pd.DataFrame(user_info["Budget Categories"].items(), columns=['Categoria', 'Limite'])

	limits_df = user_budget.set_index("Categoria").join(category_sum, how='outer')

	# filling quantia and limite
	limits_df = limits_df.fillna(0)

	# the sum of expenses is bigger than the budget?
	limits_df['Ultrapassou'] = limits_df['Quantia'] >= limits_df['Limite']

	limits_df['Color'] = limits_df['Ultrapassou'].apply(lambda value: verify_surpassed_limit(value))

	limits_df.reset_index(inplace=True)

	return limits_df.drop(columns=['index'], axis=1, errors='ignore')


def measure_filtered_quanty(df, query, expenses, savings_categories):
	"""
		If expenses, then do not consider the savings categories
		Else, only consider savings coluns

	"""

	if expenses:

		filtered_df = df[(query) & (~df['Categoria'].isin(savings_categories))]

	else:

		filtered_df = df[(query) & (df['Categoria'].isin(savings_categories))]

	return filtered_df['Quantia'].sum().round(2)


def measure_income(og_df, income_columns, header):

	if header.lower() == 'anual':

		income = og_df[og_df['Categoria'].isin(income_columns)]['Quantia'].sum()

	else:

		current_month = datetime.datetime.now().month

		income = og_df[(og_df['Categoria'].isin(income_columns)) &
						(og_df['Mês'] == current_month)]['Quantia'].sum()

	return round(income, 2)


def measure_kpis(og_df, df, income_columns, savings_columns):

	current_date = datetime.datetime.now()

	last_date = current_date - relativedelta(months=1)

	mode_columns = 'Modalidade (Cŕedito/Pix/Débito/Boleto)'


	# What if: The user pays his credit card with another credit card?
	df = df[df[mode_columns] != 'Crédito']


	metrics = {
			    "Current Expenses": measure_filtered_quanty(df, (df['Data'].dt.year == current_date.year), True, savings_columns),
				"Current Savings": measure_filtered_quanty(og_df, (og_df['Data'].dt.year == current_date.year), False, savings_columns),
				"Last Expenses": measure_filtered_quanty(df, (df['Data'].dt.year == last_date.year - 1), True, savings_columns),
				"Last Savings": measure_filtered_quanty(og_df, (og_df['Data'].dt.year == last_date.year - 1), False, savings_columns),
				"Total Saved": 0
			  }


	income = df[df['Categoria'].isin(income_columns)]['Quantia'].sum()

	metrics['Percentage Expend'] = (metrics['Current Expenses']/metrics['Last Expenses']) * 100

	income = measure_income(og_df, income_columns, 'anual')

	metrics['Diff'] = (income - metrics['Current Expenses'] - metrics["Current Savings"]).round(2)


	monthly_metrics = {
					    "Current Expenses": measure_filtered_quanty(df, (df['Data'].dt.month == current_date.month) &
					    												(df['Data'].dt.year == current_date.year), True, savings_columns),
						"Current Savings": measure_filtered_quanty(og_df, (og_df['Data'].dt.month == current_date.month) &
																	   (og_df['Data'].dt.year == current_date.year), False, savings_columns),
						"Last Expenses": measure_filtered_quanty(df, (df['Data'].dt.month == last_date.month) &
																(df['Data'].dt.year == last_date.year), True, savings_columns),
						"Last Savings": measure_filtered_quanty(og_df, (og_df['Data'].dt.month == last_date.month) &
																	   (og_df['Data'].dt.year == last_date.year), False, savings_columns)
					  }

	income = measure_income(og_df, income_columns, 'mensal')

	monthly_metrics['Percentage Expend'] = (monthly_metrics['Current Expenses']/monthly_metrics['Last Expenses']) * 100
	monthly_metrics['Diff'] = (income - monthly_metrics['Current Expenses'] - monthly_metrics["Current Savings"]).round(2)


	return metrics, monthly_metrics
