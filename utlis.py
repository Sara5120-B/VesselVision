import pandas as pd
import streamlit as st

def load_and_clean_excel(file):
    try:
        # Load the raw Excel to inspect first 5 rows (no headers yet)
        preview = pd.read_excel(file, engine="openpyxl", header=None)

        # Try rows 0 to 5 to find the best header row
        for i in range(0, 5):
            row = preview.iloc[i]
            if row.notna().sum() >= 3:  # Heuristic: header row should have at least 3 valid entries
                df = pd.read_excel(file, engine="openpyxl", skiprows=i)

                # Drop fully empty rows and columns
                df.dropna(axis=0, how="all", inplace=True)
                df.dropna(axis=1, how="all", inplace=True)

                # Reset index and return clean dataframe
                return df.reset_index(drop=True)

        # Fallback if no header row found: use default loading
        df = pd.read_excel(file, engine="openpyxl")
        df.dropna(axis=0, how="all", inplace=True)
        df.dropna(axis=1, how="all", inplace=True)
        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"❌ Could not read {file.name}")
        st.error(str(e))
        return pd.DataFrame()

