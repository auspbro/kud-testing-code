# BLED112 dongle
echo "---- BLED112 dongle: restart ----"
.\devcon.exe restart USB\Class_02
# .\devcon.exe disable USB\Class_02
# .\devcon.exe enable USB\Class_02

echo ""

# USB to UART dongle
echo "---- USB to UART dongle dongle: restart ----"
.\devcon.exe restart USB\Class_01

#pause