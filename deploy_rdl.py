import requests
import base64
import os
import getpass
from requests.auth import HTTPBasicAuth

# === SSRS Configuration ===
SSRS_URL = "http://localhost:8082/ReportServer/api/v2.0"  # Updated to match your configured port
REPORT_NAME = "GeneratedReport"
TARGET_FOLDER = "BI Reports with AI"

# Replace with your actual SSRS user or local admin account
USERNAME = "LAPTOP-L2BRSH99\\singh"
PASSWORD = getpass.getpass("Enter your SSRS password: ")

# === Load and Encode the .rdl File ===
rdl_path = os.path.join(os.getcwd(), "GeneratedReport.rdl")

if not os.path.exists(rdl_path):
    print("[ERROR] GeneratedReport.rdl not found. Run report generation first.")
    exit(1)

with open(rdl_path, "rb") as f:
    rdl_content = base64.b64encode(f.read()).decode('utf-8')

# === Step 1: Ensure the Target Folder Exists ===
folder_url = f"{SSRS_URL}/Folders"
folder_payload = {
    "Name": TARGET_FOLDER,
    "ParentFolder": "/"
}

response = requests.post(
    folder_url,
    json=folder_payload,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"}
)

if response.status_code == 201:
    print("[SUCCESS] Folder created.")
elif response.status_code == 409:
    print("[INFO] Folder already exists.")
else:
    print(f"[ERROR] Failed to create folder. Code: {response.status_code}\n{response.text}")
    exit(1)

# === Step 2: Upload the Encoded Report ===
report_url = f"{SSRS_URL}/Reports"
report_payload = {
    "Name": REPORT_NAME,
    "Path": f"/{TARGET_FOLDER}/{REPORT_NAME}",
    "Content": rdl_content
}

response = requests.post(
    report_url,
    json=report_payload,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"}
)

if response.status_code == 201:
    print("[SUCCESS] Report uploaded successfully.")
else:
    print(f"[ERROR] Failed to upload report. Code: {response.status_code}\n{response.text}")
