import pandas as pd

# Group by Year, sort by Spend descending, reset index, assign Spend_Rank
def assign_ranking(df):
    df = df.groupby('Year').apply(lambda x: x.sort_values(by='Spend', ascending=False)
                                          .reset_index(drop=True)
                                          .assign(Spend_Rank=lambda x: x.index + 1))
    return df.reset_index(drop=True)


# Function to calculate the correlation between two specified columns in a DataFrame
def calculate_correlation(df, col1, col2):
    # Group the DataFrame by 'Year' and calculate the correlation between col1 and col2 for each group
    correlations = df.groupby('Year').apply(
        lambda x: x[[col1, col2]].astype(float)
        .corr().loc[col1, col2]
    ).reset_index(name=f'Correlation_{col1}_{col2}')
    return correlations

def combine_correlations(*correlation_dfs):
    # Combine the provided DataFrames along the columns axis
    combined_correlations = pd.concat(correlation_dfs, axis=1)
    # Remove duplicate columns that may have been introduced during the concatenation process
    combined_correlations = combined_correlations.loc[:, ~combined_correlations.columns.duplicated()]
    return combined_correlations
