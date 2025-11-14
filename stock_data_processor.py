import pandas as pd
import numpy as np
import os
import sqlite3
from sqlalchemy import create_engine

# --- Configuration Data (Simulating a Separate Sector CSV/DB Table) ---

# This list contains all 50 Nifty stock symbols required for analysis.
NIFTY_50_SYMBOLS =['ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJAJFINSV', 'BAJFINANCE', 'BEL', 'BHARTIARTL', 'BPCL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'INDUSINDBK', 'INFY', 'ITC', 'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SBIN', 'SHRIRAMFIN', 'SUNPHARMA', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TCS', 'TECHM', 'TITAN', 'TRENT', 'ULTRACEMCO', 'WIPRO']

# Sector mapping for the 50 stocks (Required for Sector Analysis)
SECTOR_MAPPING ={'ADANIENT':'MISCELLANEOUS', 'ADANIPORTS':'MISCELLANEOUS', 'APOLLOHOSP':'MISCELLANEOUS', 'ASIANPAINT':'PAINTS', 'AXISBANK':'BANKING', 'BAJAJ-AUTO':'AUTOMOBILES', 'BAJAJFINSV':'FINANCE', 'BAJFINANCE':'FINANCE', 'BEL':'DEFENCE', 'BHARTIARTL':'TELECOM', 'BPCL':'ENERGY', 'BRITANNIA':'FOOD & TOBACCO', 'CIPLA':'PHARMACEUTICALS', 'COALINDIA':'MINING', 'DRREDDY':'PHARMACEUTICALS', 'EICHERMOT':'AUTOMOBILES', 'GRASIM':'TEXTILES', 'HCLTECH':'SOFTWARE', 'HDFCBANK':'BANKING', 'HDFCLIFE':'INSURANCE', 'HEROMOTOCO':'AUTOMOBILES', 'HINDALCO':'ALUMINIUM', 'HINDUNILVR':'FMCG', 'ICICIBANK':'BANKING', 'INDUSINDBK':'BANKING', 'INFY':'SOFTWARE', 'ITC':'FOOD & TOBACCO', 'JSWSTEEL':'STEEL', 'KOTAKBANK':'BANKING', 'LT':'ENGINEERING', 'M&M':'AUTOMOBILES', 'MARUTI':'AUTOMOBILES', 'NESTLEIND':'FOOD & TOBACCO', 'NTPC':'POWER', 'ONGC':'ENERGY', 'POWERGRID':'POWER', 'RELIANCE':'ENERGY', 'SBILIFE':'INSURANCE', 'SBIN':'BANKING', 'SHRIRAMFIN':'FINANCE', 'SUNPHARMA':'PHARMACEUTICALS', 'TATACONSUM':'FMCG', 'TATAMOTORS':'AUTOMOBILES', 'TATASTEEL':'STEEL', 'TCS':'SOFTWARE', 'TECHM':'SOFTWARE', 'TITAN':'RETAILING', 'TRENT':'RETAILING', 'ULTRACEMCO':'CEMENT', 'WIPRO':'SOFTWARE'}

# --- Core ETL and Data Loading Functions ---

def load_master_data_from_csvs(csv_directory="CSV_Output"):
    """
    Reads the 50 symbol-based CSV files, cleans the data, and combines them
    into a single Master DataFrame ready for analysis.
    """
    if not os.path.exists(csv_directory):
        raise FileNotFoundError(
            f"CSV directory not found: '{csv_directory}'. Please ensure your "
            f"50 CSV files are in a folder with this exact name."
        )

    all_dfs = []
    
    required_price_cols = ['open', 'high', 'low', 'close', 'volume']
    
    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(csv_directory, filename)
            try:
                df = pd.read_csv(filepath)
                
                # 1. Symbol/Ticker handling
                if 'Ticker' in df.columns:
                    df = df.rename(columns={'Ticker': 'Symbol'})
                elif 'Symbol' not in df.columns:
                    symbol = filename.replace('.csv', '').split('_')[0]
                    df['Symbol'] = symbol

                if not all(col in df.columns for col in ['date'] + required_price_cols):
                    raise ValueError(f"File {filename} is missing required columns. Found: {df.columns.tolist()}")

                # 2. Data Type Conversion & Cleanup
                for col in required_price_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df['Date'] = pd.to_datetime(df['date'], errors='coerce')
                
                df = df.drop(columns=['date', 'month'], errors='ignore')
                
                df = df.dropna(subset=['Date', 'close'])
                
                all_dfs.append(df)

            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue

    if not all_dfs:
        raise ValueError("No valid stock data could be loaded from the CSV directory.")

    # 3. Concatenate all DataFrames
    master_df = pd.concat(all_dfs, ignore_index=True)
    master_df = master_df.sort_values(by=['Symbol', 'Date']).reset_index(drop=True)

    # 4. Add Sector Data
    master_df['Sector'] = master_df['Symbol'].map(SECTOR_MAPPING)
    
    # 5. Calculate Daily Return (Crucial for all further analysis)
    master_df['Prev_Close'] = master_df.groupby('Symbol')['close'].shift(1)
    # The return calculation uses .fillna(0) for the very first day's NaN return
    master_df['Daily_Return'] = ((master_df['close'] - master_df['Prev_Close']) / master_df['Prev_Close']).fillna(0)

    master_df = master_df.drop(columns=['Prev_Close'])

    return master_df

