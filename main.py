import streamlit as st
import pandas as pd
import plotly.express as px
import crypto_utils
import os
from api_client import APIClient


def update_dataframe_with_fund(df, fund_details):
    fund_name = fund_details["fscbi_legal_name"]
    total_return_index = fund_details["total_return_index"]

    # Check if total_return_index is not empty
    if not total_return_index:
        st.warning(f"No NAV data available for {fund_name}.")
        return df

    # Convert total return index to DataFrame
    new_data = pd.DataFrame(total_return_index)
    if "d" in new_data.columns and "v" in new_data.columns:
        new_data.rename(columns={"d": "Date", "v": "NAV"}, inplace=True)
        new_data["Date"] = pd.to_datetime(new_data["Date"])
        new_data["Fund Name"] = fund_name

        # Append to the existing DataFrame
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        st.error(f"Unexpected data format for {fund_name}.")
    return df

def fetch_funds(name: str):
    data = APIClient().get(
        f"/fund-details/get_fund/?limit=5&offset=0&search_by_name={name}&sort_by=ttr_return_3_yr&organization=3&filters="
        '{"sub_categories":[],"categories":[],"risk_level_ids":[],"amc_ids":[]}'
    )
    decrypt = crypto_utils.decrypt_data(data["data"])
    # print("all funds are", decrypt["funds"])
    return decrypt["funds"]


def fetch_fund_by_id(fund_id: str):
    data = APIClient().get(f"/fund-details/{fund_id}/?user_id={os.getenv("USER_ID")}")
    decrypt = crypto_utils.decrypt_data(data["data"])
    # print('decrypt is ', decrypt["funds_details"])
    return decrypt["funds_details"]

# fund_nord=fetch_fund_by_id("4266")
# print('fund nord is ', fund_nord)

fund_dates = [
    "2018-10-31",
    "2018-11-30",
    "2018-12-31",
    "2019-01-31",
    "2019-02-28",
    "2019-03-31",
    "2019-04-30",
    "2019-05-31",
    "2019-06-30",
    "2019-07-31",
    "2019-08-31",
    "2019-09-30",
    "2019-10-31",
    "2019-11-30",
    "2019-12-31",
    "2020-01-31",
    "2020-02-29",
    "2020-03-31",
    "2020-04-30",
    "2020-05-31",
    "2020-06-30",
    "2020-07-31",
    "2020-08-31",
    "2020-09-30",
    "2020-10-31",
    "2020-11-30",
    "2020-12-31",
    "2021-01-31",
    "2021-02-28",
    "2021-03-31",
    "2021-04-30",
    "2021-05-31",
    "2021-06-30",
    "2021-07-31",
    "2021-08-31",
    "2021-09-30",
    "2021-10-31",
    "2021-11-30",
    "2021-12-31",
    "2022-01-31",
    "2022-02-28",
    "2022-03-31",
    "2022-04-30",
    "2022-05-31",
    "2022-06-30",
    "2022-07-31",
    "2022-08-31",
    "2022-09-30",
    "2022-10-31",
    "2022-11-30",
    "2022-12-31",
    "2023-01-31",
    "2023-02-28",
    "2023-03-31",
    "2023-04-30",
    "2023-05-31",
    "2023-06-30",
    "2023-07-31",
    "2023-08-31",
    "2023-09-30",
    "2023-10-31",
    "2023-11-30",
    "2023-12-31",
    "2024-01-31",
    "2024-02-29",
    "2024-03-31",
    "2024-04-30",
    "2024-05-31",
    "2024-06-30",
    "2024-07-31",
    "2024-08-31",
    "2024-09-30",
    "2024-10-31",
    "2024-11-30",
    "2024-12-31",
    "2025-01-31",
    "2025-02-28",
]


