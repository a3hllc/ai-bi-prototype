# © 2024 A3H LLC. All rights reserved.
# This file is part of the SSRS + AI Reporting Prototype.
# Use and distribution without permission is prohibited.
# SSRS BI+AI Prototype: Dynamic NLP-Driven Report Generator with Auto Column Detection

from generate_rdl import generate_rdl
import subprocess
import os
import re
import time
from nlp_to_sql import parse_question
from run_query import run_query

# === Step 1: User's NLP question ===
question = "Show me the top 5 selling products by quantity"
print(f"🔍 Interpreting question: '{question}'")

# === Step 2: NLP → SQL + intent ===
parsed = parse_question(question)
if not parsed:
    print("❌ Could not interpret the question.")
    exit(1)

sql_query = parsed['sql']
intent = parsed['intent']
print(f"🧠 NLP Intent: {intent}\n📝 SQL: {sql_query.strip()}\n")

# === Step 3: Dynamically build report metadata ===
def sanitize(text):
    return re.sub(r'[^a-zA-Z0-9]', '_', text)[:30]

report_title = question.strip().capitalize()
dataset_name = sanitize(parsed.get("dataset", "NLPDataset"))
report_id = sanitize(question.lower()) + "_" + str(int(time.time()))
output_file = f"{report_id}.rdl"

# === Step 4: If intent is to generate a report ===
if intent == "generate_report":
    try:
        df = run_query(sql_query)
        columns = list(df.columns)
    except Exception as e:
        print(f"❌ Failed to run query: {e}")
        exit(1)

    # Generate RDL
    generate_rdl(
        report_title=report_title,
        dataset_name=dataset_name,
        sql_query=sql_query,
        output_file=output_file,
        columns=columns
    )

    # Deploy using PowerShell directly with parameters
    deploy_script = os.path.join(os.getcwd(), 'deploy_rdl.ps1')
    deploy_command = [
        "powershell", "-ExecutionPolicy", "Bypass", "-File", deploy_script,
        "-ReportName", report_title,
        "-RdlPath", os.path.abspath(output_file),
        "-Folder", "/BI Reports with AI",
        "-ReportServer", "http://localhost:8082/ReportServer/ReportService2010.asmx"
    ]

    print("\n📤 Deploying RDL to SSRS...")
    result = subprocess.run(deploy_command, capture_output=True, text=True)
    print("\n--- Deployment Output ---")
    print(result.stdout)
    if result.stderr:
        print("\n[ERROR]", result.stderr)

    print(f"\n✅ Deployment complete: {output_file}")
    print("🔗 View at: http://localhost:8082/Reports")
else:
    print("ℹ️ Informational query only. No report deployed.")
