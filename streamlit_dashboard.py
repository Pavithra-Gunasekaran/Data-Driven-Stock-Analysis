import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Append the current directory to sys.path so we can import the processor script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all functions from the data processor script
try:
    from stock_data_processor import run_full_etl_and_analysis
except ImportError:
    st.error("Error: Could not find 'stock_data_processor.py'. Please ensure both files are in the same directory.")
    st.stop()

# --- Streamlit Configuration ---
st.set_page_config(
    page_title="Data-Driven Nifty 50 Stock Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Caching the Full Pipeline Run ---
# The @st.cache_data decorator ensures the expensive ETL and analysis functions
# only run once, making the dashboard fast on subsequent interactions.
@st.cache_data(show_spinner="Running full ETL, Analysis, and SQL/CSV Export...")
def load_and_analyze_data():
    """Wrapper to run the full pipeline from the processor script."""
    return run_full_etl_and_analysis()

# --- Main Dashboard Logic ---

st.title("📈 Nifty 50 Performance Dashboard (Last Year)")
st.caption("Data Processing, Analysis, and Visualization via Pandas, SQLAlchemy (SQLite), and Streamlit")

# --- Run Pipeline and Handle Errors ---
data_loaded = False
# Initialize variables to prevent NameError in case of partial failure
df = None
market_summary = None
top_10_gainers = None
top_10_losers = None
top_10_volatile = None
cumulative_returns_df = None
sector_performance_df = None
correlation_matrix = None
monthly_ranking_df = None

try:
    # Attempt to run the entire pipeline
    (
        df,
        market_summary,
        top_10_gainers,
        top_10_losers,
        top_10_volatile,
        cumulative_returns_df,
        sector_performance_df,
        correlation_matrix,
        monthly_ranking_df
    ) = load_and_analyze_data()
    data_loaded = True
except FileNotFoundError as e:
    st.error(f"CRITICAL ERROR: {e}")
    st.warning("Please create a folder named '50_stock_csvs' and place your cleaned stock CSV files inside it.")
except ValueError as e:
    st.error(f"CRITICAL DATA ERROR: {e}")
    st.warning("Data loading failed. Please check if your CSV files are formatted correctly (Ticker/date/close/etc.) and if there's enough data.")
except Exception as e:
    st.error(f"CRITICAL ANALYSIS FAILURE: An unexpected error occurred during processing. See details below.")
    st.exception(e)
    # Stop the script execution here if a critical error occurred
    st.stop()


if data_loaded:
    # --- SECTION 1: Market Overview & Key Metrics ---
    st.header("1. Market Overview & Summary")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Total Stocks Analyzed", market_summary['Total Stocks'], delta=None)
    col2.metric("Green Stocks", market_summary['Green Stocks'], delta=None)
    col3.metric("Red Stocks", market_summary['Red Stocks'], delta=None)
    col4.metric("Avg Close Price", market_summary['Avg Close Price (₹)'], delta=None)
    col5.metric("Avg Daily Volume", market_summary['Avg Daily Volume'], delta=None)
    col6.metric("Green Stocks Percentage", market_summary['Green Percent'], 
                delta=f"{market_summary['Green Stocks']} Gainer(s)")

    st.markdown("---")

    # --- SECTION 2: Stock Performance Ranking ---
    st.header("2. Yearly Stock Performance Ranking")

    col_gainer, col_loser = st.columns(2)

    with col_gainer:
        st.subheader("🏆 Top 10 Best Performing Stocks (Gainers)")
        # Display index (Symbol) and the value
        top_10_gainers.index.name = "Symbol"
        st.dataframe(top_10_gainers, width='stretch')

    with col_loser:
        st.subheader("📉 Top 10 Worst Performing Stocks (Losers)")
        top_10_losers.index.name = "Symbol"
        st.dataframe(top_10_losers, width='stretch')

    st.markdown("---")

    # --- SECTION 3: Volatility and Sector Analysis ---
    st.header("3. Risk and Sector Breakdown")

    col_volatility, col_sector = st.columns(2)

    with col_volatility:
        st.subheader("Top 10 Most Volatile Stocks")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Use a contrasting color for volatility
        sns.barplot(y=top_10_volatile.index, x='Annualized Volatility (%)', data=top_10_volatile, 
            hue=top_10_volatile.index, palette="Reds_r", legend=False, ax=ax)
        ax.set_title("Annualized Volatility (Risk Assessment)", fontsize=16)
        ax.set_xlabel("Volatility (%)")
        ax.set_ylabel("Stock Symbol")
        st.pyplot(fig)
        st.caption("Volatility is measured by the annualized standard deviation of daily returns. Higher % = Higher Risk.")

    with col_sector:
        st.subheader("Average Yearly Return by Sector")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # FIX: Convert the calculated color Series to a list before passing to palette
        sector_performance_df['Color'] = sector_performance_df['Avg Yearly Return (%)'].apply(lambda x: 'g' if x > 0 else 'r')
        sns.barplot(y=sector_performance_df.index, x='Avg Yearly Return (%)', data=sector_performance_df, 
            hue=sector_performance_df.index, palette=sector_performance_df['Color'].tolist(), legend=False, ax=ax)
        ax.set_title("Sector Performance Snapshot", fontsize=16)
        ax.set_xlabel("Average Yearly Return (%)")
        ax.set_ylabel("Sector")
        
        st.pyplot(fig)
        st.caption("Gauges overall health and sentiment across key market industries.")
        
    st.markdown("---")

    # --- SECTION 4: Cumulative Return and Correlation ---
    st.header("4. Growth and Inter-Stock Relationships")

    col_cumulative, col_correlation = st.columns(2)

    with col_cumulative:
        st.subheader("Cumulative Return for Top 5 Performers")
        fig, ax = plt.subplots(figsize=(10, 6))

        # Use Seaborn lineplot for clear visualization over time
        sns.lineplot(x='Date', y='Cumulative_Return', hue='Symbol', data=cumulative_returns_df, ax=ax)
        
        ax.set_title("Top 5 Stocks: Cumulative Growth Over Time", fontsize=16)
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Return (decimal)")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)
        st.caption("Visualizing the continuous growth of the best-performing stocks.")

    with col_correlation:
        st.subheader("Stock Price Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Use Seaborn heatmap for correlation matrix
        # Annotate=False is used here to prevent clutter with 50 stocks
        sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', fmt=".2f", 
                    cbar_kws={'label': 'Correlation Coefficient'}, ax=ax)
        ax.set_title("Closing Price Correlation Matrix", fontsize=16)
        ax.tick_params(axis='x', rotation=90)
        ax.tick_params(axis='y', rotation=0)
        st.pyplot(fig)
        st.caption("Darker colors indicate higher correlation (stocks moving together).")

    st.markdown("---")

    # --- SECTION 5: Monthly Analysis (Interactive) ---
    st.header("5. Monthly Gainers and Losers (Granular Trend)")

    # Get a list of unique Month_Year values for the select box
    months = monthly_ranking_df['Month_Year'].unique()
    
    # Use st.selectbox for user interaction
    selected_month = st.selectbox(
        "Select Month for Granular Analysis:",
        options=sorted(months, reverse=True),
        help="Choose a month to see the top 5 gainers and losers for that specific period."
    )

    # Filter the DataFrame based on the selection
    if selected_month:
        monthly_data = monthly_ranking_df[monthly_ranking_df['Month_Year'] == selected_month]
        
        # Split the monthly data into gainers and losers
        gainers = monthly_data[monthly_data['Type'] == 'Top_Gainers'].sort_values('Monthly_Return', ascending=False)
        losers = monthly_data[monthly_data['Type'] == 'Top_Losers'].sort_values('Monthly_Return', ascending=True)

        col_monthly_gainer, col_monthly_loser = st.columns(2)

        with col_monthly_gainer:
            st.subheader(f"🚀 {selected_month} Top 5 Gainers")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(y='Symbol', x='Monthly_Return', data=gainers, hue='Symbol', palette="Greens_d",legend=False, ax=ax)
            ax.set_title(f"Gainers (% Return)", fontsize=14)
            ax.set_xlabel("Monthly Return (%)")
            ax.set_ylabel("Symbol")
            st.pyplot(fig)
            
        with col_monthly_loser:
            st.subheader(f"🔻 {selected_month} Top 5 Losers")
            fig, ax = plt.subplots(figsize=(8, 5))
            # Multiply by -1 to show losses as positive bars for better comparison layout
            losers['Monthly_Return_Abs'] = losers['Monthly_Return'] * -1 
            sns.barplot(y='Symbol', x='Monthly_Return_Abs', data=losers, hue='Symbol', palette="Reds_d", legend=False, ax=ax)
            ax.set_title(f"Losers (Absolute % Loss)", fontsize=14)
            ax.set_xlabel("Monthly Loss (Absolute %)")
            ax.set_ylabel("Symbol")
            st.pyplot(fig)

    st.markdown("---")
    st.info("Files Generated: 'stock_analysis.db' (SQL Database) and 'master_stock_data.csv' (Power BI Source) are available in this directory.")