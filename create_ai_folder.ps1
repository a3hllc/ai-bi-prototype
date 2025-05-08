# === CONFIGURATION ===
$ReportServerUri = "http://localhost:8082/ReportServer/ReportService2010.asmx"
$FolderPath = "/AIReports"
$Description = "AI-driven reporting folder"
$Properties = @()

# === Connect to SSRS Web Service ===
$ssrs = New-WebServiceProxy -Uri $ReportServerUri -Namespace "SSRS" -UseDefaultCredential

try {
    # Check if folder exists
    $items = $ssrs.ListChildren("/", $false)
    $exists = $items | Where-Object { $_.Path -eq $FolderPath }

    if (-not $exists) {
        Write-Host "Creating folder: $FolderPath"
        $ssrs.CreateFolder("AIReports", "/", $Description)
        Write-Host "✅ Folder created successfully."
    } else {
        Write-Host "✅ Folder already exists: $FolderPath"
    }
}
catch {
    Write-Error "❌ Failed to create folder: $_"
}
