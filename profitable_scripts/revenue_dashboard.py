#!/usr/bin/env python3
"""
Revenue Monitoring Dashboard
Real-time monitoring and analytics for all 100 profitable instances
"""
import json, time, os, threading
from datetime import datetime, timedelta
import subprocess, sys

class RevenueDashboard:
    def __init__(self):
        self.total_revenue = 0
        self.revenue_history = []
        self.instance_stats = {}
        self.running = True
        
    def collect_revenue_data(self):
        """Collect revenue data from all instances"""
        total_revenue = 0
        active_instances = 0
        
        if os.path.exists('instances'):
            for instance_dir in os.listdir('instances'):
                instance_path = os.path.join('instances', instance_dir)
                if os.path.isdir(instance_path):
                    instance_revenue = 0
                    
                    # Scan for revenue log files
                    for file in os.listdir(instance_path):
                        if 'revenue_log.txt' in file:
                            log_path = os.path.join(instance_path, file)
                            try:
                                with open(log_path, 'r') as f:
                                    lines = f.readlines()
                                    for line in lines:
                                        if ',' in line:
                                            parts = line.strip().split(',')
                                            if len(parts) >= 3:
                                                try:
                                                    revenue = float(parts[-1])
                                                    instance_revenue += revenue
                                                except ValueError:
                                                    continue
                            except Exception:
                                continue
                    
                    if instance_revenue > 0:
                        active_instances += 1
                        total_revenue += instance_revenue
                        
                        instance_id = instance_dir.replace('instance_', '')
                        self.instance_stats[instance_id] = {
                            'revenue': instance_revenue,
                            'status': 'active',
                            'last_update': datetime.now().isoformat()
                        }
        
        self.total_revenue = total_revenue
        
        # Store revenue history
        self.revenue_history.append({
            'timestamp': datetime.now().isoformat(),
            'total_revenue': total_revenue,
            'active_instances': active_instances
        })
        
        # Keep only last 100 data points
        if len(self.revenue_history) > 100:
            self.revenue_history = self.revenue_history[-100:]
        
        return total_revenue, active_instances
    
    def calculate_growth_metrics(self):
        """Calculate growth and performance metrics"""
        if len(self.revenue_history) < 2:
            return {}
        
        current = self.revenue_history[-1]
        previous = self.revenue_history[-2] if len(self.revenue_history) > 1 else current
        
        # Calculate hourly growth rate
        time_diff = (datetime.fromisoformat(current['timestamp']) - 
                    datetime.fromisoformat(previous['timestamp'])).total_seconds() / 3600
        
        if time_diff > 0:
            hourly_growth = (current['total_revenue'] - previous['total_revenue']) / time_diff
        else:
            hourly_growth = 0
        
        # Target growth rate (7.923x per hour as mentioned in original swarm readme)
        target_hourly_multiplier = 7.923
        current_multiplier = hourly_growth / max(previous['total_revenue'], 0.01) if previous['total_revenue'] > 0 else 0
        
        return {
            'hourly_growth_usd': hourly_growth,
            'hourly_multiplier': current_multiplier,
            'target_multiplier': target_hourly_multiplier,
            'growth_efficiency': (current_multiplier / target_hourly_multiplier) * 100 if target_hourly_multiplier > 0 else 0,
            'revenue_velocity': current['total_revenue'] / max(current['active_instances'], 1)
        }
    
    def display_dashboard(self):
        """Display real-time dashboard"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("💰 PROFITABLE SCRIPTS REVENUE DASHBOARD 💰")
        print("=" * 60)
        print(f"🕐 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Collect current data
        total_revenue, active_instances = self.collect_revenue_data()
        
        # Basic stats
        print("📊 CURRENT STATUS")
        print("-" * 30)
        print(f"💵 Total Revenue: ${total_revenue:.2f}")
        print(f"🔄 Active Instances: {active_instances}/100")
        print(f"📈 Revenue per Instance: ${total_revenue/max(active_instances,1):.2f}")
        print()
        
        # Growth metrics
        metrics = self.calculate_growth_metrics()
        if metrics:
            print("📈 GROWTH METRICS")
            print("-" * 30)
            print(f"⚡ Hourly Growth: ${metrics['hourly_growth_usd']:.2f}")
            print(f"🚀 Growth Multiplier: {metrics['hourly_multiplier']:.2f}x")
            print(f"🎯 Target Multiplier: {metrics['target_multiplier']:.2f}x")
            print(f"⚙️ Efficiency: {metrics['growth_efficiency']:.1f}%")
            print(f"🏃 Revenue Velocity: ${metrics['revenue_velocity']:.2f}/instance")
            print()
        
        # Top performing instances
        if self.instance_stats:
            print("🏆 TOP PERFORMING INSTANCES")
            print("-" * 30)
            sorted_instances = sorted(
                self.instance_stats.items(), 
                key=lambda x: x[1]['revenue'], 
                reverse=True
            )[:5]
            
            for i, (instance_id, stats) in enumerate(sorted_instances, 1):
                print(f"{i}. Instance {instance_id}: ${stats['revenue']:.2f}")
            print()
        
        # Revenue trend
        if len(self.revenue_history) >= 5:
            print("📊 REVENUE TREND (Last 5 Updates)")
            print("-" * 30)
            recent_history = self.revenue_history[-5:]
            for entry in recent_history:
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S')
                print(f"{timestamp}: ${entry['total_revenue']:.2f} ({entry['active_instances']} active)")
            print()
        
        # Progress towards goals
        print("🎯 PROGRESS TRACKING")
        print("-" * 30)
        
        # Daily revenue goal (assuming $1000/day target)
        daily_target = 1000
        daily_progress = (total_revenue / daily_target) * 100
        print(f"Daily Target Progress: {daily_progress:.1f}% (${total_revenue:.2f}/${daily_target})")
        
        # Instance deployment progress
        deployment_progress = (active_instances / 100) * 100
        print(f"Instance Deployment: {deployment_progress:.1f}% ({active_instances}/100)")
        
        print()
        print("🔄 Auto-refresh in 30 seconds... (Ctrl+C to stop)")
        print("=" * 60)
    
    def save_analytics_report(self):
        """Save detailed analytics report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_revenue': self.total_revenue,
                'active_instances': len([i for i in self.instance_stats.values() if i['status'] == 'active']),
                'total_instances': len(self.instance_stats)
            },
            'growth_metrics': self.calculate_growth_metrics(),
            'instance_breakdown': self.instance_stats,
            'revenue_history': self.revenue_history
        }
        
        with open('revenue_analytics_report.json', 'w') as f:
            json.dump(report, f, indent=2)
    
    def run_dashboard(self):
        """Run the dashboard continuously"""
        print("🚀 Starting Revenue Monitoring Dashboard...")
        
        while self.running:
            try:
                self.display_dashboard()
                self.save_analytics_report()
                time.sleep(30)  # Update every 30 seconds
                
            except KeyboardInterrupt:
                print("\n👋 Dashboard stopped.")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Dashboard error: {e}")
                time.sleep(10)

def main():
    dashboard = RevenueDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()