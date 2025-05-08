# © 2024 A3H LLC. All rights reserved.
# This file is part of the SSRS + AI Reporting Prototype.
# Use and distribution without permission is prohibited.
# predict_sales.py - Predictive Forecasting for SSRS BI Prototype

import pandas as pd
import pyodbc
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import numpy as np
from datetime import datetime

# Connect to AdventureWorks2019 using correct server name
conn = pyodbc.connect("Driver={SQL Server};Server=LAPTOP-L2BRSH99;Database=AdventureWorks2019;Trusted_Connection=yes;")

# Query monthly sales totals
df = pd.read_sql("""
    SELECT 
        YEAR(OrderDate) AS Year, 
        MONTH(OrderDate) AS Month, 
        SUM(TotalDue) AS TotalSales
    FROM Sales.SalesOrderHeader
    GROUP BY YEAR(OrderDate), MONTH(OrderDate)
    ORDER BY Year, Month
""", conn)
conn.close()

# Create time index for regression
df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(Day=1))
df['TimeIndex'] = np.arange(len(df))

# Fit model
model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
model.fit(df[['TimeIndex']], df['TotalSales'])

# Forecast next 6 months
future_steps = 6
future_index = np.arange(len(df), len(df)+future_steps)
future_sales = model.predict(future_index.reshape(-1,1))

# Prepare results
future_dates = pd.date_range(df['Date'].max(), periods=future_steps+1, freq='MS')[1:]
forecast_df = pd.DataFrame({
    'ForecastMonth': future_dates.strftime('%Y-%m'),
    'PredictedSales': future_sales.round(2)
})

# Output to HTML (for preview) or CSV for SSRS
forecast_df.to_html("predicted_sales.html", index=False)
forecast_df.to_csv("predicted_sales.csv", index=False)

print("✅ Forecast ready. Files saved as predicted_sales.html and predicted_sales.csv")
