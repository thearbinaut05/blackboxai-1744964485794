#!/bin/bash

# Monitor script for checking system status

echo "=== Click-Clack-Cash-Flow System Status ==="
echo

# Check if the service is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Main service is running"
    
    # Get overall health
    echo "📊 System Health:"
    curl -s http://localhost:8000/ | python3 -m json.tool
    echo
    
    # Get payment status
    echo "💳 Payment Status:"
    curl -s http://localhost:8000/payment-status | python3 -m json.tool
    echo
    
    # Get server status
    echo "🖥️  Server Status:"
    curl -s http://localhost:8000/server-status | python3 -m json.tool
    echo
    
    # Get alerts
    echo "⚠️  Active Alerts:"
    curl -s http://localhost:8000/alerts | python3 -m json.tool
    echo
    
    # Get metrics
    echo "📈 Metrics:"
    curl -s http://localhost:8000/metrics | python3 -m json.tool
    
else
    echo "❌ Main service is not running"
    echo "   Start with: ./scripts/start.sh"
fi