# nlp_to_sql.py - Enhanced NLP to SQL for multiple SSRS report cases

import re

def parse_question(question):
    q = question.lower().strip()

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

    if "total sales by territory" in q:
        return {
            "sql": """
                SELECT soh.TerritoryID, COUNT(*) AS OrderCount, SUM(soh.TotalDue) AS TotalSales
                FROM Sales.SalesOrderHeader soh
                GROUP BY soh.TerritoryID
            """,
            "intent": "generate_report",
            "dataset": "Sales"
        }

    if "orders by country" in q:
        return {
            "sql": """
                SELECT a.CountryRegionCode, COUNT(*) AS TotalOrders
                FROM Sales.SalesOrderHeader soh
                JOIN Person.Address a ON soh.ShipToAddressID = a.AddressID
                GROUP BY a.CountryRegionCode
            """,
            "intent": "generate_report",
            "dataset": "Sales"
        }

    if "employees in" in q:
        match = re.search(r"employees in (.+)", q)
        dept = match.group(1).title() if match else "Sales"
        return {
            "sql": f"""
                SELECT e.BusinessEntityID, p.FirstName, p.LastName, d.Name AS Department
                FROM HumanResources.Employee e
                JOIN HumanResources.EmployeeDepartmentHistory h ON e.BusinessEntityID = h.BusinessEntityID
                JOIN HumanResources.Department d ON h.DepartmentID = d.DepartmentID
                JOIN Person.Person p ON p.BusinessEntityID = e.BusinessEntityID
                WHERE d.Name = '{dept}'
            """,
            "intent": "generate_report",
            "dataset": "HumanResources"
        }

    return None
