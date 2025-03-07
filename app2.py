import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(layout="wide", page_title="Health Expenditure Analysis")

st.title("Health Expenditure Year-over-Year Analysis")
st.markdown("### East Asia & Pacific Lower Middle Income Countries (2006-2015)")

# Function to load and process data from a single Excel file
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is None:
        return None
    
    # Read all sheets from the Excel file
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    
    # For debugging, print the available sheets
    st.sidebar.write("Available sheets:", list(excel_data.keys()))
    
    # Look for YoY_Health_Expenditure sheet
    if 'YoY_Health_Expenditure' in excel_data:
        yoy_data = excel_data['YoY_Health_Expenditure']
        return yoy_data
    else:
        st.error("The Excel file must contain a sheet named 'YoY_Health_Expenditure'")
        return None

# Function to process data for visualization
def process_data(data):
    if data is None:
        return None, None
    
    # Make a copy of the data
    yoy_change = data.copy()
    
    # Prepare data for visualizations
    # Melt the dataframe to long format for line charts
    yoy_long = pd.melt(
        yoy_change,
        id_vars=['Country Name', 'Country Code'],
        var_name='Year',
        value_name='YoY Change (%)'
    )
    
    # Extract the year from the column name
    yoy_long['Year'] = yoy_long['Year'].str.extract(r'(\d{4})').astype(int)
    
    return yoy_change, yoy_long

# Function to display results
def display_results(yoy_change, yoy_long):
    if yoy_change is None:
        return
    
    st.markdown("### Year-over-Year Increase in Domestic Government Health Expenditure (%)")
    
    # Format the table with better styling
    st.dataframe(
        yoy_change.style.format({col: "{:.1f}%" for col in yoy_change.columns if 'YoY' in col})
                       .background_gradient(cmap='RdYlGn', subset=[col for col in yoy_change.columns if 'YoY' in col])
                       .set_properties(**{'text-align': 'center'})
                       .set_table_styles([
                           {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center')]},
                           {'selector': 'td', 'props': [('text-align', 'center')]}
                       ]),
        use_container_width=True
    )
    
    # Add visualization options
    st.markdown("### Visualizations")
    viz_type = st.selectbox(
        "Select visualization type",
        ["Line Chart - YoY Change", "Heatmap - YoY Change", "Bar Chart - Average YoY Change"]
    )
    
    selected_countries = st.multiselect(
        "Select countries to display (leave empty to show all)",
        options=yoy_change['Country Name'].tolist(),
        default=[]
    )
    
    if not selected_countries:
        filtered_data = yoy_change
        filtered_long = yoy_long
    else:
        filtered_data = yoy_change[yoy_change['Country Name'].isin(selected_countries)]
        filtered_long = yoy_long[yoy_long['Country Name'].isin(selected_countries)]
    
    # Display selected visualization
    if viz_type == "Line Chart - YoY Change":
        plot_yoy_line_chart(filtered_long)
    elif viz_type == "Heatmap - YoY Change":
        plot_yoy_heatmap(filtered_data)
    elif viz_type == "Bar Chart - Average YoY Change":
        plot_avg_bar_chart(filtered_data)

# Visualization functions
def plot_yoy_line_chart(data):
    if len(data) == 0:
        st.warning("No data available for selected countries.")
        return
    
    # Create plot
    fig = px.line(
        data,
        x='Year',
        y='YoY Change (%)',
        color='Country Name',
        markers=True,
        title='Year-over-Year Percentage Change in Health Expenditure',
        template='plotly_white'
    )
    
    fig.update_layout(
        height=600,
        legend=dict(orientation="h", y=-0.2),
        yaxis=dict(title='YoY Change (%)', showgrid=True),
        xaxis=dict(title='Year', showgrid=True, dtick=1)
    )
    
    # Add zero line for reference
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig, use_container_width=True)

def plot_yoy_heatmap(data):
    if len(data) == 0:
        st.warning("No data available for selected countries.")
        return
    
    # Prepare data for heatmap
    heatmap_data = data.set_index('Country Name')
    # Keep only the YoY columns
    yoy_cols = [col for col in heatmap_data.columns if 'YoY' in col]
    heatmap_data = heatmap_data[yoy_cols]
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(12, len(heatmap_data) * 0.8))
    
    # Create heatmap
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".1f",
        cmap="RdYlGn",
        center=0,
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "YoY Change (%)"}
    )
    
    plt.title('Heatmap of Year-over-Year Change in Health Expenditure (%)')
    plt.tight_layout()
    
    st.pyplot(fig)

