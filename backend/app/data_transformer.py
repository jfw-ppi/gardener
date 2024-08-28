import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MultiLabelBinarizer


# Function to save and display the missing data visualization
def visualize_missing_values(df, title, filename):
    missing_values = df.isna().sum()
    empty_string_counts = (df == '').sum()
    combined_missing = missing_values + empty_string_counts

    plt.figure(figsize=(15, 7))
    sns.barplot(x=combined_missing.index, y=combined_missing.values, palette="viridis", hue=None, legend=False)
    plt.xticks(rotation=90)
    plt.title(title)
    plt.ylabel("Number of Missing/Empty Entries")
    plt.xlabel("Columns")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# Function to encode ordinal columns with binary encoding for multiple values
def binary_encode_ordinal_columns(df, ordinal_columns):
    mlb = MultiLabelBinarizer()

    for col in ordinal_columns:
        if col in df.columns:
            df[col] = df[col].replace('', pd.NA)
            df = df.dropna(subset=[col])  # Remove rows with unset values

            # Split the string by commas and apply MultiLabelBinarizer
            df.loc[:, col] = df[col].apply(lambda x: x.split(', '))
            encoded_cols = pd.DataFrame(mlb.fit_transform(df[col]), columns=mlb.classes_, index=df.index)

            # Join the binary encoded columns with the original DataFrame
            df = df.drop(columns=[col]).join(encoded_cols)

    return df


# Function to replace missing values in numerical columns with the mean
def fill_missing_numerical_with_mean(df, columns):
    for col in columns:
        df[col] = df[col].replace('', pd.NA)  # Unify missing values
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(df[col].mean())
    return df


