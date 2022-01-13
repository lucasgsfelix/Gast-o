"""

	Gastão: Sistema de controle de gastos

"""

import pandas as pd

import streamlit as st

import plotly.graph_objects as go

from plotly.subplots import make_subplots


if __name__ == '__main__':

	# User json format:
	# User name, User ID; Income (dict) - it can be several incomes;
	# Budget Categories (dict); Bank Account (dict); Investiments (dict)
	# Spreed Sheet: link

	user_info = {"User Name": "Lucas Félix", "User ID": 0, "Income": {0: 8500},
				 "Budget Categories": {"Vestuário": 100, "Viagens": 200, "Eletrônicos": 200,
				 "Saúde": 100, "Outros": 100, "Casa": 200, "Educação": 200, "Alimentação": 400,
				 "Transporte": 300}, "Investiments": {}, "Spreed Sheet": 0}

	# I need a login

	# If the salary is brute we need to measure how much is the liquid

	# I need to automatically acess the sheet

	new_user = False

	if new_user:

		# cadastration

		# If it is a new user I need to take the infos as input

		# I need to take as input the salary

		pass


	else:

		pass

		# Is not a new user

		# We must update the spread sheet - user_sheet

	user_sheet = pd.read_table("test.csv", sep=',', decimal=',')

	# visualization filters
	# by week, by month, by year, specific year, specific month

	# What info will be shown:
	# expenses per group
	category_mean = user_sheet.groupby('Categoria').mean()
	category_std = user_sheet.groupby('Categoria').std()
	category_sum = user_sheet.groupby('Categoria').sum()

	category_summary = category_mean.join(category_std, lsuffix=' std.')
	category_summary = category_summary.join(category_sum, lsuffix=' sum').reset_index()

	user_budget = pd.DataFrame(user_info["Budget Categories"].items(), columns=['Categoria', 'Limite'])

	limits_df = user_budget.set_index("Categoria").join(category_sum, how='outer')

	# filling quantia and limite
	limits_df = limits_df.fillna(0)

	# the sum of expenses is bigger than the budget?
	limits_df['Ultrapassou'] = limits_df['Quantia'] >= limits_df['Limite']


	def verify_surpassed_limit(value):


		if value:

			return 'red'

		return 'black'

	limits_df['Color'] = limits_df['Ultrapassou'].apply(lambda value: verify_surpassed_limit(value))


	limits_df.reset_index(inplace=True)



	# https://plotly.com/python/table-subplots/

	fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    specs=[[{"type": "table"}],
           [{"type": "scatter"}],
           [{"type": "scatter"}]]
	)

	fig.add_trace(
	    go.Scatter(
	        x=user_sheet["Data"],
	        y=user_sheet["Quantia"],
	        mode="lines",
	        name="Valor gasto por dia"
	    ),
	    row=3, col=1
	)

	# Data	Categoria	Descrição	Quantia	Modalidade (Cŕedito/Pix/Débito/Boleto)	Dividido

	user_sheet = user_sheet.rename(columns={"Modalidade (Cŕedito/Pix/Débito/Boleto)": "Modalidade"})

	user_sheet['Data'] = pd.to_datetime(user_sheet['Data'], format='%d/%m/%Y').astype(str)

	fig.add_trace(
	    go.Table(
	        header=dict(
	            values=["Data", "Categoria", "Descrição",
	                    "Quantia", "Modalidade", "Dividido"],
	            font=dict(size=10),
	            align="left"
	        ),
	        cells=dict(
	            values=[user_sheet[k].tolist() for k in user_sheet.columns],
	            align = "left")
	    ),
	    row=1, col=1
	)

	a = limits_df['Color']

	colors = [['black'] * len(a), a, ['black'] * len(a)]

	fig.add_trace(go.Table(
                 columnwidth= [15]+[15]+[15],
                 columnorder=[0, 1, 2],
                 header = dict(height = 50,
                               values = [['<b>Limite</b>'], ['<b>Quantia</b>'], ["<b>Categoria</b>"]],
                               line = dict(color='rgb(50,50,50)'),
                               align = ['left']*2,
                               font = dict(color=['rgb(45,45,45)']*2, size=14),
                             
                              ),
                 cells = dict(values = [limits_df['Limite'], limits_df['Quantia'], limits_df['Categoria']],
                              line = dict(color='#506784'),
                              align = ['left']*5,
                              font = dict(family="Arial", size=14, color=colors),
                              height = 30,
                              fill = dict(color='rgb(245,245,245)'))
                             ))

	fig.update_layout(
	    height=800,
	    showlegend=False,
	    title_text="Quantias gastas",
	)

	fig.show()

	# I need to consume for each user the budgets for their categories

	# I need to automatically measure if any category is exploding any budget

	# Measure all

	# Show the dash

 

