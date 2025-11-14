📈 Financial Performance Analysis Dashboard
A Dual-Component Project for Dynamic Financial Reporting & Automation

This project delivers a complete end-to-end financial analytics system, combining Power BI’s interactive reporting with Python + Streamlit’s automation capabilities.
It is designed to analyze stock market data, generate insights, and produce automated web-based financial reports.

🛠️ Technologies Used
Category	Tools	                 Purpose
Core Language	Python	               - ETL, data processing, Streamlit app logic,
Database	MySQL / PostgreSQL     - Storage for historical stock data,
Processing	Pandas	               - Data manipulation and metric generation,
	        SQLAlchemy	       - Database connection and ORM,
Visualization	Power BI	       - Interactive dashboards, DAX modelling,
	        Streamlit	       - Automated reporting interface,
Libraries	Matplotlib	       - Static charts for historical trend analysis.
🧩 Data Engineering Contribution (My Work)
✅ Converted 200 YAML files into 50 clean, structured CSV datasets

As part of the data preparation pipeline, I performed a major transformation task:

Extracted data from 200+ raw YAML files

Cleaned, validated, and formatted all fields

Consolidated and optimized them into 50 final CSV files

Ensured schema consistency across all resulting datasets

Prepared them for Power BI + Python processing

This conversion significantly improved data quality and reduced preprocessing time for analytics.

📊 1. Power BI Dashboard – Interactive Visualization

The Power BI dashboard (Stock_data.pbix)file allows interactive exploration of monthly and yearly stock performance.

Visual Components

Clustered Bar Chart – Dynamic Top 5 Gainers & Bottom 5 Losers

Month Hierarchy Slicer – Easy time filtering

Card Visuals – Avg. Price (All Time), Avg. Volume (All Time)

Multi-Row Card – Total Stocks, Green Stocks, Red Stocks

⭐ Key DAX Engineering Highlights
🔹 Reliable Top/Bottom 5 Ranking

Implemented using RANKX

More stable than native "Top N" filter

🔹 Accurate Monthly Return Calculation

Uses FIRSTNONBLANK and LASTNONBLANK

Handles weekends & missing dates

🔹 Yearly Performance Summary

Uses SELECTEDVALUE + ALL()

Ensures correct calculation per stock symbol

🐍 2. Python + Streamlit Application – Automated Reporting

The Streamlit application (streamlit_financial_dashboard.py) processes stock data and displays automated insights.

Visual Components
📌 Metric Cards (st.metric)

Average Close Price

Average Daily Volume

Total Stocks Analyzed

📌 Data Tables (st.dataframe)

Top 10 Yearly Gainers

Top 10 Yearly Losers

🚀 Setup & Installation
🔷 Power BI

Install Power BI Desktop

Open:

Stock_data.pbix


Interact using slicers

🔷 Python / Streamlit Setup
Install Required Packages
pip install streamlit pandas numpy sqlalchemy matplotlib

Run the App
streamlit run streamlit_dashboard.py
