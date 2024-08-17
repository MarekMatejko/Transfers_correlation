# Import the functions from Web_scraping_code.ipynb
from Web_scraping import Web_scraping_code
from Cleaning_data import Cleaning_data_code
from Finding_correlation import Finding_correlation_code

# URL for the transfers data
url_transfers = "https://www.transfermarkt.co.uk/premier-league/einnahmenausgaben/wettbewerb/ES1"

# Fetch and store the transfers data
df_seasons_statistics_transfers = Web_scraping_code.main_getting_scraping_data(url_transfers, Web_scraping_code.getting_transfers_data)\

# URL for the league table data
url_league_table = "https://www.transfermarkt.co.uk/premier-league/tabelle/wettbewerb/ES1?saison_id=2024"

# Fetch and store the league table data
df_seasons_statistics_table = Web_scraping_code.main_getting_scraping_data(url_league_table, Web_scraping_code.getting_season_data)

# Process and merge the dataframes
df_merged_data = Cleaning_data_code.process_dataframes(df_seasons_statistics_table, df_seasons_statistics_transfers)

# Assign rankings based on the merged data
df_merged_data = Finding_correlation_code.assign_ranking(df_merged_data)

# Calculate correlations between 'Places' and other columns
correlation_spend_rank = Finding_correlation_code.calculate_correlation(df_merged_data, 'Places', 'Spend_Rank')
correlation_spend = Finding_correlation_code.calculate_correlation(df_merged_data, 'Places', 'Spend')
correlation_balance = Finding_correlation_code.calculate_correlation(df_merged_data, 'Places', 'Balance')

# Use combine_correlations fuction
combined_correlations = Finding_correlation_code.combine_correlations(correlation_spend_rank, correlation_spend, correlation_balance)
combined_correlations

#  Saving data as csv
df_merged_data.to_csv('df_merged_data_LaLiga.csv', index=False)

combined_correlations.to_csv('correlations_LaLiga.csv', index=False)

# Write correlation results
print(combined_correlations)
