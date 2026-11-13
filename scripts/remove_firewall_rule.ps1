# Remove the CampusConnect firewall rule (run as Administrator)
$RuleName = "CampusConnect-Port-5000"
Remove-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue
Write-Host "Firewall rule '$RuleName' removed." -ForegroundColor Green
