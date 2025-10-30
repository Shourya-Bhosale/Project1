# PowerShell script to set environment variables permanently
# Run this script as Administrator if needed

Write-Host "Setting environment variables for Gmail SMTP..." -ForegroundColor Green

# Gmail SMTP (set your Gmail App Password in EMAIL_HOST_PASSWORD)
[System.Environment]::SetEnvironmentVariable('EMAIL_HOST', 'smtp.gmail.com', 'User')
[System.Environment]::SetEnvironmentVariable('EMAIL_PORT', '587', 'User')
[System.Environment]::SetEnvironmentVariable('EMAIL_USE_TLS', 'True', 'User')
[System.Environment]::SetEnvironmentVariable('EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com', 'User')
[System.Environment]::SetEnvironmentVariable('EMAIL_TIMEOUT', '30', 'User')
Write-Host "✓ Gmail SMTP base settings set" -ForegroundColor Green

Write-Host ""
Write-Host "⚠️ Set EMAIL_HOST_PASSWORD manually (Gmail App Password) using:" -ForegroundColor Yellow
Write-Host "   setx EMAIL_HOST_PASSWORD \"your_gmail_app_password\"" -ForegroundColor Yellow

Write-Host ""
Write-Host "✅ Environment variables configured (excluding password)." -ForegroundColor Green
Write-Host "Note: Restart your terminal/IDE for changes to take effect." -ForegroundColor Yellow

