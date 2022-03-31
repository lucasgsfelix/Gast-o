"""

	Page focused on getting the data needed for the users

"""
import re

import streamlit as st
import validators

import data_preprocess


def treat_input_sheet(needed_input, col):

	user_sheet, valid_execution = None, False


	if validators.url(needed_input['link']):

		# in this case is a valid link

		valid_execution = True


		try:
		
			user_sheet = data_preprocess.download_google_drive_sheet(needed_input['link'])

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


def define_user_inputs(needed_input, collection=None):
	"""

		Inputs needed from the user:

		Sheet_Link
		Categories

		What is your categories for:
		Expenses
		Savings
		Income

	"""

	_, col, _ = st.columns((70, 70, 70))

	user_sheet, go_to_graphs, valid_execution = None, False, False


	col.markdown("# Olá, seja bem-vindo ao Gastão!")

	needed_input['email'] = col.text_input("Digite seu e-mail:", "")

	needed_input['valid e-mail'] = False

	if bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", needed_input['email'])):

		needed_input['valid e-mail'] = True


	else:

		if needed_input['email'] != '':

			col.error("E-mail inválido. Por favor, digite um e-mail válido para prosseguirmos.")



	if 'valid e-mail' in needed_input.keys() and needed_input['valid e-mail'] and collection is not None:

		queried_data = collection.find({'email': needed_input['email']})

		queried_data = [data for data in queried_data]

		history_error = False

		if len(queried_data) > 0:

			# needed_input, user_sheet, go_to_graphs

			needed_input = queried_data[0]

			valid_execution, user_sheet = treat_input_sheet(needed_input, col)

			if valid_execution:

				return queried_data[0], user_sheet, True, False

			else:


				# in this case the is an error with the user input sheet
				history_error = True

				col.markdown("## Houve um erro com a planilha que você passou anteriormente.\
							  Por favor, insira novamente seus dados ou corrija sua planilha e reinicie o processo.")


		if len(queried_data) == 0 or history_error:

			if not history_error:

				col.markdown("## Precisamos de algumas informações suas para podermos prosseguir!")

			needed_input['link'] = col.text_input("Coloque aqui o link da sua planilha no GoogleSheets!", "")

			col.info("Não se esqueça que a sua planilha deve ser pública para podermos acessar!")


			if needed_input['link'] != '':

				valid_execution, user_sheet = treat_input_sheet(needed_input, col)

			go_to_graphs = False

			if valid_execution:

				valid_execution = False

				### all the data is valid
				familiar_categories, identified = data_preprocess.retrieve_categories(user_sheet)


				if identified:

					col.success("Foram identificadas algumas categorias!")

				categories = user_sheet['Categoria'].unique()

				expenses_categories = user_sheet['Descrição'].unique().tolist() + familiar_categories['Expenses']
				col.write("<b><center>Quais são os seus gastos mensais? (Aqueles que se repetem)</center></b>", unsafe_allow_html=True)
				needed_input['Expenses'] = col.multiselect("", expenses_categories, familiar_categories['Expenses'])


				economy_categories = user_sheet['Categoria'].unique().tolist() + familiar_categories['Savings']
				col.write("<b><center>Quais são suas categorias de economia?</center></b>", unsafe_allow_html=True)
				needed_input['Savings'] = col.multiselect('', economy_categories, familiar_categories['Savings'])

				income_categories = user_sheet['Categoria'].unique().tolist() + familiar_categories['Income']
				col.write("<b><center>Quais são suas categorias de fonte de renda? (Salário)</center></b>", unsafe_allow_html=True)
				needed_input['Income'] = col.multiselect("", income_categories, familiar_categories['Income'])


				with col.form(key='categories'):

					info = {}

					col.write("<b><center>Qual é o seu limite de gasto mensal para cada categoria?</center></b>", unsafe_allow_html=True)

					info['Categoria'] = col.selectbox("Categoria", categories)
					info['Limite'] = col.number_input("Limite de Gasto", min_value=0, value=500)

					if col.button(label="Salvar limite de gasto!"):

						if 'Budget Categories' in needed_input.keys():

							needed_input['Budget Categories'] = {**needed_input['Budget Categories'], info['Categoria']: info['Limite']}

							# in this case there is already a budget for some categories

						else:

							needed_input['Budget Categories'] = {info['Categoria']: info['Limite']}


						budgets = [category + " " + str(budget)  for category, budget in needed_input['Budget Categories'].items()]

						col.code(', '.join(budgets))


				go_to_graphs = col.button("Enviar informações!")


	return needed_input, user_sheet, go_to_graphs, True

