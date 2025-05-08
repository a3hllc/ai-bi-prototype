# app.py - Fixed version with secure deploy, folder routing, and audit log

from flask import Flask, render_template, request, jsonify
from nlp_to_sql import parse_question
from run_query import run_query
from generate_rdl import generate_rdl

import os
import subprocess
import re
import time
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    question = data.get('question') or data.get('query')
    creator_id = data.get('creator_id')

    with open("secrets.json") as f:
        secrets = json.load(f)

    if creator_id != secrets.get("creator_id"):
        return jsonify({"error": "Unauthorized: Invalid creator_id"}), 403

    parsed = parse_question(question)
    if not parsed:
        return jsonify({"error": "Sorry, I couldn't understand that question."}), 400

    sql = parsed.get("sql")
    intent = parsed.get("intent")

    if intent == "predict":
        subprocess.run(["python", "predict_sales.py"], check=True)
        try:
            with open("predicted_sales.html", "r", encoding="utf-8") as f:
                html = f.read()
            return jsonify({"html": html, "sql": "Forecast model used"})
        except Exception as e:
            return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

    try:
        df = run_query(sql)
        html = df.to_html(classes="table table-bordered", index=False)
        return jsonify({"html": html, "sql": sql})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/deploy', methods=['POST'])
def deploy():
    data = request.get_json()
    question = data.get('question') or data.get('query')
    creator_id = data.get('creator_id')

    with open("secrets.json") as f:
        secrets = json.load(f)

    if creator_id != secrets.get("creator_id"):
        return jsonify({"error": "Unauthorized: Invalid creator_id"}), 403

    parsed = parse_question(question)
    if not parsed:
        return jsonify({"error": "Sorry, I couldn't interpret that question."}), 400

    sql = parsed.get("sql")
    intent = parsed.get("intent")
    dataset = parsed.get("dataset", "NLPDataset")

    folder_keywords = {
        "sales": "Sales",
        "finance": "Finance",
        "hr": "HR",
        "ops": "Operations"
    }
    folder_name = "General"
    for keyword, mapped in folder_keywords.items():
        if keyword in question.lower():
            folder_name = mapped
            break

    target_folder = f"/BI Reports/{folder_name}"

    def sanitize(text):
        return re.sub(r'[^a-zA-Z0-9]', '_', text)[:30]

    report_title = sanitize(question.strip().capitalize())
    dataset_name = sanitize(dataset)
    report_id = sanitize(question.lower()) + "_" + str(int(time.time()))

    if "new version" in question.lower():
        report_id += "_v" + str(int(time.time()))

    output_file = f"{report_id}.rdl"

    if intent == "generate_report":
        try:
            df = run_query(sql)
            columns = list(df.columns)
        except Exception as e:
            return jsonify({"error": f"Query failed: {str(e)}"}), 500

        generate_rdl(
            report_title=report_title,
            dataset_name=dataset_name,
            sql_query=sql,
            output_file=output_file,
            columns=columns
        )

        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "deploy_rdl.ps1",
                                 "-ReportName", report_title,
                                 "-RdlPath", os.path.abspath(output_file),
                                 "-Folder", target_folder,
                                 "-ReportServer", "http://localhost:8082/ReportServer/ReportService2010.asmx"],
                                capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr or "Failed to deploy report."}), 500

        with open("deploy_log.jsonl", "a", encoding="utf-8") as log_file:
            log_entry = {
                "timestamp": time.time(),
                "report": report_title,
                "folder": target_folder,
                "sql": sql,
                "creator_id": creator_id
            }
            log_file.write(json.dumps(log_entry) + "\n")

        return jsonify({
            "html": f"<p>✅ Report generated and deployed.</p><a href='http://localhost:8082/Reports' target='_blank'>View in SSRS</a>",
            "sql": sql
        })

    return jsonify({"error": "Unsupported intent for deployment."}), 400

if __name__ == '__main__':
    app.run(debug=True)
