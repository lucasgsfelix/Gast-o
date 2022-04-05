"""

	Page focused on getting the data needed for the users

"""
import re

import streamlit as st
import validators

import data_preprocess


def treat_input_sheet(needed_input, col, link_column='link'):

	user_sheet, valid_execution = None, False


	if validators.url(needed_input[link_column]):

		# in this case is a valid link

		valid_execution = True


		try:
		
			user_sheet = data_preprocess.download_google_drive_sheet(needed_input[link_column])

		except:

			col.error("Houve um problema ao ler sua planilha. Ela está em modo privado?")

			valid_execution = False


		if valid_execution:

			# verify if the columns defined on the template sheet are present on the user sheet
			valid_execution, user_sheet, columns = data_preprocess.verify_sheet_columns(user_sheet)


			if not valid_execution:

				col.error("Sua planilha não possui todos os campos necessários para realizar a análise!\
						  Verifique se sua planilha possui as seguintes colunas: " + ', '.join(columns))


		user_sheet = data_preprocess.treat_nan_values(user_sheet)


		if valid_execution:

			# verify the types of the data read
			user_sheet, valid_execution = data_preprocess.verify_sheet_dtypes(user_sheet)

			if not valid_execution:

				col.error("Alguma das colunas da sua planilha possui valores inválidos. Por favor, revise-os.")



	else:

		col.error("O link adicionado não é válido! Por favor, insira um link válido.")

	return valid_execution, user_sheet


def define_user_inputs(session_state):
	"""

		Inputs needed from the user:

		Sheet_Link
		Categories

		What is your categories for:
		Expenses
		Savings
		Income

	"""

	col_a, col, col_b = st.columns(3)

	session_state.user_sheet, session_state.go_to_graphs, session_state.valid_execution = None, False, False

	session_state.collection = session_state.variables['collection']

	col.markdown("# Olá, seja bem-vindo ao Gastão!")

	with col.form(key='input_email'):

		session_state.variables['needed_input']['email'] = st.text_input("Digite seu e-mail:", "")

		if st.form_submit_button("Entrar"):

			session_state.variables['needed_input']['valid e-mail'] = False

			if bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", session_state.variables['needed_input']['email'])):

				session_state.variables['needed_input']['valid e-mail'] = True


			else:

				if session_state.variables['needed_input']['email'] != '':

					col.error("E-mail inválido. Por favor, digite um e-mail válido para prosseguirmos.")



	if 'valid e-mail' in session_state.variables['needed_input'].keys() and session_state.variables['needed_input']['valid e-mail'] and session_state.collection is not None:

		session_state.queried_data = session_state.collection.find({'email': session_state.variables['needed_input']['email']})

		session_state.queried_data = [data for data in session_state.queried_data]

		session_state.history_error = False

		if len(session_state.queried_data) > 0:

			# needed_input, user_sheet, go_to_graphs

			session_state.variables['needed_input'] = session_state.queried_data[0]

			session_state.valid_execution, session_state.user_sheet = treat_input_sheet(session_state.variables['needed_input'], col)

			if session_state.valid_execution:

				return session_state.queried_data[0], session_state.user_sheet, True, False

			else:


				# in this case the is an error with the user input sheet
				session_state.history_error = True

				col.markdown("## Houve um erro com a planilha que você passou anteriormente.\
							  Por favor, insira novamente seus dados ou corrija sua planilha e reinicie o processo.")


		if len(session_state.queried_data) == 0 or session_state.history_error:

			if not session_state.history_error:

				col.markdown("## Precisamos de algumas informações suas para podermos prosseguir!")

			session_state.variables['needed_input']['link'] = col.text_input("Coloque aqui o link da sua planilha no GoogleSheets!", "")

			col.info("Não se esqueça que a sua planilha deve ser pública para podermos acessar!")


			if session_state.variables['needed_input']['link'] != '':

				session_state.valid_execution, session_state.user_sheet = treat_input_sheet(session_state.variables['needed_input'], col)

			session_state.go_to_graphs = False

			if session_state.valid_execution:

				session_state.valid_execution = False

				### all the data is valid
				session_state.familiar_categories, session_state.identified = data_preprocess.retrieve_categories(session_state.user_sheet)


				if session_state.identified:

					col.success("Foram identificadas algumas categorias!")

				session_state.categories = session_state.user_sheet['Categoria'].unique()

				session_state.expenses_categories = session_state.user_sheet['Descrição'].unique().tolist() + session_state.familiar_categories['Expenses']
				col.write("<b><center>Quais são os seus gastos mensais? (Aqueles que se repetem)</center></b>", unsafe_allow_html=True)
				session_state.variables['needed_input']['Expenses'] = col.multiselect("", session_state.expenses_categories, session_state.familiar_categories['Expenses'])


				session_state.economy_categories = session_state.user_sheet['Categoria'].unique().tolist() + session_state.familiar_categories['Savings']
				col.write("<b><center>Quais são suas categorias de economia?</center></b>", unsafe_allow_html=True)
				session_state.variables['needed_input']['Savings'] = col.multiselect('', session_state.economy_categories, session_state.familiar_categories['Savings'])

				session_state.income_categories = session_state.user_sheet['Categoria'].unique().tolist() + session_state.familiar_categories['Income']
				col.write("<b><center>Quais são suas categorias de fonte de renda? (Salário)</center></b>", unsafe_allow_html=True)
				session_state.variables['needed_input']['Income'] = col.multiselect("", session_state.income_categories, session_state.familiar_categories['Income'])


				with col.form(key='categories'):

					session_state.info = {}

					col.write("<b><center>Qual é o seu limite de gasto mensal para cada categoria?</center></b>", unsafe_allow_html=True)

					session_state.info['Categoria'] = col.selectbox("Categoria", session_state.categories)
					session_state.info['Limite'] = col.number_input("Limite de Gasto", min_value=0, value=500)

					if col.button(label="Salvar limite de gasto!"):

						if 'Budget Categories' in session_state.variables['needed_input'].keys():

							session_state.variables['needed_input']['Budget Categories'] = {**session_state.variables['needed_input']['Budget Categories'],
																   session_state.info['Categoria']: session_state.info['Limite']}

							# in this case there is already a budget for some categories

						else:

							session_state.variables['needed_input']['Budget Categories'] = {session_state.info['Categoria']: session_state.info['Limite']}


						session_state.budgets = [category + " " + str(budget)  for category, budget in session_state.variables['needed_input']['Budget Categories'].items()]

						col.code(', '.join(session_state.budgets))


				session_state.go_to_graphs = col.button("Enviar informações!")


	return session_state.variables['needed_input'], session_state.user_sheet, session_state.go_to_graphs, True

