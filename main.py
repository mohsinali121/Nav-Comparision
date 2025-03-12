import streamlit as st
import pandas as pd
import plotly.express as px


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


# Normalize NAV values to 10 based on the first available date
def normalize_nav(df, fund_name):
    fund_data = df[df["Fund Name"] == fund_name].copy()

    if fund_data.empty:
        st.error(f"No data available for {fund_name}.")
        return pd.DataFrame(columns=["Fund Name", "Date", "NAV"])

    # Get the first available date in the dataset
    first_available_date = fund_data["Date"].min()
    base_value_row = fund_data.loc[fund_data["Date"] == first_available_date]

    base_value = base_value_row["NAV"].values[0]

    if base_value != 10:
        fund_data["NAV"] = fund_data["NAV"] * (10 / base_value)
    return fund_data


# Streamlit UI
st.title("Mutual Fund NAV Comparison")

# Dropdowns for fund selection
funds = df["Fund Name"].unique()
fund1 = st.selectbox("Select First Fund", funds)
fund2 = st.selectbox("Select Second Fund", funds)
fund3 = st.selectbox("Select Third Fund", funds)


# Date range filter with fallback for NaT values
def safe_date(value, fallback):
    return value if pd.notna(value) else fallback


date_range = st.date_input(
    "Select Date Range",
    [
        safe_date(df["Date"].min(), pd.to_datetime("2023-01-01")),
        safe_date(df["Date"].max(), pd.to_datetime("2025-01-31")),
    ],
)

# Filter data based on selected funds and date range
fund1_data = normalize_nav(df, fund1)
fund2_data = normalize_nav(df, fund2)
fund3_data = normalize_nav(df, fund3)

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
