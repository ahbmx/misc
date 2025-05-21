#!/bin/bash

# PowerMax 8000 Health and Capacity Check Script
# Uses EMC Solutions Enabler SYMCLI commands
# Requires SYMCLI to be installed and configured

# Configuration
SYMID="YOUR_ARRAY_SID"  # Replace with your PowerMax SID
THRESHOLD_WARN=70       # Warning threshold for capacity usage (%)
THRESHOLD_CRIT=85       # Critical threshold for capacity usage (%)
OUTPUT_FILE="/tmp/powermax_health_$(date +%Y%m%d_%H%M%S).log"

# Initialize output
echo "PowerMax 8000 Health and Capacity Report - $(date)" > $OUTPUT_FILE
echo "Array SID: $SYMID" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Function to check command success
check_command() {
    if [ $? -ne 0 ]; then
        echo "ERROR: Command failed - $1" >> $OUTPUT_FILE
        exit 1
    fi
}

## 1. Check Array Health Status
echo "=== Array Health Status ===" >> $OUTPUT_FILE
symhealth -sid $SYMID list -app -v >> $OUTPUT_FILE
check_command "symhealth"

## 2. Check Overall Array Capacity
echo "" >> $OUTPUT_FILE
echo "=== Array Capacity Overview ===" >> $OUTPUT_FILE
symcfg -sid $SYMID list -pool -gb -thin >> $OUTPUT_FILE
check_command "symcfg list pool"

## 3. Detailed SRP Capacity (Storage Resource Pools)
echo "" >> $OUTPUT_FILE
echo "=== SRP Capacity Details ===" >> $OUTPUT_FILE
symcfg -sid $SYMID list -srp -detail -gb -thin -all >> $OUTPUT_FILE
check_command "symcfg list srp"

## 4. Check Thin Pool Utilization
echo "" >> $OUTPUT_FILE
echo "=== Thin Pool Utilization ===" >> $OUTPUT_FILE
symthin -sid $SYMID list -pool -detail >> $OUTPUT_FILE
check_command "symthin list pool"

## 5. Check for Alerts
echo "" >> $OUTPUT_FILE
echo "=== Recent Alerts ===" >> $OUTPUT_FILE
symevent -sid $SYMID list -start 24h >> $OUTPUT_FILE
check_command "symevent list"

## 6. Check for Failed Components
echo "" >> $OUTPUT_FILE
echo "=== Failed Components ===" >> $OUTPUT_FILE
symcfg -sid $SYMID list -failed >> $OUTPUT_FILE
check_command "symcfg list failed"

## 7. Performance Metrics (Optional)
# echo "" >> $OUTPUT_FILE
# echo "=== Performance Metrics ===" >> $OUTPUT_FILE
# symstat -sid $SYMID -interval 5 -iterations 1 list >> $OUTPUT_FILE
# check_command "symstat"

## Analyze Capacity Usage
echo "" >> $OUTPUT_FILE
echo "=== Capacity Analysis ===" >> $OUTPUT_FILE

# Extract total and used capacity from SRP output
SRP_INFO=$(symcfg -sid $SYMID list -srp -gb -thin | grep -A 3 "SRP")
TOTAL_GB=$(echo "$SRP_INFO" | grep "Total GB" | awk '{print $NF}')
USED_GB=$(echo "$SRP_INFO" | grep "Used GB" | awk '{print $NF}')
SUBS_GB=$(echo "$SRP_INFO" | grep "Subscribed GB" | awk '{print $NF}')

if [ -z "$TOTAL_GB" ] || [ -z "$USED_GB" ]; then
    echo "ERROR: Could not extract capacity information" >> $OUTPUT_FILE
    exit 1
fi

# Calculate percentages
USED_PCT=$(echo "scale=2; $USED_GB * 100 / $TOTAL_GB" | bc)
SUBS_PCT=$(echo "scale=2; $SUBS_GB * 100 / $TOTAL_GB" | bc)

echo "Total Capacity: $TOTAL_GB GB" >> $OUTPUT_FILE
echo "Used Capacity: $USED_GB GB ($USED_PCT%)" >> $OUTPUT_FILE
echo "Subscribed Capacity: $SUBS_GB GB ($SUBS_PCT%)" >> $OUTPUT_FILE

# Check against thresholds
STATUS="OK"
if (( $(echo "$USED_PCT >= $THRESHOLD_CRIT" | bc -l) )); then
    STATUS="CRITICAL"
elif (( $(echo "$USED_PCT >= $THRESHOLD_WARN" | bc -l) )); then
    STATUS="WARNING"
fi

if (( $(echo "$SUBS_PCT >= $THRESHOLD_CRIT" | bc -l) )); then
    STATUS="CRITICAL"
elif (( $(echo "$SUBS_PCT >= $THRESHOLD_WARN" | bc -l) )); then
    if [ "$STATUS" != "CRITICAL" ]; then
        STATUS="WARNING"
    fi
fi

echo "" >> $OUTPUT_FILE
echo "Overall Status: $STATUS" >> $OUTPUT_FILE

## Display summary
echo "" >> $OUTPUT_FILE
echo "=== Summary ===" >> $OUTPUT_FILE
echo "Array Health: $(symhealth -sid $SYMID list -app -v | grep "Overall Health" | cut -d':' -f2 | xargs)" >> $OUTPUT_FILE
echo "Used Capacity: $USED_PCT% (Thresholds: WARN=$THRESHOLD_WARN%, CRIT=$THRESHOLD_CRIT%)" >> $OUTPUT_FILE
echo "Subscribed Capacity: $SUBS_PCT% (Thresholds: WARN=$THRESHOLD_WARN%, CRIT=$THRESHOLD_CRIT%)" >> $OUTPUT_FILE
echo "Recent Alerts (24h): $(symevent -sid $SYMID list -start 24h | grep -c "Alert ID:")" >> $OUTPUT_FILE
echo "Failed Components: $(symcfg -sid $SYMID list -failed | grep -c "FAULTED")" >> $OUTPUT_FILE

## Display output
cat $OUTPUT_FILE

## Exit with proper status code for monitoring systems
if [ "$STATUS" == "CRITICAL" ]; then
    exit 2
elif [ "$STATUS" == "WARNING" ]; then
    exit 1
else
    exit 0
fi