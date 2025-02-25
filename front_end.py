import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
#dotenv_path = os.path.join(os.path.dirname(__file__), 'cred.env')
#load_dotenv(dotenv_path)

# Get connection string from Streamlit Secrets
conn_str = st.secrets["CONN_STR"]

# Get the connection string
conn_str = os.getenv("CONN_STR")


# Ensure the variable is loaded correctly
if not conn_str:
    raise ValueError("Database connection string is missing. Check your .env file.")


# Establish the pyodbc connection
conn = pyodbc.connect(conn_str)

# Query the database to get the full dataset
query = """SELECT f.Date,f.Outlet,f.Predicted_Sales,f.Section, s.Sales as Actual_Sales FROM [Analytics].[dbo].[Pulse_OutletRevenueForecast] f
LEFT JOIN [Analytics].[dbo].[Pulse_Live_Sales] s
ON f.Outlet = s.Outlet
AND f.Date = s.Date
ORDER BY f.Date, f.Outlet asc;"""

df = pd.read_sql(query, conn)

# Convert the 'Date' column to datetime if it's not already
df['Date'] = pd.to_datetime(df['Date'])

# Close the connection
conn.close()

# Streamlit UI
st.title("Revenue Prediction Machine Learning Model 😎")

# Get unique outlets for the dropdown
outlets = df['Outlet'].unique().tolist()
section = df['Section'].unique().tolist()

# Create a dropdown for outlet selection
selected_outlet = st.selectbox("Select Outlet", outlets)
selected_section = st.selectbox("Select Section", section)

# Create date input widgets for start and end dates
start_date = st.date_input("Select Start Date", min_value=df['Date'].min().date(), max_value=df['Date'].max().date(), value=df['Date'].min().date())
end_date = st.date_input("Select End Date", min_value=df['Date'].min().date(), max_value=df['Date'].max().date(), value=df['Date'].max().date())

# Convert Streamlit date inputs to pandas datetime for comparison
start_date_dt = pd.to_datetime(start_date)
end_date_dt = pd.to_datetime(end_date)

# Filter the dataframe based on the selected outlet and date range
filtered_df = df[
    (df['Outlet'] == selected_outlet) &
    (df['Section'] == selected_section) &  
    (df['Date'] >= start_date_dt) &
    (df['Date'] <= end_date_dt)
]

# Display the filtered data
if not filtered_df.empty:
    st.dataframe(filtered_df)
    st.write(f"Showing predictions trend for {selected_outlet} from {start_date} to {end_date}.")

    # Create a single line chart for both Predicted_Sales and Actual_Sales
    chart_data = filtered_df.set_index('Date')[['Predicted_Sales', 'Actual_Sales']]
    st.line_chart(data=chart_data)
else:
    st.write("No data available for the selected outlet and date range.")

