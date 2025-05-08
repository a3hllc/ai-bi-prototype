# test_generate_bar_chart.py
# Copyright A3H LLC
# Generates a bar chart report for sales by region using AdventureWorks

from generate_rdl import generate_rdl

# Define the columns to match the query output
columns = ["Region", "TotalSales"]

# SQL that aggregates sales by territory
sql_query = """
SELECT TerritoryID AS Region,
       SUM(SubTotal) AS TotalSales
FROM Sales.SalesOrderHeader
GROUP BY TerritoryID
"""

# Generate the report using the bar chart layout
generate_rdl(
    report_title="Sales by Territory",
    dataset_name="SalesData",
    sql_query=sql_query,
    output_file="GeneratedReport/sales_by_territory_chart.rdl",
    columns=columns,
    layout_command="use bar chart"
)
