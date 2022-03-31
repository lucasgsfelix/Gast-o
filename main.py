"""

	Gastão: Sistema de controle de gastos

"""

import datetime

import pandas as pd
import numpy as np


import data_preprocess
import design
import visualization
import user_initial_page

import streamlit as st
import plotly.express as px


@st.cache(allow_output_mutation=True, show_spinner=False)
def define_cache_variables():


	variables = {'valid': False, 'needed_input': {}}

	return variables


def insert_cache_variables(variables, key, new_variable):

	variables[key] = new_variable

	return variables

if __name__ == '__main__':

	st.set_page_config(layout="wide", page_title="Gastão", page_icon="📊")

	#login.login_page()

	variables = define_cache_variables()

	if not variables['valid']:

		user_input, og_df, variables['valid'] = user_initial_page.define_user_inputs(needed_input=variables['needed_input'])

		if variables['valid']:
		
			variables = insert_cache_variables(variables, "og_df", og_df)
			variables = insert_cache_variables(variables, "user_input", user_input)


	else:

		# User json format:
		# User name, User ID; Income (dict) - it can be several incomes;
		# Budget Categories (dict); Bank Account (dict); Investiments (dict)
		# Spreed Sheet: link

		design.remove_top_padding()

		og_df = variables['og_df']
		user_input = variables['user_input']

		og_df = data_preprocess.data_treatment(og_df)

		user_data = data_preprocess.define_user_data()

		#	og_df = data_preprocess.read_data(user_data, user_input['link'])

		user_input['Plot Start Date'] = og_df['Data'].min()
		user_input['Plot End Date'] = og_df['Data'].max()
		user_input['Categories'] = og_df['Categoria'].unique()


		user_input['Categories'] = list(filter(lambda category: (category not in user_input['Savings']) and
																(category not in user_input['Income']), user_input['Categories']))

		categories = og_df['Categoria'].unique()


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


		expenses_categories = visualize_df['Descrição'].unique().tolist() + user_input['Expenses']
		user_input['Expenses'] = st.sidebar.multiselect("Quais são os seus gastos mensais?", expenses_categories,
																   user_input['Expenses'])


		economy_categories = visualize_df['Categoria'].unique().tolist() + user_input['Savings']

		user_input['Savings'] = st.sidebar.multiselect("Quais são suas categorias de economia?", economy_categories,
																   user_input['Savings'])


		metrics, monthly_metrics = data_preprocess.measure_kpis(og_df, visualize_df, user_input['Income'], user_input['Savings'])


		## What are your monthly costs? Luz, aluguel, internet, condomínio, celular


		# main indicators
		#col1, col2, col3, col4 = st.columns(4)
		col1, subcol, col2 = st.columns((70, 5, 25))

		visualize_df = visualize_df.sort_values('Data')

		col1.markdown("## Visualização temporal de gastos:")

		temporal_graph = px.line(visualize_df, x='Data', y="Quantia")

		col1.plotly_chart(temporal_graph, use_container_width=True)

		category_graph = px.histogram(visualize_df, x="Mês", y="Quantia", color='Categoria',
									  barmode='group', width=400,).update_layout(yaxis_title="Quantidade Gasta")

		col1.markdown("## Gastos por categoria:")

		col1.plotly_chart(category_graph, use_container_width=True)

		visualize_df['Data'] = visualize_df['Data'].dt.strftime('%d/%m/%Y')

		col1.markdown("## Gastos:")

		col1.dataframe(visualize_df.drop(['Mês', 'index'], axis=1, errors='ignore'), width=1000)

		
		# anual
		visualization.plot_kpis(metrics, "Anual", col2, og_df, user_input['Income'])

		# monthly
		visualization.plot_kpis(monthly_metrics, "Mensal", col2, og_df, user_input['Income'])


		visualization.plot_paid_monthly_expensives(visualize_df, col2, user_input['Expenses'])


		visualization.expenses_to_come(visualize_df, col2, user_input['Savings'])

	 
		with st.sidebar.expander("Qual é o limite de gasto para cada categoria?"):

			with st.form(key='categories'):

				info = {}

				info['Categoria'] = st.selectbox("Categoria", user_input['Categories'])
				info['Limite'] = st.number_input("Limite de Gasto", min_value=0, value=500)

				st.form_submit_button()

				user_data['Budget Categories'] = {**user_data['Budget Categories'], info['Categoria']: info['Limite']}


		col1.markdown("## Limite de gastos por categoria mensal:")

		limits_table = data_preprocess.define_limits_table(visualize_df, user_data)

		col1.dataframe(limits_table.drop(['Dividido', 'Mês', 'Ultrapassou', 'Color'], axis=1).style.highlight_max(axis=1), width=1000)


