# PowerShell script to set environment variables permanently
# Run this script as Administrator if needed

Write-Host "Setting environment variables for Shiv Dairy WhatsApp notifications..." -ForegroundColor Green

# Company WhatsApp Phone
[System.Environment]::SetEnvironmentVariable('COMPANY_WHATSAPP_PHONE', '+919158019119', 'User')
Write-Host "✓ COMPANY_WHATSAPP_PHONE set" -ForegroundColor Green

# Twilio Credentials
# IMPORTANT: Replace these with your actual Twilio credentials
[System.Environment]::SetEnvironmentVariable('TWILIO_ACCOUNT_SID', 'YOUR_TWILIO_ACCOUNT_SID', 'User')
Write-Host "✓ TWILIO_ACCOUNT_SID set" -ForegroundColor Green

[System.Environment]::SetEnvironmentVariable('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_AUTH_TOKEN', 'User')
Write-Host "✓ TWILIO_AUTH_TOKEN set" -ForegroundColor Green

Write-Host "`n✅ All environment variables set successfully!" -ForegroundColor Green
Write-Host "Note: You may need to restart your terminal or IDE for changes to take effect." -ForegroundColor Yellow