def plot_avg_bar_chart(data):
    if len(data) == 0:
        st.warning("No data available for selected countries.")
        return
    
    # Calculate average YoY change for each country
    avg_data = data.copy()
    # Keep only the YoY columns
    yoy_cols = [col for col in avg_data.columns if 'YoY' in col]
    
    avg_data['Average YoY Change (%)'] = avg_data[yoy_cols].mean(axis=1)
    
    avg_data = avg_data[['Country Name', 'Average YoY Change (%)']].sort_values('Average YoY Change (%)', ascending=False)
    
    # Create bar chart
    fig = px.bar(
        avg_data,
        x='Country Name',
        y='Average YoY Change (%)',
        color='Average YoY Change (%)',
        color_continuous_scale='RdYlGn',
        title='Average Year-over-Year Change in Health Expenditure (2006-2015)',
        template='plotly_white'
    )
    
    fig.update_layout(
        height=600,
        xaxis={'categoryorder': 'total descending'},
        coloraxis_colorbar=dict(title="Avg YoY Change (%)"),
    )
    
    # Add zero line for reference
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig, use_container_width=True)

# Add file uploader in the sidebar
st.sidebar.title("Upload Data File")
st.sidebar.markdown("Please upload your Excel file with the YoY_Health_Expenditure sheet:")
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    yoy_data = load_data(uploaded_file)
    
    if yoy_data is not None:
        yoy_change, yoy_long = process_data(yoy_data)
        display_results(yoy_change, yoy_long)
else:
    st.info("Please upload an Excel file containing the YoY_Health_Expenditure sheet.")
    
    # Sample data option
    if st.sidebar.checkbox("Use sample data (for demonstration)"):
        # Create sample data for demonstration purposes
        sample_data = pd.DataFrame({
            'Country Name': ['Indonesia', 'Philippines', 'Viet Nam', 'Myanmar', 'Cambodia'],
            'Country Code': ['IDN', 'PHL', 'VNM', 'MMR', 'KHM'],
            '2006 YoY (%)': [9.7, -3.0, -1.9, 63.9, -12.0],
            '2007 YoY (%)': [13.7, -2.4, -2.0, -15.9, 26.3],
            '2008 YoY (%)': [-2.3, -3.8, 6.7, -19.3, -21.6],
            '2009 YoY (%)': [-0.3, 1.7, -3.8, 6.9, 3.4],
            '2010 YoY (%)': [-32.6, 4.1, 9.3, 13.6, 22.8],
            '2011 YoY (%)': [-0.9, -17.3, -2.3, 21.5, -13.6],
            '2012 YoY (%)': [12.1, -0.4, 8.3, 44.0, 13.6],
            '2013 YoY (%)': [8.1, -0.3, 12.4, 9.6, 3.1],
            '2014 YoY (%)': [17.6, 30.1, -10.9, 28.1, -7.4],
            '2015 YoY (%)': [18.2, 10.4, -0.4, -9.1, 17.3]
        })
        
        yoy_change, yoy_long = process_data(sample_data)
        display_results(yoy_change, yoy_long)
    
# Add documentation to the sidebar
with st.sidebar.expander("Documentation"):
    st.markdown("""
    ### About this Application
    
    This application analyzes year-over-year increases in domestic government health expenditure for East Asia & Pacific Lower Middle Income Countries.
    
    ### Required Excel Sheet
    
    Your Excel file should contain a sheet named 'YoY_Health_Expenditure' with the following columns:
    - Country Name
    - Country Code
    - Year columns in the format "YYYY YoY (%)" - e.g., "2006 YoY (%)"
    
    ### Visualization Options
    
    - **Line Chart - YoY Change**: Shows the year-over-year percentage change for each country
    - **Heatmap - YoY Change**: Displays a color-coded matrix of all values
    - **Bar Chart - Average YoY Change**: Compares the average change across countries
    
    ### Countries
    
    You can select specific countries to focus on using the "Select countries to display" dropdown.
    """)

# Add footer
st.markdown("---")
st.markdown("### Health Expenditure Analysis Dashboard | Created with Streamlit")