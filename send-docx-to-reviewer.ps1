# File: send-docx-to-reviewer.ps1

param (
    [string]$FilePath = "Test_Spec.docx",
    [string]$Endpoint = "http://localhost:7071/api/SpecReviewer"
)

if (!(Test-Path $FilePath)) {
    Write-Host "File not found: $FilePath"
    exit 1
}

try {
    $bytes = [System.IO.File]::ReadAllBytes($FilePath)
    $base64 = [Convert]::ToBase64String($bytes)

    $body = @{
        base64_file = $base64
    }

    $bodyJson = $body | ConvertTo-Json -Depth 3 -Compress

    Write-Host "Sending file to reviewer..."

    $response = Invoke-RestMethod -Uri $Endpoint `
        -Method Post `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($bodyJson)) `
        -ContentType "application/json"

    Write-Host "Reviewer Response:"
    $response | ConvertTo-Json -Depth 10
}
catch {
    Write-Error "Error: $_"
}
