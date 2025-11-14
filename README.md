📈 Financial Performance Analysis Dashboard
A Dual-Component Project for Dynamic Financial Reporting & Automation
This project delivers a complete end-to-end financial analytics system, combining Power BI’s interactive reporting with Python + Streamlit’s automation capabilities.
It is designed to analyze stock market data, create dynamic insights, and generate automated web-based financial reports.

🛠️ Technologies Used
Category	        Tools	                         Purpose
Core Language    	Python	             -    ETL, data processing, Streamlit app logic,
Database	        MySQL / PostgreSQL	 -    Storage for historical stock data,
Processing	      Pandas	              -   Data manipulation and metric generation,
                  SQLAlchemy	           -  Database connection and ORM,
Visualization	    Power BI	              - Interactive dashboards, DAX modelling,
      	          Streamlit               - Automated reporting interface,
Libraries	        Matplotlib/seaborn	    - Static charts for historical trend analysis.



📊 1. Power BI Dashboard – Interactive Visualization

The Power BI dashboard (Stock_data) allows interactive exploration of monthly and yearly stock performance.

Visual Components

Clustered Bar Chart -  Dynamic Top 5 Gainers & Bottom 5 Losers - Green/Red conditional formatting

Month Hierarchy Slicer - User-friendly time filtering

Card Visuals -

Avg. Price (All Time), Avg. Volume (All Time)

Stock counts: Total, Green, Red

⭐ Key DAX Engineering Highlights
🔹 Reliable Top/Bottom 5 Ranking

Implemented using RANKX

More stable than native "Top N" filter

Ensures accurate sorting across slicers

🔹 Accurate Monthly Return Calculation

Uses FIRSTNONBLANK & LASTNONBLANK

Handles missing days (weekends/holidays) gracefully

🔹 Yearly Performance Summary

Built with SELECTEDVALUE + ALL()

Ensures symbol-accurate calculation regardless of filters

🐍 2. Python + Streamlit Application – Automated Reporting

The Streamlit application (streamlit_financial_dashboard.py) processes stock data and presents automated yearly insights.

Features
📌 Metric Cards (st.metric)

Average Close Price

Average Daily Volume

Total Stocks Analyzed

📌 Data Tables (st.dataframe)

Top 10 Gainers of the year

Top 10 Losers of the year

Perfect for automated financial reporting or embedding in internal analytics portals.

🚀 Setup & Installation
🔷 Power BI

Install Power BI Desktop

Open the file:

Stock_data.pbix


Use the Month Slicer to interact with the dashboard.

🔷 Python / Streamlit Setup
Prerequisites

Python 3.8+

MySQL/PostgreSQL database

Stock data loaded into your DB table

Install Required Packages
pip install streamlit pandas numpy sqlalchemy matplotlib

Run the Streamlit App
streamlit run streamlit_dashboard.py


The application will open automatically in your browser.