# Load data
@st.cache_data
def load_data():
    file_path = "./cleaned_nav_data.xlsx"
    df = pd.read_excel(file_path, header=0)
    df = df.melt(id_vars=df.columns[0], var_name="Date", value_name="NAV")
    df.rename(columns={df.columns[0]: "Fund Name"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    return df


df = load_data()

# Initialize the DataFrame in session state if not already present
if "df" not in st.session_state:
    st.session_state["df"] = df  # Store the initial DataFrame in session state

# Print the first row of the DataFrame
if not st.session_state["df"].empty:
    print("Lasr row of the DataFrame:")
    print(st.session_state["df"].tail(5))  # Prints the first row of the DataFrame

    # Filter rows where 'Fund Name' starts with 'Aditya'
    filtered_df = st.session_state["df"][st.session_state["df"]["Fund Name"].str.startswith("Aditya", na=False)]
    print("First 5 rows where 'Fund Name' starts with 'Aditya':")
    print(filtered_df.head(5))  # Prints the first 5 rows of the filtered DataFrame


# Normalize NAV values to 10 based on the first available date
def normalize_nav(df, fund_name):
    fund_data = df[df["Fund Name"] == fund_name].copy()

    if fund_data.empty:
        st.error(f"No data available for {fund_name}.")
        return pd.DataFrame(columns=["Fund Name", "Date", "NAV"])

    # Ensure NAV column is numeric
    fund_data["NAV"] = pd.to_numeric(fund_data["NAV"], errors="coerce")

    # Filter data for dates on or after 31 October 2018
    fund_data = fund_data[fund_data["Date"] >= pd.to_datetime("2018-10-31")]

    if fund_data.empty:
        st.error(f"No data available for {fund_name} on or after 31 October 2018.")
        return pd.DataFrame(columns=["Fund Name", "Date", "NAV"])

    # Get the first available date in the filtered dataset
    first_available_date = fund_data["Date"].min()
    base_value_row = fund_data.loc[fund_data["Date"] == first_available_date]

    # Ensure base_value is numeric
    base_value = base_value_row["NAV"].values[0]

    if pd.isna(base_value):
        st.error(f"Invalid NAV value for {fund_name} on the first available date.")
        return pd.DataFrame(columns=["Fund Name", "Date", "NAV"])

    # Normalize NAV values to 10
    if base_value != 10:
        fund_data["NAV"] = fund_data["NAV"] * (10 / base_value)

    return fund_data

def get_max_starting_date(df, fund_names):
    """
    Calculate the maximum starting date for the selected funds.
    """
    max_date = None
    for fund_name in fund_names:
        fund_data = df[df["Fund Name"] == fund_name]
        if not fund_data.empty:
            fund_start_date = fund_data["Date"].min()
            if max_date is None or fund_start_date > max_date:
                max_date = fund_start_date
    return max_date

def normalize_nav_with_max_date(df, fund_name, max_start_date):
    """
    Normalize NAV values for a fund starting from the max_start_date.
    """
    fund_data = df[df["Fund Name"] == fund_name].copy()

    if fund_data.empty:
        st.error(f"No data available for {fund_name}.")
        return pd.DataFrame(columns=["Fund Name", "Date", "NAV"])

    # Ensure NAV column is numeric
    fund_data["NAV"] = pd.to_numeric(fund_data["NAV"], errors="coerce")

    # Filter data for dates on or after max_start_date
    fund_data = fund_data[fund_data["Date"] >= max_start_date]

    if fund_data.empty:
        st.error(f"No data available for {fund_name} on or after {max_start_date}.")
        return pd.DataFrame(columns=["Fund Name", "Date", "NAV"])

    # Get the first available date in the filtered dataset
    first_available_date = fund_data["Date"].min()
    base_value_row = fund_data.loc[fund_data["Date"] == first_available_date]

    # Ensure base_value is numeric
    base_value = base_value_row["NAV"].values[0]

    if pd.isna(base_value):
        st.error(f"Invalid NAV value for {fund_name} on the first available date.")
        return pd.DataFrame(columns=["Fund Name", "Date", "NAV"])

    # Normalize NAV values to 10
    if base_value != 10:
        fund_data["NAV"] = fund_data["NAV"] * (10 / base_value)

    return fund_data


# Streamlit UI
st.title("Mutual Fund NAV Comparison")

# Dropdowns for fund selection
# funds = df["Fund Name"].unique()
# fund1 = st.selectbox("Select First Fund", funds)
# fund2 = st.selectbox("Select Second Fund", funds)
# fund3 = st.selectbox("Select Third Fund", funds)
if "funds" not in st.session_state:
    st.session_state["funds"] = list(st.session_state["df"]["Fund Name"].unique())  # Initialize funds list

# Function to handle search and update dropdown and DataFrame
def handle_search():
    search_name = st.session_state.get("input_1", "")
    if search_name:
        search_results = fetch_funds(search_name)
        if search_results:
            for fund in search_results:
                fund_details = fetch_fund_by_id(fund["id"])

                # Extract fund name and NAV data
                fund_name = fund_details["fscbi_legal_name"]
                total_return_index = fund_details.get("total_return_index", [])
                print("Total Return Index:", total_return_index)  # Debugging: Print total_return_index

                # Check if NAV data exists
                if total_return_index:
                    # Convert NAV data to DataFrame
                    new_data = pd.DataFrame(total_return_index)
                    new_data.rename(columns={"d": "Date", "v": "NAV"}, inplace=True)
                    new_data["Date"] = pd.to_datetime(new_data["Date"])
                    new_data["Fund Name"] = fund_name

                    # Debugging: Print new_data before filtering
                    print("New Data Before Filtering:")
                    print(new_data)

                    # Append the new rows to the DataFrame
                    if not new_data.empty:
                        st.session_state["df"] = pd.concat(
                            [st.session_state["df"], new_data[["Fund Name", "Date", "NAV"]]],
                            ignore_index=True,
                        )
                        print("Data successfully appended to DataFrame. ", st.session_state["df"].tail())  # Debugging: Confirm data append
                    else:
                        print("No data to append after filtering.")  # Debugging: No data after filtering

                else:
                    print(f"No NAV data found for fund: {fund_name}")  # Debugging: No NAV data

                # Add fund name to the dropdown list if not already present
                if fund_name not in st.session_state["funds"]:
                    st.session_state["funds"].append(fund_name)

# Print the last rows of the DataFrame
if not st.session_state["df"].empty:
    print("Last rows of the DataFrame:")
    print(st.session_state["df"].tail(5))  # Prints the last 5 rows of the DataFrame

# First Fund
col1, col2 = st.columns([3, 1])

st.text_input("Enter Fund Name", key="input_1")
if st.button("Search", key="search_1"):
    handle_search()

fund1 = st.selectbox("Select First Fund", st.session_state["funds"], key="dropdown_1")
# with col1:
#     fund1 = st.selectbox("Select First Fund", st.session_state["funds"], key="dropdown_1")
# with col2:
#     st.text_input("Enter Fund Name", key="input_1")
#     if st.button("Search", key="search_1"):
#         handle_search()

# Second Fund
fund2 = st.selectbox("Select Second Fund", st.session_state["funds"], key="dropdown_2")

# Third Fund
fund3 = st.selectbox("Select Third Fund", st.session_state["funds"], key="dropdown_3")


# Date range filter with fallback for NaT values
def safe_date(value, fallback):
    return value if pd.notna(value) else fallback


date_range = st.date_input(
    "Select Date Range",
    [
        safe_date(st.session_state["df"]["Date"].min(), pd.to_datetime("2023-01-01")),
        safe_date(st.session_state["df"]["Date"].max(), pd.to_datetime("2025-01-31")),
    ],
)

# Calculate the maximum starting date for the selected funds
selected_funds = [fund1, fund2, fund3]
max_start_date = get_max_starting_date(st.session_state["df"], selected_funds)

# Normalize NAV values for each fund using the max_start_date
fund1_data = normalize_nav_with_max_date(st.session_state["df"], fund1, max_start_date)
fund2_data = normalize_nav_with_max_date(st.session_state["df"], fund2, max_start_date)
fund3_data = normalize_nav_with_max_date(st.session_state["df"], fund3, max_start_date)

# Filter data based on selected funds and date range
filtered_fund1 = fund1_data[
    (fund1_data["Date"] >= pd.to_datetime(date_range[0]))
    & (fund1_data["Date"] <= pd.to_datetime(date_range[1]))
]
filtered_fund2 = fund2_data[
    (fund2_data["Date"] >= pd.to_datetime(date_range[0]))
    & (fund2_data["Date"] <= pd.to_datetime(date_range[1]))
]
filtered_fund3 = fund3_data[
    (fund3_data["Date"] >= pd.to_datetime(date_range[0]))
    & (fund3_data["Date"] <= pd.to_datetime(date_range[1]))
]

# Merge data for visualization
merged_data = pd.concat([filtered_fund1, filtered_fund2, filtered_fund3])

# Plot graph
fig = px.line(
    merged_data,
    x="Date",
    y="NAV",
    color="Fund Name",
    title="Mutual Fund NAV Comparison",
    labels={"NAV": "Net Asset Value", "Date": "Date"},
)

fig.update_traces(mode="lines+markers")
fig.update_layout(hovermode="x unified")

st.plotly_chart(fig)
