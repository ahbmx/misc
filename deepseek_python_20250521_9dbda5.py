#!/usr/bin/env python3

from PyU4V import U4VConn
from PyU4V.utils import exception
import argparse
import datetime
import json
import sys

# Configuration
UNISPHERE_IP = 'your_unisphere_ip'
UNISPHERE_PORT = '8443'
USERNAME = 'your_username'
PASSWORD = 'your_password'
ARRAY_ID = 'your_powermax_array_id'

# Thresholds (adjust as needed)
CAPACITY_WARNING = 70  # Percentage
CAPACITY_CRITICAL = 85  # Percentage
THIN_WARNING = 70  # Percentage
THIN_CRITICAL = 85  # Percentage

def initialize_connection():
    """Initialize connection to Unisphere REST API"""
    try:
        conn = U4VConn(
            u4v_ip=UNISPHERE_IP,
            port=UNISPHERE_PORT,
            username=USERNAME,
            password=PASSWORD,
            verify=False,  # Set to True if using valid SSL cert
            array_id=ARRAY_ID
        )
        return conn
    except exception.ResourceNotFoundException as e:
        print(f"Connection error: {str(e)}")
        sys.exit(1)

def check_array_health(conn):
    """Check overall array health status"""
    try:
        health = conn.common.get_array_health()
        return health
    except Exception as e:
        print(f"Error checking array health: {str(e)}")
        return None

def check_array_capacity(conn):
    """Check array capacity metrics"""
    try:
        capacity = conn.performance.get_array_capacity_metrics()
        return capacity
    except Exception as e:
        print(f"Error checking array capacity: {str(e)}")
        return None

def check_srp_capacity(conn, srp_id='SRP_1'):
    """Check SRP capacity details"""
    try:
        srp = conn.provisioning.get_srp(srp_id)
        return srp
    except Exception as e:
        print(f"Error checking SRP capacity: {str(e)}")
        return None

def check_alerts(conn, days=1):
    """Check recent alerts"""
    try:
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        alerts = conn.system.get_alerts(
            start_date=start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            end_date=end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        return alerts
    except Exception as e:
        print(f"Error checking alerts: {str(e)}")
        return None

def analyze_capacity(srp_data):
    """Analyze capacity data and return status"""
    if not srp_data:
        return {'status': 'UNKNOWN', 'message': 'No SRP data available'}
    
    total_capacity = srp_data.get('total_capacity_gb', 0)
    used_capacity = srp_data.get('used_capacity_gb', 0)
    subscribed_capacity = srp_data.get('subscribed_capacity_gb', 0)
    
    if total_capacity == 0:
        return {'status': 'UNKNOWN', 'message': 'Total capacity is zero'}
    
    percent_used = (used_capacity / total_capacity) * 100
    percent_subscribed = (subscribed_capacity / total_capacity) * 100
    
    status = 'OK'
    messages = []
    
    # Check used capacity
    if percent_used >= CAPACITY_CRITICAL:
        status = 'CRITICAL'
        messages.append(f"Used capacity at {percent_used:.2f}% (threshold: {CAPACITY_CRITICAL}%)")
    elif percent_used >= CAPACITY_WARNING:
        if status != 'CRITICAL':
            status = 'WARNING'
        messages.append(f"Used capacity at {percent_used:.2f}% (threshold: {CAPACITY_WARNING}%)")
    else:
        messages.append(f"Used capacity at {percent_used:.2f}% - OK")
    
    # Check thin provisioning
    if percent_subscribed >= THIN_CRITICAL:
        status = 'CRITICAL'
        messages.append(f"Subscribed capacity at {percent_subscribed:.2f}% (threshold: {THIN_CRITICAL}%)")
    elif percent_subscribed >= THIN_WARNING:
        if status != 'CRITICAL':
            status = 'WARNING'
        messages.append(f"Subscribed capacity at {percent_subscribed:.2f}% (threshold: {THIN_WARNING}%)")
    else:
        messages.append(f"Subscribed capacity at {percent_subscribed:.2f}% - OK")
    
    return {
        'status': status,
        'messages': messages,
        'metrics': {
            'total_capacity_gb': total_capacity,
            'used_capacity_gb': used_capacity,
            'subscribed_capacity_gb': subscribed_capacity,
            'percent_used': percent_used,
            'percent_subscribed': percent_subscribed
        }
    }

def analyze_health(health_data):
    """Analyze health data and return status"""
    if not health_data:
        return {'status': 'UNKNOWN', 'message': 'No health data available'}
    
    health_status = health_data.get('health', {}).get('health_score', {}).get('value', -1)
    health_state = health_data.get('health', {}).get('health_score', {}).get('description', 'UNKNOWN').upper()
    
    if health_state == 'OK' or health_status == 100:
        return {'status': 'OK', 'message': f"Array health is {health_state} (score: {health_status})"}
    elif health_state == 'WARNING' or (health_status < 100 and health_status >= 80):
        return {'status': 'WARNING', 'message': f"Array health is {health_state} (score: {health_status})"}
    else:
        return {'status': 'CRITICAL', 'message': f"Array health is {health_state} (score: {health_status})"}

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PowerMax 8000 Health and Capacity Check')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    args = parser.parse_args()
    
    # Initialize connection
    conn = initialize_connection()
    
    # Collect data
    health_data = check_array_health(conn)
    srp_data = check_srp_capacity(conn)
    alerts = check_alerts(conn)
    
    # Analyze data
    health_status = analyze_health(health_data)
    capacity_status = analyze_capacity(srp_data)
    
    # Prepare output
    output = {
        'timestamp': datetime.datetime.now().isoformat(),
        'array_id': ARRAY_ID,
        'health': health_status,
        'capacity': capacity_status,
        'recent_alerts': len(alerts) if alerts else 0
    }
    
    # Output results
    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"PowerMax 8000 Health and Capacity Report - {output['timestamp']}")
        print(f"Array ID: {output['array_id']}")
        print("\nHealth Status:")
        print(f"  Status: {output['health']['status']}")
        print(f"  Details: {output['health']['message']}")
        
        print("\nCapacity Status:")
        print(f"  Status: {output['capacity']['status']}")
        for msg in output['capacity']['messages']:
            print(f"  - {msg}")
        
        print(f"\nRecent Alerts (last 24 hours): {output['recent_alerts']}")
        
        # Exit code for monitoring systems (Nagios, etc.)
        if 'CRITICAL' in [output['health']['status'], output['capacity']['status']]:
            sys.exit(2)
        elif 'WARNING' in [output['health']['status'], output['capacity']['status']]:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == '__main__':
    main()