# --- Core Analysis Functions (Refactored for Cleanliness) ---

def calculate_yearly_performance(df):
    """
    Calculates Yearly Return and Annualized Volatility for all stocks, 
    combining them into a single performance DataFrame.
    """
    
    # 1. Yearly Return Calculation
    first_close = df.groupby('Symbol')['close'].first()
    last_close = df.groupby('Symbol')['close'].last()
    yearly_return = ((last_close - first_close) / first_close) * 100
    
    # 2. Annualized Volatility Calculation
    daily_volatility = df.groupby('Symbol')['Daily_Return'].std()
    # Volatility is Std Dev of Daily Returns * sqrt(252 trading days) * 100 to get percent
    annualized_volatility = (daily_volatility * np.sqrt(252) * 100).round(2)
    
    # 3. Combine into master performance DF (This is the YearlyPerformance table for SQL)
    performance_df = pd.DataFrame({
        'Yearly Return (%)': yearly_return.round(2),
        'Annualized Volatility (%)': annualized_volatility
    })
    
    # 4. Generate summary rankings/counts
    top_10_gainers = performance_df.sort_values(by='Yearly Return (%)', ascending=False).head(10)
    top_10_losers = performance_df.sort_values(by='Yearly Return (%)', ascending=True).head(10)
    top_10_volatile = performance_df.sort_values(by='Annualized Volatility (%)', ascending=False).head(10)
    
    green_stocks = performance_df[performance_df['Yearly Return (%)'] > 0]
    red_stocks = performance_df[performance_df['Yearly Return (%)'] <= 0]
    
    # Returning the full DF along with the subsets
    return performance_df, top_10_gainers, top_10_losers, top_10_volatile, green_stocks, red_stocks


def get_market_summary(df, green_stocks, red_stocks):
    """
    Calculates overall market metrics.
    """
    total_stocks = df['Symbol'].nunique()
    green_count = len(green_stocks)
    red_count = len(red_stocks)
    
    avg_price = df['close'].mean()
    avg_volume = df['volume'].mean()

    # NOTE: This will be saved as the 'MarketSummary' table
    return pd.Series({
        'Total Stocks': total_stocks,
        'Green Stocks': green_count,
        'Red Stocks': red_count,
        'Avg Close Price (₹)': f"{avg_price:,.2f}",
        'Avg Daily Volume': f"{avg_volume:,.0f}",
        'Green Percent': f"{(green_count / total_stocks) * 100:.1f}%"
    })


def get_cumulative_returns(df, top_n=5):
    """
    Calculates the cumulative return over the year for the top N performers.
    """
    # 1. Find the top N symbols based on the total return (first-to-last close)
    first_close = df.groupby('Symbol')['close'].first()
    last_close = df.groupby('Symbol')['close'].last()
    total_return = ((last_close - first_close) / first_close)
    top_performers_symbols = total_return.nlargest(top_n).index

    # 2. Filter data for only those top performers
    top_df = df[df['Symbol'].isin(top_performers_symbols)].copy()
    
    # 3. Calculate cumulative return using cumprod
    top_df['Cumulative_Return'] = top_df.groupby('Symbol')['Daily_Return'].transform(
        lambda x: (1 + x).cumprod()
    )
    
    # Select and format results for plotting
    cumulative_returns_df = top_df[['Symbol', 'Date', 'Cumulative_Return']].reset_index(drop=True)
    
    return cumulative_returns_df

def get_sector_performance(df, yearly_performance_df):
    """
    Calculates the average yearly return for each sector.
    """
    # 1. Map sector to each stock's return using the full yearly performance DF
    stock_returns_df = yearly_performance_df[['Yearly Return (%)']].copy()
    stock_returns_df['Sector'] = stock_returns_df.index.map(SECTOR_MAPPING)
    
    # 2. Calculate the average return per sector
    sector_avg_return = stock_returns_df.groupby('Sector')['Yearly Return (%)'].mean().round(2)
    
    # NOTE: This will be saved as the 'SectorPerformance' table
    return sector_avg_return.to_frame(name='Avg Yearly Return (%)')

def get_correlation_matrix(df):
    """
    Calculates the correlation matrix of daily closing prices.
    """
    pivot_df = df.pivot(index='Date', columns='Symbol', values='close')
    correlation_matrix = pivot_df.corr().round(2)
    return correlation_matrix

