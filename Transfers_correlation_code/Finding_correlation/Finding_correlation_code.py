# Group by Year, sort by Spend descending, reset index, assign Spend_Rank
def assign_ranking(df):
    df = df.groupby('Year').apply(lambda x: x.sort_values(by='Spend', ascending=False)
                                          .reset_index(drop=True)
                                          .assign(Spend_Rank=lambda x: x.index + 1))
    return df.reset_index(drop=True)


# Calculate the correlation between Places and Spend_Rank for each year
def calculate_correlation_with_lambda(df):
    correlations = df.groupby('Year').apply(
        lambda x: x[['Places', 'Spend_Rank']].astype(float)
        .corr().loc['Places', 'Spend_Rank']
    ).reset_index(name='Correlation')
    return correlations