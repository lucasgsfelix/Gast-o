import datetime
import streamlit as st


def plot_kpis(metrics, header, column, user_data):

	mult = 1

	if header.lower() == 'anual':

		current_date = datetime.datetime.now()

		mult = current_date.month


	column.header(header + ':')

	column.metric('Salário ', str(user_data['Income'] * mult))

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

		column.header("Contas pagas no mês " + str(current_month))

		monthly_data = user_data[user_data['Mês'] == current_month]

		paid_expenses = monthly_data['Categoria'].tolist() + monthly_data['Descrição'].tolist()

		paid_expenses = list(map(lambda expense: expense.lower(), paid_expenses))

		for expense in expenses:

			if not expense.lower() in paid_expenses:

				column.markdown('### :no_entry_sign: ' + expense.title())


		for expense in expenses:

			if expense.lower() in paid_expenses:

				column.markdown('### :white_check_mark: ' + expense.title())
