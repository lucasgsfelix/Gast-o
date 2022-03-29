import datetime
import pandas as pd
import streamlit as st


def plot_kpis(metrics, header, column, og_df, income_columns):

	if header.lower() == 'anual':

		income = og_df[og_df['Categoria'].isin(income_columns)]['Quantia'].sum()

	else:

		current_month = datetime.datetime.now().month

		income = og_df[(og_df['Categoria'].isin(income_columns)) &
						(og_df['Mês'] == current_month)]['Quantia'].sum()


	column.header(header + ':')

	column.metric('Salário ', str(income))

	column.metric("Gasto:", "R$ " + str(metrics['Current Expenses']), "R$ " + str(metrics['Last Expenses']))

	if metrics['Percentage Expend'] < 100:

		# the delta will be compared to the last month
		column.metric("Economizado:",  "R$ " + str((metrics['Diff'])), str(metrics['Percentage Expend'].round(2)) + '%')

	else:

		column.metric("Gasto a mais:", "R$ " + str(metrics['Diff']), str(metrics['Percentage Expend'].round(2)) + '%')

	column.metric("Poupança & Investimentos: ", "R$ " + str(metrics['Current Savings']), "R$ " + str(metrics['Last Savings']))


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





