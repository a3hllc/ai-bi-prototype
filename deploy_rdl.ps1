# ========================================
# PowerShell Script to Deploy .rdl to SSRS
# Uses SOAP API (ReportService2010.asmx)
# Compatible with SSRS 2016+ (port 8082)
# ========================================

param(
    [string]$ReportName,   # Name of the report (no extension)
    [string]$RdlPath,      # Full path to the .rdl file
    [string]$Folder,       # Target SSRS folder path (e.g., "/BI Reports with AI")
    [string]$ReportServer  # Full SOAP endpoint (e.g., http://localhost:8082/ReportServer/ReportService2010.asmx)
)

Write-Host "🔄 Starting SSRS deployment to $ReportServer..."

# === Step 1: Validate .rdl file path ===
if (-not (Test-Path $RdlPath)) {
    Write-Error "❌ RDL file not found at $RdlPath"
    exit 1
}

try {
    # === Step 2: Load report file as byte array ===
    $bytes = [System.IO.File]::ReadAllBytes($RdlPath)

    # === Step 3: Connect to SSRS SOAP API ===
    $ssrs = New-WebServiceProxy -Uri $ReportServer -Namespace "SSRS" -UseDefaultCredential

    # === Step 4: Check if the folder already exists ===
    $existing = $ssrs.ListChildren("/", $false) | Where-Object { $_.Path -eq $Folder }

    if (-not $existing) {
        Write-Host "📁 Folder '$Folder' not found. Creating it..."
        # Create folder (strip leading slash)
        $ssrs.CreateFolder($Folder.TrimStart("/"), "/", "Auto-created for report deployment")
        Write-Host "✅ Folder '$Folder' created successfully."
    }
    else {
        Write-Host "ℹ️ Folder '$Folder' already exists."
    }

    # === Step 5: Upload the report ===
    $null = $ssrs.CreateCatalogItem(
        "Report",           # Item type
        $ReportName,        # Name of the report
        $Folder,            # Folder to place it in
        $true,              # Overwrite if exists
        $bytes,             # File content
        $null,              # Properties
        [ref]$null          # Warnings
    )

    Write-Host "✅ Report '$ReportName' successfully deployed to folder '$Folder'."
}
catch {
    # === Catch and display errors ===
    Write-Error "❌ Deployment failed: $_"
    exit 1
}
