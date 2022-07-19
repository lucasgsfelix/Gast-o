import datetime
import pandas as pd
import streamlit as st

import data_preprocess
from dateutil.relativedelta import relativedelta


def plot_kpis(metrics, header, column, og_df, income_columns):


	income = data_preprocess.measure_income(og_df, income_columns, header)

	column.header(header + ':')

	column.metric('Salário ', str(income.round(2)))

	column.metric("Gasto:", "R$ " + str(metrics['Current Expenses']), "R$ " + str(metrics['Last Expenses']))

	if metrics['Percentage Expend'] < 100:

		# the delta will be compared to the last month
		column.metric("Economizado:",  "R$ " + str(round(metrics['Diff'], 2)), str(metrics['Percentage Expend'].round(2)) + '%')

	else:

		column.metric("Gasto a mais:", "R$ " + str(round(metrics['Diff'], 2)), str(metrics['Percentage Expend'].round(2)) + '%')

	column.metric("Poupança & Investimentos: ", "R$ " + str(metrics['Current Savings']), "R$ " + str(metrics['Last Savings']))



def plot_biweekly_expenses(column, df):


	# expenses dataframe
	current_day = datetime.datetime.now()

	last_biweek = datetime.datetime.now() - relativedelta(days=15)

	last_biweek_expenses = df[(df['Data'] >= last_biweek) & (df['Data'] <= current_day)]['Quantia'].sum()

	# last month data
	total_expenses_last_month = df[df['Mês'] == current_day.month - 1]['Quantia'].sum()

	total_expenses = df[df['Mês'] == current_day.month]['Quantia'].sum()

	df['Dia'] = df['Data'].dt.day

	df['Ano'] = df['Data'].dt.year

	first_biweek_last_month = df[(df['Mês'] == current_day.month - 1) & (df['Dia'] <= 15)]['Quantia'].sum()

	second_biweek_last_month = df[(df['Mês'] == current_day.month - 1) & (df['Dia'] > 15)]['Quantia'].sum()

	mean_expenses_first_biweek = df[(df['Ano'] == current_day.year) & (df['Dia'] <= 15)]['Quantia'].sum()/len(df['Mês'].unique())

	mean_expenses_second_biweek = df[(df['Ano'] == current_day.year) & (df['Dia'] > 15)]['Quantia'].sum()/len(df['Mês'].unique())

	column.header('Avaliação quinzenal:')

	column.metric("Gasto nos últimos 15 dias: ", "R$" + str(round(last_biweek_expenses, 2)))

	column.metric("Gasto total 1ª quinzena mês anterior: ", "R$" + str(round(first_biweek_last_month, 2)))

	column.metric("Gasto total 2ª quinzena mês anterior: ", "R$" + str(round(second_biweek_last_month, 2)))

	column.metric("Gasto médio 1ª quinzena do mês: ", "R$" + str(round(mean_expenses_first_biweek, 2)))

	column.metric("Gasto médio 2ª quinzena do mês: ", "R$" + str(round(mean_expenses_second_biweek, 2)))

	column.metric("Gasto total no último mês: ", "R$" + str(round(total_expenses_last_month, 2)))

	column.metric("Gasto total mês atual: ", "R$" + str(round(total_expenses, 2)))



def plot_paid_monthly_expensives(user_data, column, expenses):

	# there most be some expenses indexed by the users

	if len(expenses):

		current_month = datetime.datetime.now().month

		column.header("Contas pagas no mês " + str(current_month) + ":")

		monthly_data = user_data[user_data['Mês'] == current_month]

		paid_expenses = monthly_data['Categoria'].tolist() + monthly_data['Descrição'].tolist()

		paid_expenses = list(map(lambda expense: expense.lower(), paid_expenses))

		for expense in expenses:

			if not expense.lower() in paid_expenses:

				column.markdown('### :no_entry_sign: ' + expense.title())


		for expense in expenses:

			if expense.lower() in paid_expenses:

				column.markdown('### :white_check_mark: ' + expense.title())



def expenses_to_come(user_data, column, savings_categories):

	# define the expenses that will come

	user_data['Data Datetime'] = pd.to_datetime(user_data['Data'], format='%d/%m/%Y')

	future_expenses = user_data[(user_data['Data Datetime'] >= datetime.datetime.now()) &
								~(user_data['Categoria'].isin(savings_categories))]

	column.header("Contas agendadas: ")

	index = 0

	for expense, date, value in future_expenses[['Descrição', 'Data', 'Quantia']].values:

		column.markdown('### :large_blue_circle: ' + ' - '.join([expense.title(), str(date), "R$" + str(value)]))

		index += 1


		if index > 5:

			break

	if index > 5:

		column.markdown("### :red_circle: Existem outras despesas futuras que não foram apresentadas!")





