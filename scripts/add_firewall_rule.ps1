# ═══════════════════════════════════════════════════════════════════════════
# add_firewall_rule.ps1 – Add Windows Firewall inbound rule for CampusConnect
#
# Run as Administrator:
#   Right-click PowerShell → "Run as Administrator"
#   Then: .\scripts\add_firewall_rule.ps1
#
# This opens TCP port 5000 on the PRIVATE profile only, restricted to
# the local subnet.  It does NOT affect internet traffic.
# ═══════════════════════════════════════════════════════════════════════════

$RuleName = "CampusConnect-Port-5000"

# Check if rule already exists
if (Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue) {
    Write-Host "Firewall rule '$RuleName' already exists." -ForegroundColor Yellow
} else {
    New-NetFirewallRule `
        -DisplayName $RuleName `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 5000 `
        -Action Allow `
        -Profile Private `
        -RemoteAddress LocalSubnet `
        -Description "Allow CampusConnect Flask app on LAN (private network only)"

    Write-Host "Firewall rule '$RuleName' created successfully." -ForegroundColor Green
}

Write-Host ""
Write-Host "To REMOVE this rule later, run:" -ForegroundColor Cyan
Write-Host "  Remove-NetFirewallRule -DisplayName '$RuleName'"
