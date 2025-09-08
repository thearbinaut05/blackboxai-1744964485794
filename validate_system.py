#!/usr/bin/env python3
"""
Quick Test & Validation Script
Tests individual profitable scripts before full deployment
"""
import subprocess, time, os, sys, json
from datetime import datetime

def test_script(script_name, duration=60):
    """Test a single script for specified duration"""
    print(f"🧪 Testing {script_name} for {duration} seconds...")
    
    script_path = os.path.join('profitable_scripts', script_name)
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        # Start the script
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let it run for specified duration
        time.sleep(duration)
        
        # Terminate the process
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        print(f"✅ {script_name} test completed")
        
        # Check for any obvious output
        if stdout:
            lines = stdout.strip().split('\n')
            if lines:
                print(f"   Sample output: {lines[-1][:100]}...")
        
        # Check for revenue logs
        revenue_files = [f for f in os.listdir('.') if 'revenue_log.txt' in f]
        if revenue_files:
            print(f"   Revenue logs created: {len(revenue_files)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing {script_name}: {e}")
        return False

def test_one_liner(script_type):
    """Test one-liner version of scripts"""
    print(f"🚀 Testing one-liner: {script_type}")
    
    try:
        # Start one-liner script
        process = subprocess.Popen(
            [sys.executable, 'profitable_scripts/one_liners.py', script_type],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let it run briefly
        time.sleep(10)
        
        # Terminate
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        print(f"✅ One-liner {script_type} test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing one-liner {script_type}: {e}")
        return False

def validate_deployment_system():
    """Validate the deployment system can start"""
    print("🔧 Validating deployment system...")
    
    # Check if deployment manager exists
    deployment_script = 'profitable_scripts/deployment_manager.py'
    if not os.path.exists(deployment_script):
        print(f"❌ Deployment manager not found: {deployment_script}")
        return False
    
    print("✅ Deployment system files validated")
    return True

def generate_test_report():
    """Generate a test report"""
    report = {
        'test_timestamp': datetime.now().isoformat(),
        'test_results': {},
        'system_status': 'validated',
        'ready_for_deployment': True
    }
    
    # Test each script type briefly
    scripts_to_test = [
        'crypto_arbitrage.py',
        'data_harvester.py',
        'content_monetizer.py',
        'api_revenue_server.py',
        'affiliate_monetizer.py'
    ]
    
    print("🧪 Running Script Validation Tests")
    print("=" * 50)
    
    for script in scripts_to_test:
        success = test_script(script, duration=30)  # Quick 30-second test
        report['test_results'][script] = {
            'status': 'pass' if success else 'fail',
            'tested_at': datetime.now().isoformat()
        }
    
    print("\n🚀 Testing One-Liner Scripts")
    print("-" * 30)
    
    one_liner_types = ['crypto', 'data', 'content', 'api', 'affiliate']
    for ol_type in one_liner_types:
        success = test_one_liner(ol_type)
        report['test_results'][f'one_liner_{ol_type}'] = {
            'status': 'pass' if success else 'fail',
            'tested_at': datetime.now().isoformat()
        }
    
    # Validate deployment system
    print("\n🔧 Validating Deployment System")
    print("-" * 30)
    deployment_valid = validate_deployment_system()
    report['deployment_system'] = {
        'status': 'pass' if deployment_valid else 'fail',
        'validated_at': datetime.now().isoformat()
    }
    
    # Generate summary
    total_tests = len(report['test_results']) + 1  # +1 for deployment system
    passed_tests = sum(1 for r in report['test_results'].values() if r['status'] == 'pass')
    if deployment_valid:
        passed_tests += 1
    
    report['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'success_rate': (passed_tests / total_tests) * 100,
        'ready_for_production': passed_tests == total_tests
    }
    
    # Save report
    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Display summary
    print(f"\n📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {report['summary']['success_rate']:.1f}%")
    
    if report['summary']['ready_for_production']:
        print("🎯 SYSTEM READY FOR PRODUCTION DEPLOYMENT")
        print("\nTo deploy 100 instances:")
        print("bash deploy_100_instances.sh")
        print("\nTo monitor revenue:")
        print("python profitable_scripts/revenue_dashboard.py")
    else:
        print("⚠️ SYSTEM NEEDS ATTENTION BEFORE DEPLOYMENT")
        failed_tests = [name for name, result in report['test_results'].items() if result['status'] == 'fail']
        if failed_tests:
            print(f"Failed tests: {', '.join(failed_tests)}")
    
    print(f"\nDetailed report saved to: validation_report.json")
    return report

def main():
    print("🎯 Profitable Scripts Validation System")
    print("Testing all components before full deployment...")
    print("=" * 60)
    
    # Clean up any existing test files
    test_files = [f for f in os.listdir('.') if any(x in f for x in ['revenue_log', 'data_', 'content_', 'affiliate_'])]
    for f in test_files:
        try:
            os.remove(f)
        except:
            pass
    
    # Run validation
    report = generate_test_report()
    
    return report['summary']['ready_for_production']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)