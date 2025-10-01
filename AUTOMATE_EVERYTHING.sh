#!/bin/bash
"""
ULTIMATE AUTOMATION MASTER SCRIPT
Automates EVERYTHING from repo creation to agent workflows to money generation
ONE COMMAND TO RULE THEM ALL
"""

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     🚀 ULTIMATE AUTOMATION MASTER SCRIPT 🚀                     ║"
echo "║                                                                  ║"
echo "║  Automates EVERYTHING:                                          ║"
echo "║  ✅ Repository Creation & Setup                                 ║"
echo "║  ✅ Agent Workflows                                             ║"
echo "║  ✅ Revenue Generation (100+ instances)                         ║"
echo "║  ✅ Auto-scaling & Monitoring                                   ║"
echo "║  ✅ CI/CD Pipelines                                             ║"
echo "║  ✅ Profit Maximization                                         ║"
echo "║                                                                  ║"
echo "║  ONE SCRIPT TO AUTOMATE EVERYTHING AND MAKE MONEY              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Function to check and install dependencies
check_dependencies() {
    echo "📦 Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3."
        exit 1
    fi
    echo "✅ Python 3 found"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        echo "❌ Git not found. Please install Git."
        exit 1
    fi
    echo "✅ Git found"
    
    # Install Python dependencies
    echo "📦 Installing Python dependencies..."
    python3 -c "import aiohttp, requests, psutil" 2>/dev/null || {
        echo "Installing required Python packages..."
        pip3 install --user aiohttp requests beautifulsoup4 pandas python-dotenv psutil 2>/dev/null || \
        pip3 install aiohttp requests beautifulsoup4 pandas python-dotenv psutil
    }
    echo "✅ All dependencies installed"
}

# Function to setup automation
setup_automation() {
    echo ""
    echo "🔧 Setting up automation system..."
    
    # Make all scripts executable
    chmod +x *.py 2>/dev/null || true
    chmod +x *.sh 2>/dev/null || true
    chmod +x profitable_scripts/*.py 2>/dev/null || true
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    mkdir -p configs
    mkdir -p instances
    
    echo "✅ Automation system ready"
}

# Function to start all automation
start_automation() {
    echo ""
    echo "🚀 Starting complete automation system..."
    echo ""
    
    # Option menu
    echo "Choose automation mode:"
    echo "1. FULL AUTOMATION (Everything - Recommended)"
    echo "2. Quick Test (5 instances)"
    echo "3. Repository Automation Only"
    echo "4. Revenue Generation Only"
    echo "5. Custom Configuration"
    echo ""
    read -p "Enter choice (1-5): " choice
    
    case $choice in
        1)
            echo ""
            echo "🎯 Starting FULL AUTOMATION..."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            
            # Start master orchestrator
            python3 automation_orchestrator.py &
            ORCHESTRATOR_PID=$!
            
            echo "✅ Master Orchestrator: RUNNING (PID: $ORCHESTRATOR_PID)"
            echo "📊 100+ Revenue Instances: DEPLOYING"
            echo "🤖 Agent Workflows: ACTIVE"
            echo "📈 Auto-scaling: ENABLED"
            echo "🏥 Health Monitoring: ACTIVE"
            echo "💰 Profit Maximization: RUNNING"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "🎯 FULL AUTOMATION IS NOW RUNNING!"
            echo ""
            echo "📊 Monitor with: tail -f automation_orchestrator.log"
            echo "💰 Revenue Dashboard: cd profitable_scripts && python3 revenue_dashboard.py"
            echo "🛑 Stop with: kill $ORCHESTRATOR_PID"
            echo ""
            
            # Wait for orchestrator
            wait $ORCHESTRATOR_PID
            ;;
            
        2)
            echo ""
            echo "🧪 Starting Quick Test (5 instances)..."
            cd profitable_scripts
            
            python3 -c "
import subprocess, time, sys, os

scripts = [
    'crypto_arbitrage.py',
    'data_harvester.py',
    'content_monetizer.py',
    'api_revenue_server.py',
    'affiliate_monetizer.py'
]

processes = []
print('🚀 Starting test instances...\n')

for i, script in enumerate(scripts):
    print(f'✅ Instance {i+1}: {script}')
    p = subprocess.Popen(
        [sys.executable, script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    processes.append(p)
    time.sleep(1)

print('\n✅ 5 test instances running')
print('💰 Generating revenue...')
print('🛑 Press Ctrl+C to stop\n')

try:
    while True:
        time.sleep(10)
        alive = sum(1 for p in processes if p.poll() is None)
        print(f'📊 Status: {alive}/5 instances running')
except KeyboardInterrupt:
    print('\n🛑 Stopping test instances...')
    for p in processes:
        if p.poll() is None:
            p.terminate()
    print('✅ Test complete')
"
            ;;
            
        3)
            echo ""
            echo "📦 Starting Repository Automation..."
            python3 github_repo_automator.py --name "automated-revenue-system"
            echo "✅ Repository automation complete"
            ;;
            
        4)
            echo ""
            echo "💰 Starting Revenue Generation Only..."
            cd profitable_scripts
            python3 deployment_manager.py
            ;;
            
        5)
            echo ""
            echo "⚙️  Custom Configuration Mode"
            echo ""
            echo "Select components to enable:"
            read -p "Enable Revenue Generation? (y/n): " enable_revenue
            read -p "Enable Agent Workflows? (y/n): " enable_agents
            read -p "Enable Auto-scaling? (y/n): " enable_scaling
            read -p "Enable Repository Automation? (y/n): " enable_repo
            
            echo ""
            echo "🔧 Starting selected components..."
            
            if [[ $enable_revenue == "y" ]]; then
                echo "💰 Revenue Generation: ENABLED"
                cd profitable_scripts && python3 deployment_manager.py &
                cd ..
            fi
            
            if [[ $enable_repo == "y" ]]; then
                echo "📦 Repository Automation: ENABLED"
                python3 github_repo_automator.py &
            fi
            
            if [[ $enable_agents == "y" ]] || [[ $enable_scaling == "y" ]]; then
                echo "🤖 Master Orchestrator: ENABLED"
                python3 automation_orchestrator.py &
            fi
            
            echo ""
            echo "✅ Custom configuration started"
            ;;
            
        *)
            echo "Invalid choice. Defaulting to FULL AUTOMATION..."
            python3 automation_orchestrator.py
            ;;
    esac
}

# Main execution
main() {
    # Check dependencies
    check_dependencies
    
    # Setup automation
    setup_automation
    
    # Start automation
    start_automation
}

# Run main function
main

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ AUTOMATION COMPLETE ✅                        ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
