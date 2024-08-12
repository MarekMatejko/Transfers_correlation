from rapidfuzz import process, fuzz
import pandas as pd

# Function to clean the specified column in the DataFrame by removing unwanted characters and whitespace
def clean_column_text(df, column_name):
    return (
        df[column_name]
        .str.replace('\n', '', regex=False)
        .str.replace('\xa0', '', regex=False)
        .str.strip()
    )

# Function to match teams between two lists using fuzzy matching
def match_teams(teams_list_1, teams_list_2, threshold=50):
    mapping_dict = {}
    for team in teams_list_1:
        match = process.extractOne(team, teams_list_2, scorer=fuzz.token_sort_ratio)
        if match[1] > threshold:
            mapping_dict[team] = match[0]
        else:
            mapping_dict[team] = None
    return mapping_dict

# Function to convert spend and balance values from strings to numeric values
def convert_currency(value):
    value = str(value).replace('€', '')  # Ensure value is a string and remove euro symbol
    if value in ['-', '', '+-0']:
        return 0.0  # Handle special cases
    elif 'm' in value:
        return float(value.replace('m', '')) * 1e6  # Convert millions
    elif 'k' in value:
        return float(value.replace('k', '')) * 1e3  # Convert thousands
    else:
        return float(value)

# Function to process the dataframes
def process_dataframes(df_stats, df_transfers):
    # Clean the 'Teams' column in both dataframes
    df_stats['Teams'] = clean_column_text(df_stats, 'Teams')
    df_transfers['Teams'] = clean_column_text(df_transfers, 'Teams')

    # Extract unique team names from both dataframes
    unique_teams_stats = df_stats['Teams'].unique()
    unique_teams_transfers = df_transfers['Teams'].unique()

    # Perform team name matching between transfers and statistics tables
    mapping_dict = match_teams(unique_teams_transfers, unique_teams_stats)

    # Display the mapping dictionary for confirmation
    print("Here is the team mapping dictionary:")
    for team, mapped_team in mapping_dict.items():
        print(f"{team}: {mapped_team}")

    # Ask for user confirmation to continue
    while True:
        user_input = input(
            "Do the team names match correctly? Type 'yes' to continue, 'no' to apply manual corrections, or 'end' to exit: ").lower()

        if user_input == 'yes':
            break  # Continue with the function
        elif user_input == 'no':
            # Apply manual corrections and check again
            mapping_dict = manual_team_adjustments(mapping_dict)
            print("Manual corrections have been applied. Here is the updated mapping dictionary:")
            for team, mapped_team in mapping_dict.items():
                print(f"{team}: {mapped_team}")
        elif user_input == 'end':
            print("Exiting the function.")
            return None  # Exit the function
        else:
            print("Input not recognized. Please type 'yes', 'no', or 'end'.")

    # Map the matched team names back to the 'Teams' column in the transfers dataframe
    df_transfers['Teams'] = df_transfers['Teams'].map(mapping_dict).fillna(df_transfers['Teams'])

    # Merge DataFrames on 'Teams' and 'Year' columns to align data and include only common entries
    df_merged = pd.merge(df_stats, df_transfers, on=['Teams', 'Year'], how='inner')

    # Check if the length of the merged DataFrame is equal to the original df_transfers 'Teams' length
    if len(df_merged) != len(df_transfers['Teams']):
        print("Warning: The merged DataFrame has fewer rows than expected!")
        print({team: mapped_team for team, mapped_team in mapping_dict.items() if mapped_team is None})
        raise ValueError("Length mismatch between merged DataFrame and original transfers DataFrame.")

    # Apply the conversion to both Spend and Balance columns in the merged dataframe
    df_merged['Spend'] = df_merged['Spend'].apply(convert_currency)
    df_merged['Balance'] = df_merged['Balance'].apply(convert_currency)

    return df_merged

# This function performs manual adjustments to team names in the mapping dictionary.
# Currently, it is specifically designed for the Premier League, and is not necessary for La Liga.
# However, if web scraping other leagues, manual team name corrections might be required
def manual_team_adjustments(mapping_dict):
    # Known manual corrections
    corrections = {
        'Wolverhampton Wanderers': 'Wolves',
        'Queens Park Rangers': 'QPR'
    }

    # Apply the corrections
    for incorrect_name, correct_name in corrections.items():
        if incorrect_name in mapping_dict:
            mapping_dict[incorrect_name] = correct_name
        else:
            print(f"Error: '{incorrect_name}' not found in the mapping dictionary.")

    return mapping_dict