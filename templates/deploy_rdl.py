import requests
import base64
import os
from requests_ntlm import HttpNtlmAuth

# === SSRS Configuration ===
SSRS_URL = "http://localhost/ReportServer/api/v2.0"  # Updated to correct ReportServer URL
REPORT_NAME = "GeneratedReport"  # Name of the report to be uploaded (no extension)
TARGET_FOLDER = "BI Reports with AI"  # Target SSRS folder for deployment
USERNAME = "DOMAIN\\YourUsername"  # Replace with actual domain\username
PASSWORD = "YourPassword"  # Replace with your actual password

# === Load and Encode the .rdl File ===
rdl_path = os.path.join(os.getcwd(), "GeneratedReport.rdl")  # Full path to the report file

# Read and encode the .rdl file as base64 (SSRS requires this format)
with open(rdl_path, "rb") as f:
    rdl_content = base64.b64encode(f.read()).decode('utf-8')

# === Step 1: Ensure the Target Folder Exists ===
folder_url = f"{SSRS_URL}/Folders"
folder_payload = {
    "Name": TARGET_FOLDER,        # Desired folder name
    "ParentFolder": "/"           # Root folder
}

# Attempt to create the folder (will fail silently if it already exists)
response = requests.post(
    folder_url,
    json=folder_payload,
    auth=HttpNtlmAuth(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"}
)

# Handle folder creation response
if response.status_code == 201:
    print("✅ Folder created.")
elif response.status_code == 409:
    print("ℹ️ Folder already exists.")
else:
    print(f"❌ Failed to create folder. Code: {response.status_code}")

# === Step 2: Upload the Encoded Report ===
report_url = f"{SSRS_URL}/Reports"
report_payload = {
    "Name": REPORT_NAME,
    "Path": f"/{TARGET_FOLDER}/{REPORT_NAME}",  # Full SSRS path
    "Content": rdl_content  # Base64 content of the .rdl file
}

# Send request to upload the report
response = requests.post(
    report_url,
    json=report_payload,
    auth=HttpNtlmAuth(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"}
)

# Handle report upload response
if response.status_code == 201:
    print("✅ Report uploaded successfully.")
else:
    print(f"❌ Failed to upload report. Code: {response.status_code}")

