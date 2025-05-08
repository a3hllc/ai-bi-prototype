# © 2024 A3H LLC. All rights reserved.
# This file is part of the SSRS + AI Reporting Prototype.
# Use and distribution without permission is prohibited.
import os
import zipfile

def zip_project_folder(folder_path, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    project_folder = "C:\\AIProjects\\nlp_aw_web"
    output_zip = "C:\\AIProjects\\SSRS_AI_Prototype.zip"
    zip_project_folder(project_folder, output_zip)
    print(f"✅ Prototype zipped successfully: {output_zip}")
