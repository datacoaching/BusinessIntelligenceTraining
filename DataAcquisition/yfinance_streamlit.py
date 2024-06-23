import streamlit as st
import yfinance as yf
import pandas as pd
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Define the current date
curr_date = datetime.now()

# Calculate the prior day
end_date = datetime.now() - relativedelta(days=1)

# Calculate the start date (5 years of history)
start_date = end_date - relativedelta(years=5)

# Calculate the last day of the prior month
end_date_last_month = (datetime(curr_date.year, curr_date.month, 1) - relativedelta(days=1)).replace(hour=23, minute=59, second=59)

# Calculate the first day of the month 2 months ago
start_date_prior_month = (datetime(end_date_last_month.year, end_date_last_month.month, 1) - relativedelta(months=1))

# Hard-coded list of column names
columns = ['Open', 'High', 'Low', 'Close', 'Volume']
default_metrics = ['High', 'Close']

# Streamlit App Title
st.title("Stock Price History")

# Stock symbol input
ticker = st.text_input("Enter Stock Symbol (e.g., AAPL, GOOGL, MSFT, NVDA):", value="NVDA")

selected_metrics = st.multiselect("Select Metrics to Plot:", columns, default=default_metrics)

# Convert start_date and end_date to date objects for comparison
start_date_date = start_date.date()
end_date_date = end_date.date()

# Create two columns
col1, col2 = st.columns(2)

# Place the KPI card for open price change
with col1:
    # Date picker for selecting start date
    selected_start_date = st.date_input('Select Start Date:',
                                        value=start_date_date,
                                        min_value=start_date_date, # - timedelta(days=365),  # Example: allow selecting up to 1 year back
                                        max_value=end_date_date)

with col2:
    # Date picker for selecting end date
    selected_end_date = st.date_input('Select End Date:',
                                      value=end_date_date,
                                      min_value=start_date_date,
                                      max_value=end_date_date)

# Convert selected dates back to datetime objects for further processing if needed
selected_start_datetime = datetime.combine(selected_start_date, datetime.min.time())
selected_end_datetime = datetime.combine(selected_end_date, datetime.max.time())

# Attempt to download data for the last 5 years
data = yf.download(ticker, start=start_date, end=end_date)

# Ensure start date is before end date
if selected_start_date > selected_end_date:
    st.error('Error: End date must be after start date.')
else:
    # Fetch historical data based on selected date range
    sub_data = data[(data.index >= selected_start_datetime) & (data.index <= selected_end_datetime)]

monthly_comparison = data[(data.index >= start_date_prior_month) & (data.index <= end_date_last_month)]

# Resample data on a monthly basis with custom aggregation functions
custom_aggregation = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Adj Close': 'last',
    'Volume': 'sum'
}

# Resample data on a monthly basis, applying custom aggregate functions from above
monthly_comparison_resampled = monthly_comparison.resample('M').agg(custom_aggregation)

# Sort the DataFrame by index (dates) in ascending order (if not already sorted)
monthly_comparison_resampled = monthly_comparison_resampled.sort_index()

# Get the row indices for the most recent and prior months
latest_index = -1  # Index of the latest month (last row after sorting)
prior_index = -2   # Index of the prior month (second last row after sorting)

# Extract the values for Open, High, Low, Close for the most recent month
open_recent = monthly_comparison_resampled.iloc[latest_index]['Open']
high_recent = monthly_comparison_resampled.iloc[latest_index]['High']
low_recent = monthly_comparison_resampled.iloc[latest_index]['Low']
close_recent = monthly_comparison_resampled.iloc[latest_index]['Close']

# Extract the values for Open, High, Low, Close for the prior month
open_prior = monthly_comparison_resampled.iloc[prior_index]['Open']
high_prior = monthly_comparison_resampled.iloc[prior_index]['High']
low_prior = monthly_comparison_resampled.iloc[prior_index]['Low']
close_prior = monthly_comparison_resampled.iloc[prior_index]['Close']

#monthly_comparison_resampled

if math.isnan(open_prior):
            open_growth = 'n/a'
            open_delta_color = 'off'
else:
    open_growth = f'{(open_recent / open_prior) - 1:,.2f}%'
    open_delta_color = 'normal'

if math.isnan(low_prior):
            low_growth = 'n/a'
            low_delta_color = 'off'
else:
    low_growth = f'{(low_recent / low_prior) - 1:,.2f}%'
    low_delta_color = 'normal'

if math.isnan(high_prior):
            high_growth = 'n/a'
            high_delta_color = 'off'
else:
    high_growth = f'{(high_recent / high_prior) - 1:,.2f}%'
    high_delta_color = 'normal'

if math.isnan(close_prior):
            close_growth = 'n/a'
            close_delta_color = 'off'
else:
    close_growth = f'{(close_recent / close_prior) - 1:,.2f}%'
    close_delta_color = 'normal'

# Format the dates to be printed in Streamlit
formatted_strt = start_date_prior_month.strftime("%b %Y")
formatted_end = end_date_last_month.strftime("%b %Y")

st.header(f"Monthly \u0394 for {ticker}: {formatted_strt} - {formatted_end}", divider='gray')

''

# Create two columns
#col1a, col2a, col3a, col4a = st.columns(4)
# Adjust the number of empty columns on each side to center the main content
left_empty_col, col1a, col2a, col3a, col4a, right_empty_col = st.columns([0.5, 2, 2, 2, 2, 0.5])

# Place the KPI card for open price change
with col1a:
    st.metric(
        label=f'{ticker} Open Price',
        value=f'{open_recent:,.2f}',
        delta=open_growth,
        delta_color=open_delta_color
    )

# Place the KPI card for low price change
with col2a:
    st.metric(
        label=f'{ticker} Low Price',
        value=f'{low_recent:,.2f}',
        delta=low_growth,
        delta_color=low_delta_color
    )

# Place the KPI card for high price change
with col3a:
    st.metric(
        label=f'{ticker} High Price',
        value=f'{high_recent:,.2f}',
        delta=high_growth,
        delta_color=high_delta_color
    )

# Place the KPI card for close price change
with col4a:
    st.metric(
        label=f'{ticker} Close Price',
        value=f'{close_recent:,.2f}',
        delta=close_growth,
        delta_color=close_delta_color
    )

# Melt DataFrame to pivot all columns into rows except 'Date'
data_melted = (sub_data
               .reset_index()
               .melt(id_vars='Date', var_name='Metric', value_name='Value')
               .set_index('Date')
              )

# Filter the data
filtered_data_melted = data_melted[
    (data_melted['Metric'].isin(selected_metrics))
]

# Format the dates to be printed in Streamlit
formatted_selected_strt = selected_start_datetime.strftime("%b %Y")
formatted_selected_end = selected_end_datetime.strftime("%b %Y")

st.header(f"Price History for {ticker}: {formatted_selected_strt} - {formatted_selected_end}", divider='gray')

''

st.line_chart(
    filtered_data_melted,
    y='Value',
    color='Metric',
)