"""
FastAPI application for click-clack-cash-flow payment verification and monitoring system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .payment_verifier import PaymentVerifier
from .server_monitor import ServerMonitor
from .wallet import WalletManager
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Click-Clack-Cash-Flow Monitor",
    description="Payment verification and server monitoring system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
payment_verifier = PaymentVerifier()
server_monitor = ServerMonitor()
wallet_manager = WalletManager()

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
    payment_automation_active: bool
    server_health: Dict[str, bool]

class PaymentStatusResponse(BaseModel):
    automated_payments_count: int
    failed_payments_count: int
    last_verification: datetime
    payment_methods_status: Dict[str, str]

@app.on_event("startup")
async def startup_event():
    """Initialize monitoring systems on startup"""
    logger.info("Starting Click-Clack-Cash-Flow monitoring system...")
    
    # Start background monitoring tasks
    asyncio.create_task(payment_verifier.start_monitoring())
    asyncio.create_task(server_monitor.start_monitoring())
    
    logger.info("Monitoring systems started successfully")

@app.get("/", response_model=HealthResponse)
async def root():
    """Get overall system health status"""
    server_status = await server_monitor.get_all_server_status()
    payment_status = await payment_verifier.is_automation_active()
    
    return HealthResponse(
        status="healthy" if all(server_status.values()) and payment_status else "degraded",
        timestamp=datetime.utcnow(),
        services={
            "payment_verifier": "active",
            "server_monitor": "active", 
            "wallet_manager": "active"
        },
        payment_automation_active=payment_status,
        server_health=server_status
    )

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/payment-status", response_model=PaymentStatusResponse)
async def get_payment_status():
    """Get detailed payment automation status"""
    stats = await payment_verifier.get_payment_stats()
    method_status = await payment_verifier.get_payment_method_status()
    
    return PaymentStatusResponse(
        automated_payments_count=stats.get("automated_count", 0),
        failed_payments_count=stats.get("failed_count", 0),
        last_verification=stats.get("last_verification", datetime.utcnow()),
        payment_methods_status=method_status
    )

@app.get("/server-status")
async def get_server_status():
    """Get detailed server health status"""
    return await server_monitor.get_detailed_status()

@app.get("/wallet/{user_id}")
async def get_wallet(user_id: str):
    """Get wallet details for a user"""
    wallet = wallet_manager.get_wallet(user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return wallet

@app.post("/verify-payments")
async def trigger_payment_verification(background_tasks: BackgroundTasks):
    """Manually trigger payment verification"""
    background_tasks.add_task(payment_verifier.verify_all_payments)
    return {"message": "Payment verification triggered"}

@app.post("/restart-monitoring")
async def restart_monitoring():
    """Restart all monitoring services"""
    try:
        await payment_verifier.restart()
        await server_monitor.restart()
        return {"message": "Monitoring services restarted successfully"}
    except Exception as e:
        logger.error(f"Failed to restart monitoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to restart monitoring services")

@app.get("/metrics")
async def get_metrics():
    """Get system performance metrics"""
    payment_metrics = await payment_verifier.get_metrics()
    server_metrics = await server_monitor.get_metrics()
    wallet_metrics = wallet_manager.get_metrics()
    
    return {
        "payment_metrics": payment_metrics,
        "server_metrics": server_metrics,
        "wallet_metrics": wallet_metrics,
        "timestamp": datetime.utcnow()
    }

@app.get("/alerts")
async def get_active_alerts():
    """Get current system alerts"""
    payment_alerts = await payment_verifier.get_alerts()
    server_alerts = await server_monitor.get_alerts()
    
    return {
        "payment_alerts": payment_alerts,
        "server_alerts": server_alerts,
        "total_alerts": len(payment_alerts) + len(server_alerts)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)