def get_monthly_performance(df):
    """
    Calculates the monthly return for all stocks and identifies top 5 gainers/losers.
    
    NOTE: This will be saved as the 'MonthlyRanking' table
    """
    # Calculate the first and last day close price for each month and symbol
    monthly_prices = df.groupby(['Symbol', pd.Grouper(key='Date', freq='ME')])['close'].agg(['first', 'last'])
    
    # Calculate Monthly Return
    monthly_prices['Monthly_Return'] = (monthly_prices['last'] - monthly_prices['first']) / monthly_prices['first']
    
    monthly_prices = monthly_prices.reset_index()

    monthly_ranking = []
    
    for month, group in monthly_prices.groupby(pd.Grouper(key='Date', freq='ME')):
        top_gainers = group.nlargest(5, 'Monthly_Return').copy()
        top_gainers['Type'] = 'Top_Gainers'
        monthly_ranking.append(top_gainers)
        
        top_losers = group.nsmallest(5, 'Monthly_Return').copy()
        top_losers['Type'] = 'Top_Losers'
        monthly_ranking.append(top_losers)

    if not monthly_ranking:
        return pd.DataFrame()

    monthly_ranking_df = pd.concat(monthly_ranking, ignore_index=True)

    monthly_ranking_df['Month_Year'] = monthly_ranking_df['Date'].dt.strftime('%Y-%m')
    
    monthly_ranking_df = monthly_ranking_df[['Symbol', 'Month_Year', 'Monthly_Return', 'Type']]
    monthly_ranking_df['Monthly_Return'] = (monthly_ranking_df['Monthly_Return'] * 100).round(2)
    
    return monthly_ranking_df

# --- Persistence Functions (FIXED) ---

def save_all_analysis_to_sql(master_df, market_summary_series, yearly_performance_df, sector_performance_df, monthly_ranking_df, db_name="stock_analysis.db"):
    """
    FIXED: Saves ALL five analysis dataframes to the SQLite database.
    """
    try:
        engine = create_engine(f'sqlite:///{db_name}')

        # 1. Master Raw Data (The biggest table)
        master_df.to_sql('master_stock_data', engine, if_exists='replace', index=False, chunksize=1000)

        # 2. Yearly Performance (Returns and Volatility)
        yearly_performance_df.to_sql('YearlyPerformance', engine, if_exists='replace')
        
        # 3. Sector Analysis
        sector_performance_df.to_sql('SectorPerformance', engine, if_exists='replace')

        # 4. Monthly Ranking
        monthly_ranking_df.to_sql('MonthlyRanking', engine, if_exists='replace', index=False)
        
        # 5. Summary Metrics (Convert Series to a DataFrame row before saving)
        market_summary_series.to_frame('Value').T.to_sql('MarketSummary', engine, if_exists='replace', index=False)
        
        print(f"Successfully saved 5 tables to {db_name}")
        return True
    except Exception as e:
        print(f"SQL Database Save Error: {e}")
        return False

def export_master_csv(df, filename="master_stock_data.csv"):
    """
    Exports the clean Master DataFrame for Power BI, fulfilling the Power BI data source deliverable.
    """
    try:
        df.to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"CSV Export Error: {e}")
        return False

# --- Main Execution Function (UPDATED) ---

def run_full_etl_and_analysis():
    """
    Runs the entire pipeline: Load -> Clean -> SQL Save -> CSV Export -> Analysis.
    Returns all necessary DataFrames and metrics for the Streamlit dashboard.
    """
    # 1. Load and Clean Master Data
    master_df = load_master_data_from_csvs()

    # 2. Core Analysis Functions
    # Calculate performance and extract the full performance DF
    yearly_performance_df, top_10_gainers, top_10_losers, top_10_volatile, green_stocks, red_stocks = calculate_yearly_performance(master_df)
    
    market_summary_series = get_market_summary(master_df, green_stocks, red_stocks)
    
    cumulative_returns_df = get_cumulative_returns(master_df)
    
    sector_performance_df = get_sector_performance(master_df, yearly_performance_df)
    
    correlation_matrix = get_correlation_matrix(master_df)
    
    monthly_ranking_df = get_monthly_performance(master_df)

    # 3. Persistence Step (FIXED to save all 5 tables)
    save_all_analysis_to_sql(
        master_df,
        market_summary_series,
        yearly_performance_df,
        sector_performance_df,
        monthly_ranking_df
    )
    
    export_master_csv(master_df)

    # 4. Return all necessary DataFrames for the Streamlit dashboard
    return (
        master_df,
        market_summary_series,
        top_10_gainers,
        top_10_losers,
        top_10_volatile,
        cumulative_returns_df,
        sector_performance_df,
        correlation_matrix,
        monthly_ranking_df
    )