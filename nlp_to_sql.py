# © 2024 A3H LLC. All rights reserved.
# nlp_to_sql.py - Hybrid parser with year fallback + AdventureWorks star schema

import re
import pyodbc

# Fetch all available years from DimDate

def get_valid_years():
    try:
        conn = pyodbc.connect("DSN=AdventureWorks")  # Adjust your DSN or use a full connection string
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Year FROM DimDate")
        return sorted([row[0] for row in cursor.fetchall()], reverse=True)
    except:
        return []

def parse_question(question):
    q = question.lower().strip()

    static_result = parse_static_question(q)
    if static_result:
        return static_result

    star_result = parse_star_schema_question(q)
    if star_result:
        return star_result

    return None

def parse_static_question(q):
    if re.search(r"top \d+ selling products", q):
        return {
            "sql": """
                SELECT TOP 5 p.Name, SUM(sd.OrderQty) AS TotalSold
                FROM Sales.SalesOrderDetail sd
                JOIN Production.Product p ON p.ProductID = sd.ProductID
                GROUP BY p.Name
                ORDER BY TotalSold DESC
            """,
            "intent": "generate_report",
            "dataset": "Sales"
        }

    if "sales by territory" in q:
        return {
            "sql": """
                SELECT TerritoryID, SUM(TotalDue) AS Sales
                FROM Sales.SalesOrderHeader
                GROUP BY TerritoryID
            """,
            "intent": "generate_report",
            "dataset": "Sales"
        }

    if "top customers by revenue" in q:
        return {
            "sql": """
                SELECT TOP 10 c.CustomerID, SUM(soh.TotalDue) AS TotalSpent
                FROM Sales.Customer c
                JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
                GROUP BY c.CustomerID
                ORDER BY TotalSpent DESC
            """,
            "intent": "generate_report",
            "dataset": "Sales"
        }

    if any(phrase in q for phrase in ["forecast", "predict", "expected", "projected"]):
        return {"intent": "predict", "sql": None, "dataset": "Sales"}

    return None

def parse_star_schema_question(q):
    select_clause = ""
    from_clause = "FROM FactSales f\n"
    joins = []
    group_by = []
    filters = []
    order = "ORDER BY Total DESC"
    intent = "generate_report"
    notes = ""

    if "region" in q:
        joins.append("JOIN DimTerritory t ON f.TerritoryKey = t.TerritoryKey")
        select_clause += "t.Name AS Region, "
        group_by.append("t.Name")

    if "customer" in q:
        joins.append("JOIN DimCustomer c ON f.CustomerKey = c.CustomerKey")
        select_clause += "c.CustomerID, "
        group_by.append("c.CustomerID")

    if "product" in q:
        joins.append("JOIN DimProduct p ON f.ProductKey = p.ProductKey")
        select_clause += "p.Name AS Product, "
        group_by.append("p.Name")

    if "month" in q or "year" in q:
        joins.append("JOIN DimDate d ON f.OrderDateKey = d.DateKey")
        if "month" in q:
            select_clause += "d.Month, d.MonthName, "
            group_by += ["d.Month", "d.MonthName"]
        if "year" in q:
            select_clause += "d.Year, "
            group_by.append("d.Year")

    # Year logic with fallback
    year_match = re.search(r"in (20\d{2})", q)
    valid_years = get_valid_years()
    if year_match:
        requested_year = int(year_match.group(1))
        if requested_year in valid_years:
            filters.append(f"d.Year = {requested_year}")
        elif valid_years:
            filters.append(f"d.Year = {valid_years[0]}")
            notes = f"Note: No data for {requested_year}, defaulted to {valid_years[0]}"
    elif "year" in q and valid_years:
        filters.append(f"d.Year = {valid_years[0]}")

    if "average" in q:
        select_clause += "AVG(f.TotalDue) AS Total\n"
    elif "count" in q:
        select_clause += "COUNT(*) AS Total\n"
    else:
        select_clause += "SUM(f.TotalDue) AS Total\n"

    if not group_by:
        group_by.append("1")

    sql = f"SELECT {select_clause}{from_clause}"
    if joins:
        sql += "\n" + "\n".join(joins) + "\n"
    if filters:
        sql += f"WHERE {' AND '.join(filters)}\n"
    sql += f"GROUP BY {', '.join(group_by)}\n{order}"

    return {
        "sql": sql,
        "intent": intent,
        "dataset": "FactSales",
        "notes": notes
    }
