import pandas as pd

def import_datasets():
    """Import and return required datasets."""
    path = "data/"
    df_all_data = pd.read_csv(path + "gvc_trade_WITS-update.csv")
    df_sectors = pd.read_csv(path + "sector-tiva.csv", sep=";")
    df_countries = pd.read_csv(path + "gvc-countries.csv")

    return df_all_data, df_sectors, df_countries


def filter_and_merge_datasets(df_all_data, df_sectors):
    """Filter, merge, and clean datasets."""
    # Drop unnecessary columns
    unnecessary_col = ["gtrade_fin", "gtrade_int", "traditional_trade_int", "traditional_trade_fin", "gvcbp", "gvcfp", "gvcmix"]
    df_data = df_all_data.drop(unnecessary_col, axis=1)

    # Filter data for a range of years
    before95_index = df_data[df_data["t"] < 1995].index
    df_data.drop(before95_index, inplace=True)

    # Merge datasets
    left_on = ["sect", "source"]
    right_on = ["sect", "source"]
    df_filtered = pd.merge(df_data, df_sectors, left_on=left_on, right_on=right_on, how="left")
    df_filtered.drop(["sect"], axis=1, inplace=True)

    return df_filtered


def convert_country_abbreviation(df_filtered, df_countries):
    """Convert country abbreviation to full name."""
    # Create a dictionary from the dataframe
    dic_country_name = {row["country"]: row["country_name"] for _, row in df_countries.iterrows()}

    # Change country abbreviation to full name in exp and imp column
    for col in ["exp", "imp"]:
        df_filtered[col] = df_filtered[col].map(dic_country_name)

    return df_filtered


def clean_dataset(df_filtered):
    """Clean the dataset by handling null values and filtering rows."""
    # Fill null values with "Rest of the World"
    df_filtered["exp"].fillna("Rest of the World", inplace=True)
    df_filtered["imp"].fillna("Rest of the World", inplace=True)

    # Drop rows with specific source values
    drop_sectors = ["adb", "eora", "wiodlr", "wiodn", "wiodo"]
    df_clean = df_filtered[df_filtered.source.isin(drop_sectors) == False]

    # Replace "Viet Nam" with "Vietnam"
    for col in ["exp", "imp"]:
        df_clean[col] = df_clean[col].replace(["Viet Nam"], "Vietnam")

    # Rename columns
    column_names = {"exp": "Export", "imp": "Import", "t": "Year", "source": "Source", "gtrade": "Gross Trade",
                    "traditional_trade": "Traditional Trade", "gvc": "GVC", "category": "Category"}
    df_clean.rename(columns=column_names, inplace=True)

    # Remove rows where export and import are the same country
    df_clean = df_clean[df_clean["Export"] != df_clean["Import"]]

    return df_clean


def main():
    # Import datasets
    df_all_data, df_sectors, df_countries = import_datasets()

    # Filter and merge datasets
    df_filtered = filter_and_merge_datasets(df_all_data, df_sectors)

    # Convert country abbreviation to full name

    df_filtered = convert_country_abbreviation(df_filtered, df_countries)

    # Clean dataset
    df_clean = clean_dataset(df_filtered)

    # Inspect the clean dataframe
    print(df_clean.sample(15))
    print(df_clean.count())
    print(df_clean.isnull().sum())

if __name__ == "__main__":
    main()
