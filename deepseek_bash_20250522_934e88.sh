#!/bin/bash
# Brocade Logical Switch (VSAN) Information Extractor
# Generates a detailed report for all virtual fabrics

# Configuration
OUTPUT_DIR="/var/tmp/brocade_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="${OUTPUT_DIR}/brocade_vsan_report_${TIMESTAMP}.txt"
ARCHIVE_FILE="${OUTPUT_DIR}/brocade_config_${TIMESTAMP}.tar.gz"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Initialize report file
{
echo "======================================================"
echo " Brocade Logical Switch (VSAN) Configuration Report"
echo " Generated: $(date)"
echo " Switch: $(hostname)"
echo " Firmware: $(firmwareshow | head -n1)"
echo "======================================================"
echo ""
} > "$REPORT_FILE"

# Get list of all configured VSANs
VSAN_LIST=$(vsanshow | awk '/^VSAN/ {print $2}' | grep -v '^[^0-9]')

# Global switch information
{
echo "============= GLOBAL SWITCH INFORMATION ============="
echo ""
echo "--- Switch Capacity ---"
switchshow
switchstatuspolicyshow
switchstatusshow
echo ""

echo "--- Health Status ---"
healthcheck
tempshow
fanshow
pshow
echo ""

echo "--- Firmware Information ---"
firmwareshow
version
echo ""

echo "--- ISL Information ---"
trunkcfgshow
portstatsshow
portperfshow
echo ""

echo "--- Name Server Database ---"
nsallshow
echo ""
} >> "$REPORT_FILE"

# Process each VSAN
for VSAN in $VSAN_LIST; do
    {
    echo "============= VSAN ${VSAN} CONFIGURATION ============="
    echo ""
    
    # VSAN configuration
    echo "--- VSAN ${VSAN} Properties ---"
    vsanadmin -v $VSAN -show
    echo ""
    
    echo "--- VSAN ${VSAN} Membership ---"
    vsanmember -v $VSAN
    echo ""
    
    # Switch to VSAN context
    vsan $VSAN
    
    # Zoning information
    echo "--- VSAN ${VSAN} Zoning Configuration ---"
    zoneshow
    echo ""
    
    echo "--- VSAN ${VSAN} Active Zones ---"
    zoneshow --active
    echo ""
    
    echo "--- VSAN ${VSAN} Zone Aliases ---"
    alishow
    echo ""
    
    echo "--- VSAN ${VSAN} FLOGI Database ---"
    nsshow
    echo ""
    
    echo "--- VSAN ${VSAN} Port States ---"
    portshow
    echo ""
    
    # Return to default VSAN
    vsan 1
    
    echo "======================================================"
    echo ""
    } >> "$REPORT_FILE"
done

# Save configurations
{
echo "============= CONFIGURATION BACKUPS ============="
echo ""
echo "Saving running configurations..."
configdownload -all -o "${OUTPUT_DIR}/running_config_${TIMESTAMP}.txt"
cfgsave -y
echo "Configurations saved."
echo ""
} >> "$REPORT_FILE"

# Create archive of all files
tar -czvf "$ARCHIVE_FILE" -C "$OUTPUT_DIR" .

# Final output
echo "Report generated: $REPORT_FILE"
echo "Configuration archive: $ARCHIVE_FILE"