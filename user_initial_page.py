"""

	Page focused on getting the data needed for the users

"""

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


def define_user_inputs(user_name=''):
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

	_, col, _ = st.columns((70, 70, 70))

	user_sheet = None


	col.markdown("# Olá " + user_name + " seja bem-vindo ao Gastão!")

	col.markdown("## Precisamos de algumas informações suas para podermos prosseguir!")

	needed_input['link'] = col.text_input("Coloque aqui o link da sua planilha no GoogleSheets!", "")

	col.info("Não se esqueça que a sua planilha deve ser pública para podermos acessar!")

	valid_execution = False

	if needed_input['link'] != '':

		valid_execution, user_sheet = treat_input_sheet(needed_input, col)


	if valid_execution:

		valid_execution = False

		### all the data is valid
		familiar_categories, identified = data_preprocess.retrieve_categories(user_sheet)


		if identified:

			col.success("Foram identificadas algumas categorias!")

		categories = user_sheet['Categoria'].unique()

		expenses_categories = user_sheet['Descrição'].unique().tolist() + familiar_categories['Expenses']
		needed_input['Expenses'] = col.multiselect("Quais são os seus gastos mensais? (Aqueles que se repetem)", expenses_categories,
																   							 familiar_categories['Expenses'])


		economy_categories = user_sheet['Categoria'].unique().tolist() + familiar_categories['Savings']
		needed_input['Savings'] = col.multiselect("Quais são suas categorias de economia?", economy_categories,
																   familiar_categories['Savings'])

		income_categories = user_sheet['Categoria'].unique().tolist() + familiar_categories['Income']
		needed_input['Income'] = col.multiselect("Quais são suas categorias de fonte de renda? (Salário)", income_categories,
																   								familiar_categories['Income'])


		valid_execution = col.button("Enviar informações!")


	return needed_input, user_sheet, valid_execution

