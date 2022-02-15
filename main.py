"""

	Gastão: Sistema de controle de gastos

"""

import datetime

import pandas as pd
import numpy as np


import data_preprocess
import design
import visualization

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

	# pre-process the data
	# filtering by category
	visualize_df = og_df[og_df['Categoria'].isin(user_input['Selected Categories'])]

	# filtering by date
	visualize_df = visualize_df[(visualize_df['Data'].dt.date >= user_input['Plot Start Date']) &
								(visualize_df['Data'].dt.date <= user_input['Plot End Date'])]


	metrics, monthly_metrics = data_preprocess.measure_kpis(visualize_df)




	# main indicators
	#col1, col2, col3, col4 = st.columns(4)
	col1, _, col2 = st.columns((70, 5, 25))

	visualize_df = visualize_df.sort_values('Data')

	temporal_graph = px.line(visualize_df, x='Data', y="Quantia")

	col1.plotly_chart(temporal_graph, use_container_width=True)

	category_graph = px.histogram(visualize_df, x="Mês", y="Quantia", color='Categoria',
								  barmode='group', width=400,).update_layout(yaxis_title="Quantidade Gasta")

	col1.plotly_chart(category_graph, use_container_width=True)

	visualize_df['Data'] = visualize_df['Data'].dt.strftime('%d/%m/%Y')

	col1.dataframe(visualize_df, width=1000)

	
	# anual
	visualization.plot_kpis(metrics, "Anual", col2, user_data)

	# monthly
	visualization.plot_kpis(monthly_metrics, "Mensal", col2, user_data)

 
	with st.sidebar.expander("Qual é o limite de gasto para cada categoria?"):

		with st.form(key='categories'):

			info = {}

			start_time, end_time = st.columns(2)

			info['Category'] = st.selectbox("Categoria", user_input['Categories'])
			info['Budget'] = st.number_input("Limite de Gasto", min_value=0, value=500)

			st.form_submit_button()
