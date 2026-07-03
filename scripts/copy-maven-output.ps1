param(
    [string]$Source = "build/maven-repo"
)

if (-not (Test-Path $Source)) {
    Write-Error "Source folder not found: $Source"
    Write-Host "Usage: .\scripts\copy-maven-output.ps1 -Source C:\path\to\build\maven-repo"
    exit 1
}

Copy-Item -Path (Join-Path $Source "*") -Destination "." -Recurse -Force

Write-Host "Copied Maven output from: $Source"
Write-Host "Now run:"
Write-Host "  git add ."
Write-Host "  git commit -m 'Publish Maven artifacts'"
Write-Host "  git push"
