#!/usr/bin/env python3
"""
Quick Status Checker
Check status of all automation systems
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def check_file_exists(filepath):
    """Check if file exists"""
    return Path(filepath).exists()


def check_process_running(process_name):
    """Check if process is running"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', process_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def load_json_file(filepath):
    """Load JSON file if it exists"""
    if check_file_exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {'error': str(e)}
    return None


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_status(label, status, details=""):
    """Print formatted status line"""
    symbol = "✅" if status else "❌"
    status_text = "RUNNING" if status else "STOPPED"
    print(f"{symbol} {label:30s} {status_text:10s} {details}")


def main():
    """Main status check"""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "AUTOMATION SYSTEM STATUS" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Check Core Services
    print_header("Core Services")
    
    orchestrator_running = check_process_running('automation_orchestrator.py')
    print_status("Master Orchestrator", orchestrator_running)
    
    deployment_running = check_process_running('deployment_manager.py')
    print_status("Deployment Manager", deployment_running)
    
    dashboard_running = check_process_running('revenue_dashboard.py')
    print_status("Revenue Dashboard", dashboard_running)
    
    # Check Configuration Files
    print_header("Configuration Files")
    
    configs = [
        'repo_automation_config.json',
        'agent_workflows_config.json',
        'recovery_config.json',
        'cicd_automation_config.json',
        'unified_dashboard_config.json'
    ]
    
    for config in configs:
        exists = check_file_exists(config)
        print_status(config, exists)
    
    # Check Instances
    print_header("Revenue Instances")
    
    instances_dir = Path('profitable_scripts/instances')
    if instances_dir.exists():
        instance_count = len([d for d in instances_dir.iterdir() if d.is_dir()])
        print(f"📊 Total Instances: {instance_count}")
        
        # Check running instances
        running_count = 0
        for instance in instances_dir.iterdir():
            if instance.is_dir():
                # Check if instance has active process
                output_log = instance / 'output.log'
                if output_log.exists():
                    running_count += 1
        
        print(f"✅ Running Instances: {running_count}/{instance_count}")
    else:
        print("❌ No instances directory found")
    
    # Check Revenue Data
    print_header("Revenue Analytics")
    
    revenue_file = Path('profitable_scripts/revenue_analytics_report.json')
    if revenue_file.exists():
        revenue_data = load_json_file(revenue_file)
        if revenue_data and 'summary' in revenue_data:
            summary = revenue_data['summary']
            print(f"💰 Total Revenue: ${summary.get('total_revenue', 0):.2f}")
            print(f"📊 Active Instances: {summary.get('active_instances', 0)}")
            print(f"📈 Total Instances: {summary.get('total_instances', 0)}")
        else:
            print("⚠️  Revenue data format error")
    else:
        print("⚠️  No revenue data available yet")
    
    # Check Logs
    print_header("Recent Activity")
    
    log_file = Path('automation_orchestrator.log')
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-5:] if len(lines) >= 5 else lines
                print("\nLast 5 log entries:")
                for line in recent_lines:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"❌ Error reading log: {e}")
    else:
        print("⚠️  No log file found")
    
    # System Summary
    print_header("System Summary")
    
    total_services = 3
    running_services = sum([orchestrator_running, deployment_running, dashboard_running])
    
    print(f"📊 Services: {running_services}/{total_services} running")
    
    if running_services == total_services:
        print("✅ All systems operational!")
        status_code = 0
    elif running_services > 0:
        print("⚠️  Some systems are down")
        status_code = 1
    else:
        print("❌ All systems are stopped")
        status_code = 2
    
    # Next Steps
    print_header("Quick Commands")
    print("🚀 Start Everything:  ./AUTOMATE_EVERYTHING.sh")
    print("📊 View Dashboard:    cd profitable_scripts && python3 revenue_dashboard.py")
    print("📝 View Logs:         tail -f automation_orchestrator.log")
    print("🛑 Stop All:          pkill -f 'automation_orchestrator\\|deployment_manager'")
    
    print("\n" + "=" * 70 + "\n")
    
    return status_code


if __name__ == "__main__":
    sys.exit(main())
