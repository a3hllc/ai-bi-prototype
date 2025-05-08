param(
    [string]$ReportName,
    [string]$RdlPath,
    [string]$Folder,
    [string]$ReportServer
)

$bytes = [System.IO.File]::ReadAllBytes($RdlPath)
$ssrs = New-WebServiceProxy -Uri $ReportServer -Namespace "SSRS" -UseDefaultCredential

$null = $ssrs.CreateCatalogItem(
    "Report",
    $ReportName,
    $Folder,
    $true,
    $bytes,
    $null,
    [ref]$null
)

Write-Host "✅ Report '$ReportName' successfully deployed to '$Folder'."
