# app.py - Fixed version with clear result HTML in /api/query

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
    question = data.get('question')
    creator_id = data.get('creator_id')

    with open("secrets.json") as f:
        secrets = json.load(f)

    if creator_id != secrets.get("creator_id"):
        return jsonify({"error": "Unauthorized: Invalid creator_id"}), 403

    parsed = parse_question(question)
    if not parsed:
        return jsonify({"error": "Sorry, I couldn't understand that question."}), 400

    sql = parsed["sql"]
    try:
        df = run_query(sql)
        html = df.to_html(classes="table table-bordered", index=False)
        return jsonify({
            "html": html,
            "sql": sql
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/deploy', methods=['POST'])
def deploy():
    data = request.get_json()
    question = data.get('question')
    creator_id = data.get('creator_id')

    with open("secrets.json") as f:
        secrets = json.load(f)

    if creator_id != secrets.get("creator_id"):
        return jsonify({"error": "Unauthorized: Invalid creator_id"}), 403

    parsed = parse_question(question)
    if not parsed:
        return jsonify({"error": "Sorry, I couldn't understand that question."}), 400

    sql = parsed["sql"]
    intent = parsed["intent"]
    dataset = parsed.get("dataset", "NLPDataset")

    def sanitize(text):
        return re.sub(r'[^a-zA-Z0-9]', '_', text)[:30]

    report_title = question.strip().capitalize()
    dataset_name = sanitize(dataset)
    report_id = sanitize(question.lower()) + "_" + str(int(time.time()))
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
                                 "-Folder", "/BI Reports with AI",
                                 "-ReportServer", "http://localhost:8082/ReportServer/ReportService2010.asmx"],
                                capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr or "Failed to deploy report."}), 500

        return jsonify({
            "html": f"<p>✅ Report generated and deployed.</p><a href='http://localhost:8082/Reports' target='_blank'>View in SSRS</a>",
            "sql": sql
        })
    else:
        return jsonify({"error": "Intent was not to generate a report."}), 400

if __name__ == '__main__':
    app.run(debug=True)
