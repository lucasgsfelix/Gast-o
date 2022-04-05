"""

	Gastão: Sistema de controle de gastos

"""

import datetime

import pandas as pd
import numpy as np

import random


import data_preprocess
import design
import visualization
import user_initial_page


import SessionState

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


	session_state = SessionState.get(variables=define_cache_variables(), user_id=random.uniform(0, 100000))

	if session_state.variables['established_connection']:

		session_state.variables['collection'] = init_connection()

		session_state.variables['established_connection'] = False

	if session_state.variables['valid']:


		# User json format:
		# User name, User ID; Income (dict) - it can be several incomes;
		# Budget Categories (dict); Bank Account (dict); Investiments (dict)
		# Spreed Sheet: link

		design.remove_top_padding()

		session_state.og_df = session_state.variables['og_df']
		session_state.user_input = session_state.variables['user_input']

		session_state.og_df = data_preprocess.data_treatment(session_state.og_df)

		session_state.user_input['Change'] = False

		#	og_df = data_preprocess.read_data(user_data, user_input['link'])

		session_state.user_input['Plot Start Date'] = session_state.og_df['Data'].min()
		session_state.user_input['Plot End Date'] = session_state.og_df['Data'].max()
		session_state.user_input['Categories'] = session_state.og_df['Categoria'].unique()


		session_state.user_input['Categories'] = list(filter(lambda category: (category not in session_state.user_input['Savings']) and
																(category not in session_state.user_input['Income']),
																session_state.user_input['Categories']))

		session_state.categories = session_state.og_df['Categoria'].unique()


		session_state.user_input['Plot Start Date'] = st.sidebar.date_input(label="Data de início da análise",
															 value=session_state.user_input['Plot Start Date'],
															 min_value=session_state.user_input['Plot Start Date'],
															 max_value=session_state.user_input['Plot End Date'])

		session_state.user_input['Plot End Date'] = st.sidebar.date_input(label="Data final da análise",
														    value=session_state.user_input['Plot End Date'],
														    min_value=session_state.user_input['Plot Start Date'],
															max_value=session_state.user_input['Plot End Date'])


		session_state.user_input['New Selected Categories'] = st.sidebar.multiselect("Quais categorias gostaria de analisar?", session_state.user_input['Categories'],
																   session_state.user_input['Categories'])

		session_state.user_input = data_preprocess.verify_change(session_state.user_input, 'Selected Categories', 'New Selected Categories')

		# pre-process the data
		# filtering by category
		session_state.visualize_df = session_state.og_df[session_state.og_df['Categoria'].isin(session_state.user_input['Selected Categories'])]

		# filtering by date
		session_state.visualize_df = session_state.visualize_df[(session_state.visualize_df['Data'].dt.date >= session_state.user_input['Plot Start Date']) &
																(session_state.visualize_df['Data'].dt.date <= session_state.user_input['Plot End Date'])]


		session_state.expenses_categories = session_state.visualize_df['Descrição'].unique().tolist() + session_state.user_input['Expenses']
		session_state.user_input['New Expenses'] = st.sidebar.multiselect("Quais são os seus gastos mensais?", session_state.expenses_categories,
																   session_state.user_input['Expenses'])

		session_state.user_input = data_preprocess.verify_change(session_state.user_input, 'Expenses', 'New Expenses')


		session_state.economy_categories = session_state.visualize_df['Categoria'].unique().tolist() + session_state.user_input['Savings']

		session_state.user_input['New Savings'] = st.sidebar.multiselect("Quais são suas categorias de economia?", session_state.economy_categories,
																   		 session_state.user_input['Savings'])

		session_state.user_input = data_preprocess.verify_change(session_state.user_input, 'Savings', 'New Savings')


		session_state.metrics, session_state.monthly_metrics = data_preprocess.measure_kpis(session_state.og_df,
																							session_state.visualize_df,
																							session_state.user_input['Income'],
																							session_state.user_input['Savings'])

        # HERE: I have to add a update table button


		# main indicators
		#col1, col2, col3, col4 = st.columns(4)
		col1, subcol, col2 = st.columns((70, 5, 25))

		session_state.visualize_df = session_state.visualize_df.sort_values('Data')

		col1.markdown("## Visualização temporal de gastos:")

		session_state.temporal_graph = px.line(session_state.visualize_df, x='Data', y="Quantia")

		col1.plotly_chart(session_state.temporal_graph, use_container_width=True)

		session_state.category_graph = px.histogram(session_state.visualize_df, x="Mês", y="Quantia", color='Categoria',
									  barmode='group', width=400,).update_layout(yaxis_title="Quantidade Gasta")

		col1.markdown("## Gastos por categoria:")

		col1.plotly_chart(session_state.category_graph, use_container_width=True)

		session_state.visualize_df['Data'] = session_state.visualize_df['Data'].dt.strftime('%d/%m/%Y')

		col1.markdown("## Gastos:")

		col1.dataframe(session_state.visualize_df.drop(['Mês', 'index'], axis=1, errors='ignore'), width=1000)

		
		# anual
		visualization.plot_kpis(session_state.metrics, "Anual", col2,
											  session_state.og_df, session_state.user_input['Income'])

		# monthly
		visualization.plot_kpis(session_state.monthly_metrics, "Mensal", col2,
								session_state.og_df, session_state.user_input['Income'])


		visualization.plot_paid_monthly_expensives(session_state.visualize_df, col2, session_state.user_input['Expenses'])


		visualization.expenses_to_come(session_state.visualize_df, col2, session_state.user_input['Savings'])

	 
		with st.sidebar.expander("Qual é o limite de gasto para cada categoria?"):

			with st.form(key='categories'):

				session_state.info = {}

				session_state.info['Categoria'] = st.selectbox("Categoria", session_state.user_input['Categories'])
				session_state.info['Limite'] = st.number_input("Limite de Gasto", min_value=0, value=500)

				st.form_submit_button()

				if 'Budget Categories' in session_state.user_input.keys():

					session_state.user_input['New Budget Categories'] = {**session_state.user_input['Budget Categories'],
																		   session_state.info['Categoria']: session_state.info['Limite']}


					session_state.user_input = data_preprocess.verify_change(session_state.user_input, 'Budget Categories', 'New Budget Categories')

				else:

					session_state.user_input['Budget Categories'] = {session_state.info['Categoria']: session_state.info['Limite']}



		col1.markdown("## Limite de gastos por categoria mensal:")

		session_state.limits_table = data_preprocess.define_limits_table(session_state.visualize_df, session_state.user_input)

		col1.dataframe(session_state.limits_table.drop(['Dividido', 'Mês', 'Ultrapassou', 'Color'], axis=1).style.highlight_max(axis=1), width=1000)

		if session_state.user_input['Change']:

			session_state.collection = session_state.variables['collection']

			session_state.user_input['Plot Start Date'] = str(session_state.user_input['Plot Start Date'])
			session_state.user_input['Plot End Date'] = str(session_state.user_input['Plot End Date'])

			collection.update_one({"email": session_state.user_input['email']}, {"$set": session_state.user_input}, True)

			session_state.user_input['Change'] = False


		session_state.user_input['new link'] = st.sidebar.text_input("Avaliar outra planilha do GoogleSheets!", '')

		session_state.update_sheet = st.sidebar.button("Atualizar planilha atual")

		if session_state.user_input['new link'] != '' or session_state.update_sheet:

			session_state.main_column = 'new link'

			if session_state.update_sheet:

				session_state.main_column = 'link'

			session_state.valid_execution, session_state.new_df = user_initial_page.treat_input_sheet(session_state.user_input, st.sidebar,
																									  session_state.main_column)

			session_state.variables['og_df'] = session_state.new_df

			if session_state.valid_execution:

				if not session_state.update_sheet:

					session_state.user_input = data_preprocess.verify_change(session_state.user_input, 'link', 'new link')

					session_state.user_input['new link'] = ''

				session_state.familiar_categories, _ = data_preprocess.retrieve_categories(session_state.new_df)

				session_state.og_df = data_preprocess.data_treatment(session_state.new_df)

				session_state.variables['og_df'] = session_state.og_df

				session_state.user_input['Expenses'] = session_state.familiar_categories['Expenses']

				session_state.user_input['Savings'] = session_state.familiar_categories['Savings']

				session_state.session_state.user_input['Income'] = session_state.familiar_categories['Income']

				session_state.variables['user_input'] = session_state.user_input


	else:

		(session_state.user_input, session_state.og_df,
		 session_state.variables['valid'], session_state.new_user) = user_initial_page.define_user_inputs(session_state)

		if session_state.variables['valid']:
		
			session_state.variables = insert_cache_variables(session_state.variables, "og_df", session_state.og_df)
			session_state.variables = insert_cache_variables(session_state.variables, "user_input", session_state.user_input)

			session_state.collection = session_state.variables['collection']

			if session_state.new_user:

				session_state.collection.insert_one(session_state.variables['user_input'])