# Function to perform all transformations and save reports
def transform_ecocrop_data(binary_encode=False):
    # Define paths
    resources_path = "resources"
    data_report_path = os.path.join(resources_path, "data-report")

    # Ensure the resources and data-report directories exist
    os.makedirs(resources_path, exist_ok=True)
    os.makedirs(data_report_path, exist_ok=True)

    # Load the Excel file into a DataFrame (before any transformations)
    file_path = os.path.join(resources_path, "EcoCrop_DB.xlsx")
    ecocrop_df = pd.read_excel(file_path)

    # Open a text file to write the summary
    summary_file_path = os.path.join(data_report_path, "transformation_summary.txt")
    with open(summary_file_path, "w") as summary_file:

        # Perform initial visualizations
        visualize_missing_values(ecocrop_df,
                                 "Missing Values (NA or Empty String) Across Columns - Before Transformation",
                                 os.path.join(data_report_path, "missing_before.png"))

        # List of ordinal fields with multiple possible values
        ordinal_fields_with_multiple_values = ["TEXT", "DRA"]

        # Apply binary encoding if specified
        if binary_encode:
            ecocrop_df = binary_encode_ordinal_columns(ecocrop_df, ordinal_fields_with_multiple_values)

        # List of numerical fields to process
        numerical_fields = ["TOPMN", "TOPMX", "TMIN", "TMAX", "ROPMN", "ROPMX", "RMIN", "RMAX", "GMIN", "GMAX", "KTMP"]

        # Step 1: Remove entries where TOPMN > 40 degrees
        initial_row_count = ecocrop_df.shape[0]
        invalid_topmn_mask = ecocrop_df['TOPMN'] > 40
        invalid_topmn_count = invalid_topmn_mask.sum()
        ecocrop_df = ecocrop_df[~invalid_topmn_mask]

        # Step 2: Handle KTMP where it is NA and set min temp -5 degrees in C° as default value
        ktmp_na_mask = ecocrop_df['KTMP'].isna()
        ktmp_na_count = ktmp_na_mask.sum()
        ecocrop_df.loc[ktmp_na_mask, 'KTMP'] = ecocrop_df.loc[ktmp_na_mask, 'TMIN'] - 5

        # Step 3: Validate latitude-related fields and remove invalid data with degrees > 90
        latitude_columns = ['LATOPMN', 'LATOPMX', 'LATMN', 'LATMX']
        latitude_invalid_counts = {}
        for col in latitude_columns:
            invalid_latitude_mask = (ecocrop_df[col] < -90) | (ecocrop_df[col] > 90)
            latitude_invalid_counts[col] = invalid_latitude_mask.sum()
            ecocrop_df.loc[invalid_latitude_mask, col] = pd.NA

        # Step 4: Handle GMAX, GMIN where it is NA or an empty string AFTER all removals and set to 0 as default
        gmax_na_or_empty_mask = ecocrop_df['GMAX'].isna() | (ecocrop_df['GMAX'] == '')
        gmax_na_count = gmax_na_or_empty_mask.sum()
        ecocrop_df.loc[gmax_na_or_empty_mask, 'GMAX'] = 0

        gmin_na_or_empty_mask = ecocrop_df['GMIN'].isna() | (ecocrop_df['GMIN'] == '')
        gmin_na_count = gmin_na_or_empty_mask.sum()
        ecocrop_df.loc[gmin_na_or_empty_mask, 'GMIN'] = 0

        # Step 5: Remove rows with any other NA values in the fields of interest
        fields_to_check = ["TOPMN", "TOPMX", "TMIN", "TMAX", "ROPMN", "ROPMX", "RMIN", "RMAX", "GMIN", "GMAX", "KTMP"]
        before_removal_row_count = ecocrop_df.shape[0]
        cleaned_ecocrop_df = ecocrop_df.dropna(subset=fields_to_check)
        removed_rows_count = before_removal_row_count - cleaned_ecocrop_df.shape[0]

        # Determine the output file name based on whether binary encoding was applied
        if binary_encode:
            cleaned_file_name = "Cleaned_EcoCrop_DB_Final_BinaryEncoded.xlsx"
            suffix = "_binary_encoded"
        else:
            cleaned_file_name = "Cleaned_EcoCrop_DB_Final.xlsx"
            suffix = ""

        cleaned_file_path = os.path.join(resources_path, cleaned_file_name)
        cleaned_ecocrop_df.to_excel(cleaned_file_path, index=False)

        # Summary of transformations
        summary_file.write("\nData Transformation Summary:\n")
        summary_file.write(f"1. Removed {invalid_topmn_count} rows where 'TOPMN' > 40 degrees.\n")
        summary_file.write(f"2. Replaced NA values in 'KTMP' with 'TMIN - 5 degrees' for {ktmp_na_count} rows.\n")
        for col, count in latitude_invalid_counts.items():
            summary_file.write(
                f"3. Set latitude values outside the range -90 to 90 degrees to NA for {count} rows in '{col}'.\n")
        summary_file.write(f"4. Set 'GMAX' to 0 for {gmax_na_count} rows where it was missing or empty.\n")
        summary_file.write(
            f"5. Removed {removed_rows_count} rows with NA values in the following fields: {', '.join(fields_to_check)}.\n")
        if binary_encode:
            summary_file.write("6. Binary encoded ordinal columns with multiple values.\n")
        summary_file.write(
            f"Resulting dataset contains {cleaned_ecocrop_df.shape[0]} rows and {cleaned_ecocrop_df.shape[1]} columns.\n")

        # Perform final visualizations with modified filenames if binary encoding is applied
        visualize_missing_values(cleaned_ecocrop_df,
                                 "Missing Values (NA or Empty String) Across Columns - After Transformation",
                                 os.path.join(data_report_path, f"missing_after{suffix}.png"))

        # Further analysis (example: value distributions)
        plt.figure(figsize=(15, 7))
        sns.boxplot(data=cleaned_ecocrop_df[numerical_fields], palette="viridis")
        plt.title("Value Distributions Across Suitability Score Fields - After Transformation")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.path.join(data_report_path, f"distributions_after{suffix}.png"))
        plt.close()


# Call the transformation method with binary encoding as needed
# transform_ecocrop_data(binary_encode=False)
