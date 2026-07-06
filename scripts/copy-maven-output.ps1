param(
    [string]$Source = "build/maven-repo",
    [string]$Target = "maven"
)

if (-not (Test-Path $Source)) {
    Write-Error "Source folder not found: $Source"
    Write-Host "Usage: .\scripts\copy-maven-output.ps1 -Source C:\path\to\build\maven-repo [-Target maven]"
    exit 1
}

New-Item -ItemType Directory -Path $Target -Force | Out-Null
Copy-Item -Path (Join-Path $Source "*") -Destination $Target -Recurse -Force

Write-Host "Copied Maven output from: $Source"
Write-Host "to: $Target"
Write-Host "Now run:"
Write-Host "  git add ."
Write-Host "  git commit -m 'Publish Maven artifacts'"
Write-Host "  git push"
