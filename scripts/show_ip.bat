@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  Show this machine's IPv4 addresses (to find the LAN IP).
REM  Share the IPv4 address shown under your Wi-Fi adapter with students.
REM ═══════════════════════════════════════════════════════════════════════

echo.
echo ── Your IPv4 Addresses ────────────────────────────────────────────────
ipconfig | findstr /i "IPv4"
echo.
echo Share the address labelled "Wi-Fi" or "Wireless LAN" with students.
echo Students should open: http://YOUR_IP:5000
echo.
pause
