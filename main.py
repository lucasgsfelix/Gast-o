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

import pymongo
import urllib


def init_connection():


	client = pymongo.MongoClient("mongodb+srv://gastao_user:" + urllib.parse.quote_plus(st.secrets["mongo"]['password']) + "@gastao.n3j3j.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")


	db = client.test

	collection = db['gastao']

	return collection


@st.cache(allow_output_mutation=True, show_spinner=False)
def define_cache_variables():


	variables = {'valid': False, 'needed_input': {},
				 'established_connection': True}

	return variables


def insert_cache_variables(variables, key, new_variable):

	variables[key] = new_variable

	return variables


st.set_page_config(layout="wide", page_title="Gastão", page_icon="📊")

if __name__ == '__main__':

	print("First command")

	variables = define_cache_variables()

	print("Here?", variables['valid'])

	if variables['established_connection']:

		variables['collection'] = init_connection()

		variables['established_connection'] = False

	if variables['valid']:


		# User json format:
		# User name, User ID; Income (dict) - it can be several incomes;
		# Budget Categories (dict); Bank Account (dict); Investiments (dict)
		# Spreed Sheet: link

		design.remove_top_padding()

		og_df = variables['og_df']
		user_input = variables['user_input']

		og_df = data_preprocess.data_treatment(og_df)

		user_input['Change'] = False

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


		user_input['New Selected Categories'] = st.sidebar.multiselect("Quais categorias gostaria de analisar?", user_input['Categories'],
																   user_input['Categories'])

		user_input = data_preprocess.verify_change(user_input, 'Selected Categories', 'New Selected Categories')

		# pre-process the data
		# filtering by category
		visualize_df = og_df[og_df['Categoria'].isin(user_input['Selected Categories'])]

		# filtering by date
		visualize_df = visualize_df[(visualize_df['Data'].dt.date >= user_input['Plot Start Date']) &
									(visualize_df['Data'].dt.date <= user_input['Plot End Date'])]


		expenses_categories = visualize_df['Descrição'].unique().tolist() + user_input['Expenses']
		user_input['New Expenses'] = st.sidebar.multiselect("Quais são os seus gastos mensais?", expenses_categories,
																   user_input['Expenses'])

		user_input = data_preprocess.verify_change(user_input, 'Expenses', 'New Expenses')


		economy_categories = visualize_df['Categoria'].unique().tolist() + user_input['Savings']

		user_input['New Savings'] = st.sidebar.multiselect("Quais são suas categorias de economia?", economy_categories,
																   user_input['Savings'])

		user_input = data_preprocess.verify_change(user_input, 'Savings', 'New Savings')


		metrics, monthly_metrics = data_preprocess.measure_kpis(og_df, visualize_df, user_input['Income'], user_input['Savings'])

        # HERE: I have to add a update table button


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

				if 'Budget Categories' in user_input.keys():

					user_input['New Budget Categories'] = {**user_input['Budget Categories'], info['Categoria']: info['Limite']}


					user_input = data_preprocess.verify_change(user_input, 'Budget Categories', 'New Budget Categories')

				else:

					user_input['Budget Categories'] = {info['Categoria']: info['Limite']}



		col1.markdown("## Limite de gastos por categoria mensal:")

		limits_table = data_preprocess.define_limits_table(visualize_df, user_input)

		col1.dataframe(limits_table.drop(['Dividido', 'Mês', 'Ultrapassou', 'Color'], axis=1).style.highlight_max(axis=1), width=1000)

		if user_input['Change']:

			collection = variables['collection']

			user_input['Plot Start Date'] = str(user_input['Plot Start Date'])
			user_input['Plot End Date'] = str(user_input['Plot End Date'])

			collection.update_one({"email": user_input['email']}, {"$set": user_input}, True)

			user_input['Change'] = False


		user_input['new link'] = st.sidebar.text_input("Avaliar outra planilha do GoogleSheets!", '')

		update_sheet = st.sidebar.button("Atualizar planilha atual")

		if user_input['new link'] != '' or update_sheet:

			main_column = 'new link'

			if update_sheet:

				main_column = 'link'

			valid_execution, new_df = user_initial_page.treat_input_sheet(user_input, st.sidebar, main_column)

			variables['og_df'] = new_df

			if valid_execution:

				if not update_sheet:

					user_input = data_preprocess.verify_change(user_input, 'link', 'new link')

					user_input['new link'] = ''

				familiar_categories, _ = data_preprocess.retrieve_categories(new_df)

				og_df = data_preprocess.data_treatment(new_df)

				variables['og_df'] = og_df

				user_input['Expenses'] = familiar_categories['Expenses']

				user_input['Savings'] = familiar_categories['Savings']

				user_input['Income'] = familiar_categories['Income']

				variables['user_input'] = user_input


	else:


		user_input, og_df, variables['valid'], new_user = user_initial_page.define_user_inputs(variables['needed_input'],
																					 variables['collection'])

		if variables['valid']:
		
			variables = insert_cache_variables(variables, "og_df", og_df)
			variables = insert_cache_variables(variables, "user_input", user_input)

			collection = variables['collection']

			if new_user:

				collection.insert_one(variables['user_input'])

		