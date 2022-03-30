"""

	Page focused on getting the data needed for the users

"""

import streamlit as st
import validators

import data_preprocess


def treat_input_sheet(needed_input):

	user_sheet, valid_execution = None, False


	if validators.url(needed_input['link']):

		# in this case is a valid link

		valid_execution = True

		try:
		
			user_sheet = download_google_drive_sheet(needed_input['link'])

		except:

			st.error("Houve um problema ao ler sua planilha. Ela está em modo privado?")

			valid_execution = False


		if valid_execution:

			# verify if the columns defined on the template sheet are present on the user sheet
			valid_execution, user_sheet, columns = data_preprocess.verify_sheet_columns(user_sheet)


			if not valid_execution:

				st.error("Sua planilha não possui todos os campos necessários para realizar a análise!\
						  Verifique se sua planilha possui as seguintes colunas: " + columns)


		user_sheet = data_preprocess.treat_nan_values(user_sheet)


		if valid_execution:

			# verify the types of the data read
			user_sheet, valid_execution = data_preprocess.verify_sheet_dtypes(user_sheet)

			if not valid_execution:

				st.error("Alguma das colunas da sua planilha possui valores inválidos. Por favor, revise-os.")



	else:

		st.error("O link adicionado não é válido! Por favor, insira um link válido.")

	return valid_execution, user_sheet


def define_user_inputs():
	"""

		Inputs needed from the user:

		Sheet_Link
		Categories

		What is your categories for:
		Expenses
		Savings
		Income

	"""


	needed_input = {}


	st.markdown("# Olá " + user_name, + " seja bem-vindo ao Gastão!")

	st.markdown("## Precisamos de algumas informações suas para podermos prosseguir!")

	needed_input['link'] = st.text_input("Coloque aqui o link da sua planilha no GoogleSheets!", "")

	st.info("Não se esqueça que a sua planilha deve ser pública para podermos acessar!")

	valid_execution, user_sheet = treat_input_sheet(needed_input)


	if valid_execution:

		### all the data is valid
		familiar_categories = data_preprocess.retrieve_categories(user_sheet)

		categories = user_sheet['Categoria'].unique()

		expenses_categories = visualize_df['Descrição'].unique().tolist() + familiar_categories['Expenses']
		needed_input['Expenses'] = st.sidebar.multiselect("Quais são os seus gastos mensais? (Aqueles que se repetem)", expenses_categories,
																   							 familiar_categories['Expenses'])


		economy_categories = visualize_df['Categoria'].unique().tolist() + familiar_categories['Savings']
		needed_input['Savings'] = st.sidebar.multiselect("Quais são suas categorias de economia?", economy_categories,
																   familiar_categories['Savings'])

		income_categories = visualize_df['Categoria'].unique().tolist() + familiar_categories['Income']
		needed_input['Income'] = st.sidebar.multiselect("Quais são suas categorias de fonte de renda? (Salário)", income_categories,
																   								familiar_categories['Income'])



	return needed_input



