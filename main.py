"""

	Gastão: Sistema de controle de gastos

"""

import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
import numpy as np


import data_preprocess
import design

import streamlit as st
import plotly.express as px


if __name__ == '__main__':

	st.set_page_config(layout="wide")

	# User json format:
	# User name, User ID; Income (dict) - it can be several incomes;
	# Budget Categories (dict); Bank Account (dict); Investiments (dict)
	# Spreed Sheet: link

	user_data = {"User Name": "Lucas Félix", "User ID": 0, "Income": 8500, "Last Income": 8500,
				 "Budget Categories": {"Vestuário": 100, "Viagens": 200, "Eletrônicos": 200,
				 "Saúde": 100, "Outros": 100, "Casa": 200, "Educação": 200, "Alimentação": 400,
				 "Transporte": 300}, "Investiments": {}, "Spreed Sheet": 0}


	agg_df, og_df = data_preprocess.read_data(user_data)

	design.remove_top_padding()

	user_input = {}

	user_input['Plot Start Date'] = og_df['Data'].min()
	user_input['Plot End Date'] = og_df['Data'].max()
	user_input['Categories'] = og_df['Categoria'].unique()


	categories = og_df['Categoria'].unique()

	# sidebar infos
	#user_input['Income'][0] = st.sidebar.number_input(label="Qual é o seu salário?", value=1200, min_value=0)

	user_input['Plot Start Date'] = st.sidebar.date_input(label="Data de início da análise",
														 value=user_input['Plot Start Date'],
														 min_value=user_input['Plot Start Date'],
														 max_value=user_input['Plot End Date'])

	user_input['Plot End Date'] = st.sidebar.date_input(label="Data final da análise",
													    value=user_input['Plot End Date'],
													    min_value=user_input['Plot Start Date'],
														max_value=user_input['Plot End Date'])


	user_input['Selected Categories'] = st.sidebar.multiselect("Quais categorias gostaria de analisar?", user_input['Categories'],
															   user_input['Categories'])

	#print(og_df.shape)
	# pre-process the data
	# filtering by category
	visualize_df = og_df[og_df['Categoria'].isin(user_input['Selected Categories'])]

	# filtering by date
	visualize_df = visualize_df[(visualize_df['Data'].dt.date >= user_input['Plot Start Date']) &
								(visualize_df['Data'].dt.date <= user_input['Plot End Date'])]

	# will be a user input
	investiments_category = ['Investimentos', 'Poupança']

	current_date = datetime.datetime.now()

	# current year data
	year_df = visualize_df[visualize_df['Data'].dt.year == current_date.year]

	# what are the expenses in relation what was expend next year in the same period
	last_year_df = visualize_df[(visualize_df['Data'].dt.year == current_date.year - 1) &
								(visualize_df['Data'].dt.month <= year_df['Data'].dt.month.max())]

	metrics = {"Current Year Expenses": year_df[~year_df['Categoria'].isin(investiments_category)]['Quantia'].sum().round(2),
			   "Last Year Expenses": last_year_df[~last_year_df['Categoria'].isin(investiments_category)]['Quantia'].sum().round(2),
			   "Current Savings": year_df[year_df['Categoria'].isin(investiments_category)]['Quantia'].sum().round(2),
			   "Last Year Savings": last_year_df[last_year_df['Categoria'].isin(investiments_category)]['Quantia'].sum().round(2),
			   "Total Saved": visualize_df['Quantia'].sum().round(2)}

	metrics['Expenses Color'] = "inverse" if metrics['Current Year Expenses'] >= metrics['Last Year Expenses'] else "normal"

	# if last year is bigger than current it means that you are saving money
	metrics['Expenses Delta'] = metrics['Last Year Expenses'] - metrics['Current Year Expenses']

	


	# main indicators
	#col1, col2, col3, col4 = st.columns(4)

	col1, _, col2 = st.columns((70, 5, 25))


	temporal_graph = px.line(visualize_df, x='Data', y="Quantia")

	col1.plotly_chart(temporal_graph, use_container_width=True)

	category_graph = px.histogram(visualize_df, x="Mês", y="Quantia", color='Categoria',
								  barmode='group', width=400,).update_layout(yaxis_title="Quantidade Gasta")

	col1.plotly_chart(category_graph, use_container_width=True)

	col2.header('Anual:')

	col2.metric('Salário ', str(user_data['Income'] * current_date.month))

	col2.metric("Gasto:", "R$ " + str(metrics['Current Year Expenses']),
				"R$ " + str(metrics['Last Year Expenses']),
				delta_color=metrics['Expenses Color'])

	if metrics['Expenses Delta'] > 0:

		# the delta will be compared to the last month
		col2.metric("Economizado:", metrics['Last Year Expenses']/metrics['Current Year Expenses'])

	else:

		col2.metric("Gasto a mais:", metrics['Last Year Expenses']/metrics['Current Year Expenses'])

	col2.metric("Poupança & Investimentos: ", "R$ " + str(metrics['Current Savings']),
											  "R$ " + str(metrics['Last Year Savings']))


	col2.header('Mensal:')
	col2.metric('Salário ', "R$ " + str(user_data['Income']))

	last_date = current_date - relativedelta(months=1)

	# year month df expenses df
	monthly_metrics = {
						    "Current Expenses": data_preprocess.mesuare_filtered_quanty(visualize_df, (visualize_df['Data'].dt.month == current_date.month) &
												(visualize_df['Data'].dt.year == current_date.year), True),
							"Current Savings": data_preprocess.mesuare_filtered_quanty(visualize_df, (visualize_df['Data'].dt.month == current_date.month) &
												(visualize_df['Data'].dt.year == current_date.year), False),
							"Last Expenses": data_preprocess.mesuare_filtered_quanty(visualize_df, (visualize_df['Data'].dt.month == last_date.month) &
												(visualize_df['Data'].dt.year == last_date.year), True),
							"Last Savings": data_preprocess.mesuare_filtered_quanty(visualize_df, (visualize_df['Data'].dt.month == last_date.month) &
												(visualize_df['Data'].dt.year == last_date.year), False)
					  }


	monthly_metrics['Percentage Expend'] = (monthly_metrics['Current Expenses']/monthly_metrics['Last Expenses']) * 100
	monthly_metrics['Diff'] = np.abs(monthly_metrics['Current Expenses'] - monthly_metrics['Last Expenses']).round(2)


	if monthly_metrics['Percentage Expend'] < 100:

		# the delta will be compared to the last month
		col2.metric("Economizado:",  "R$ " + str((monthly_metrics['Diff'])), str(monthly_metrics['Percentage Expend'].round(2)) + '%')

	else:

		col2.metric("Gasto a mais:", "R$ " + (monthly_metrics['Diff']), str(monthly_metrics['Percentage Expend'].round(2)) + '%')


	visualize_df['Data'] = visualize_df['Data'].dt.strftime('%d/%m/%Y')

	col1.dataframe(visualize_df, width=1000)



 

