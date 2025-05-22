#!/bin/bash
# Brocade Single Path Host Checker
# Identifies hosts with only one active path to storage

# Output file
OUTPUT_FILE="single_path_hosts_$(date +%Y%m%d_%H%M%S).csv"
TIMESTAMP=$(date)

# Temporary files
TEMP_NSHOW="/tmp/nshow_$$.tmp"
TEMP_ZONE="/tmp/zoneshow_$$.tmp"

# Header for output file
echo "Timestamp,Host_WWPN,Host_Alias,Connected_Port,VSAN,Zone_Membership" > "$OUTPUT_FILE"

# Get list of all VSANs
VSAN_LIST=$(vsanshow | awk '/^VSAN/ {print $2}' | grep -v '^[^0-9]')

for VSAN in $VSAN_LIST; do
    echo "Checking VSAN $VSAN..."
    
    # Get FLOGI database for this VSAN
    vsan $VSAN
    nsshow > "$TEMP_NSHOW"
    zoneshow > "$TEMP_ZONE"
    
    # Process each host in FLOGI database
    awk '
    BEGIN {
        FS="[)(]";
        while (getline < "'"$TEMP_ZONE"'") {
            if ($0 ~ /zone:.*/ || $0 ~ /alias:.*/) {
                current_zone = $2;
            }
            if ($0 ~ /[0-9a-f]{16}/) {
                split($0, parts, ";");
                for (i in parts) {
                    gsub(/^[ \t]+|[ \t]+$/, "", parts[i]);
                    if (parts[i] ~ /[0-9a-f]{16}/) {
                        zones[parts[i]] = (zones[parts[i]] ? zones[parts[i]] ", " : "") current_zone;
                    }
                }
            }
        }
    }
    /Nx_Port/ && !/FC Router/ {
        # Extract WWPN
        wwpn = $2;
        gsub(/ /, "", wwpn);
        
        # Extract Port (Domain,Area)
        port = $4;
        gsub(/ /, "", port);
        
        # Count occurrences of this WWPN
        host_count[wwpn]++;
        host_port[wwpn] = port;
        host_vsan[wwpn] = "'"$VSAN"'";
    }
    END {
        for (wwpn in host_count) {
            if (host_count[wwpn] == 1) {
                alias = "N/A";
                if (wwpn in zones) {
                    alias = zones[wwpn];
                }
                print "'"$TIMESTAMP"'", wwpn, alias, host_port[wwpn], host_vsan[wwpn], zones[wwpn];
            }
        }
    }' "$TEMP_NSHOW" | tr ' ' ',' >> "$OUTPUT_FILE"
    
    vsan 1  # Return to default VSAN
done

# Clean up temp files
rm -f "$TEMP_NSHOW" "$TEMP_ZONE"

# Generate summary
TOTAL_HOSTS=$(awk 'END{print NR-1}' "$OUTPUT_FILE")
echo "Scan completed."
echo "Found $TOTAL_HOSTS hosts with single paths"
echo "Report saved to: $OUTPUT_FILE"

# Display sample of results (first 5 entries)
if [ "$TOTAL_HOSTS" -gt 0 ]; then
    echo ""
    echo "Sample of affected hosts:"
    head -n 6 "$OUTPUT_FILE" | column -t -s','
fi