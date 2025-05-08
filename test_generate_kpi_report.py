# test_generate_kpi_report.py
# Copyright A3H LLC
# Generates a KPI report using correct AdventureWorks2019 tables

from generate_rdl import generate_rdl

# ✅ Valid columns from Sales.SalesOrderHeader
columns = ["Region", "TotalSales", "OrderCount"]

# ✅ SQL that works with AdventureWorks2019
sql_query = """
SELECT TerritoryID AS Region,
       SUM(SubTotal) AS TotalSales,
       COUNT(SalesOrderID) AS OrderCount
FROM Sales.SalesOrderHeader
GROUP BY TerritoryID
"""

# ✅ Trigger layout selection via NLP
generate_rdl(
    report_title="Regional Sales KPIs",
    dataset_name="SalesByRegion",
    sql_query=sql_query,
    output_file="GeneratedReport/kpi_sales_report.rdl",
    columns=columns,
    layout_command="use KPI cards"
)
