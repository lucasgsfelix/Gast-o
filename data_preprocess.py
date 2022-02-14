import pandas as pd


def verify_surpassed_limit(value):

	if value:

		return 'red'

	return 'black'

def read_data(user_info):

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


	limits_df['Color'] = limits_df['Ultrapassou'].apply(lambda value: verify_surpassed_limit(value))


	limits_df.reset_index(inplace=True)

	user_sheet['Data'] = pd.to_datetime(user_sheet['Data'], format='%d/%m/%Y')

	user_sheet['Month'] = user_sheet['Data'].dt.month


	return limits_df, user_sheet

