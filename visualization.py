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



