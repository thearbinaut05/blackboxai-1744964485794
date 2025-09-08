#!/usr/bin/env python3
"""
Test script for click-clack-cash-flow payment verification and monitoring system.
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime

async def test_endpoint(session, url, description):
    """Test a specific endpoint"""
    try:
        async with session.get(url) as response:
            data = await response.json()
            status = "✅ PASS" if response.status == 200 else f"❌ FAIL ({response.status})"
            print(f"{status} - {description}")
            if response.status != 200:
                print(f"    Error: {data}")
            return response.status == 200
    except Exception as e:
        print(f"❌ FAIL - {description}")
        print(f"    Error: {e}")
        return False

async def test_payment_verification():
    """Test payment verification functionality"""
    print("\n🧪 Testing Payment Verification System...")
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        tests = [
            (f"{base_url}/health", "Health Check"),
            (f"{base_url}/", "System Overview"),
            (f"{base_url}/payment-status", "Payment Status"),
            (f"{base_url}/server-status", "Server Status"),
            (f"{base_url}/metrics", "System Metrics"),
            (f"{base_url}/alerts", "Active Alerts"),
        ]
        
        results = []
        for url, description in tests:
            result = await test_endpoint(session, url, description)
            results.append(result)
        
        print(f"\n📊 Test Results: {sum(results)}/{len(results)} tests passed")
        
        # Test payment verification trigger
        try:
            async with session.post(f"{base_url}/verify-payments") as response:
                if response.status == 200:
                    print("✅ PASS - Payment Verification Trigger")
                else:
                    print(f"❌ FAIL - Payment Verification Trigger ({response.status})")
        except Exception as e:
            print(f"❌ FAIL - Payment Verification Trigger: {e}")
        
        return all(results)

def create_test_wallet():
    """Create test wallet data"""
    print("\n👛 Creating test wallet data...")
    
    test_wallets = {
        "user123": {
            "user_id": "user123",
            "balance": 1000.0,
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "transaction_count": 5,
            "total_received": 1200.0,
            "total_sent": 200.0,
            "status": "active"
        },
        "user456": {
            "user_id": "user456",
            "balance": 500.0,
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "transaction_count": 3,
            "total_received": 750.0,
            "total_sent": 250.0,
            "status": "active"
        }
    }
    
    try:
        with open("wallets.json", "w") as f:
            json.dump(test_wallets, f, indent=2)
        print("✅ Test wallet data created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create test wallet data: {e}")
        return False

async def test_wallet_endpoints():
    """Test wallet-related endpoints"""
    print("\n👛 Testing Wallet Endpoints...")
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test getting existing wallet
        result1 = await test_endpoint(session, f"{base_url}/wallet/user123", "Get Wallet - user123")
        
        # Test getting non-existent wallet
        try:
            async with session.get(f"{base_url}/wallet/nonexistent") as response:
                if response.status == 404:
                    print("✅ PASS - Get Non-existent Wallet (404 expected)")
                    result2 = True
                else:
                    print(f"❌ FAIL - Get Non-existent Wallet (Expected 404, got {response.status})")
                    result2 = False
        except Exception as e:
            print(f"❌ FAIL - Get Non-existent Wallet: {e}")
            result2 = False
        
        return result1 and result2

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
        print("✅ Uvicorn available")
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import aiohttp
        print("✅ aiohttp available")
    except ImportError:
        missing_deps.append("aiohttp")
    
    try:
        import stripe
        print("✅ Stripe available")
    except ImportError:
        missing_deps.append("stripe")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install -r swarm/requirements.txt")
        return False
    
    print("✅ All dependencies available")
    return True

async def wait_for_service(max_attempts=30):
    """Wait for the service to start"""
    print("⏳ Waiting for service to start...")
    
    for attempt in range(max_attempts):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health") as response:
                    if response.status == 200:
                        print("✅ Service is running")
                        return True
        except:
            pass
        
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        await asyncio.sleep(2)
    
    print("❌ Service did not start within expected time")
    return False

async def main():
    """Main test function"""
    print("🏦 Click-Clack-Cash-Flow System Test")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create test data
    if not create_test_wallet():
        sys.exit(1)
    
    # Wait for service
    if not await wait_for_service():
        print("\n💡 Make sure to start the service first:")
        print("   ./scripts/start.sh")
        sys.exit(1)
    
    # Run tests
    payment_test = await test_payment_verification()
    wallet_test = await test_wallet_endpoints()
    
    print("\n" + "=" * 50)
    if payment_test and wallet_test:
        print("🎉 ALL TESTS PASSED")
        print("\n✅ Payment verification system is working correctly")
        print("✅ Server monitoring is operational")
        print("✅ Wallet system is functional")
        print("\n🌐 Open dashboard.html in a browser to view real-time monitoring")
        print("📊 Use ./scripts/monitor.sh for command-line monitoring")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check the service logs and configuration")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())