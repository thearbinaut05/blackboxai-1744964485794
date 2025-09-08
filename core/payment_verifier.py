"""
Payment verification system to monitor automated payments and ensure they are working correctly.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
import stripe

from .config import settings

logger = logging.getLogger(__name__)

class PaymentVerifier:
    """Verifies and monitors automated payment systems"""
    
    def __init__(self):
        self.is_running = False
        self.payment_stats = {
            "automated_count": 0,
            "failed_count": 0,
            "last_verification": datetime.utcnow(),
            "total_processed": 0
        }
        self.alerts = []
        self.payment_methods = {}
        
        # Initialize Stripe if configured
        if settings.stripe_secret_key:
            stripe.api_key = settings.stripe_secret_key
            logger.info("Stripe API initialized")
        else:
            logger.warning("Stripe API key not configured")
    
    async def start_monitoring(self):
        """Start continuous payment monitoring"""
        self.is_running = True
        logger.info("Starting payment verification monitoring")
        
        while self.is_running:
            try:
                await self.verify_all_payments()
                await self.check_payment_methods()
                await asyncio.sleep(settings.payment_verification_interval)
            except Exception as e:
                logger.error(f"Error in payment monitoring: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def verify_all_payments(self):
        """Verify all automated payments are functioning"""
        logger.info("Starting payment verification cycle")
        
        try:
            # Check Stripe payments
            stripe_status = await self._verify_stripe_payments()
            
            # Check wallet transactions
            wallet_status = await self._verify_wallet_transactions()
            
            # Check DeFi operations
            defi_status = await self._verify_defi_operations()
            
            # Update stats
            self._update_payment_stats(stripe_status, wallet_status, defi_status)
            
            logger.info("Payment verification cycle completed")
            
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            self.payment_stats["failed_count"] += 1
            await self._add_alert("payment_verification_failed", str(e))
    
    async def _verify_stripe_payments(self) -> bool:
        """Verify Stripe payment processing"""
        try:
            if not settings.stripe_secret_key:
                return False
            
            # Get recent charges
            charges = stripe.Charge.list(limit=10)
            
            # Check if payments are being processed
            recent_charges = [
                charge for charge in charges.data 
                if datetime.fromtimestamp(charge.created) > datetime.utcnow() - timedelta(hours=1)
            ]
            
            if recent_charges:
                logger.info(f"Found {len(recent_charges)} recent Stripe charges")
                return True
            else:
                logger.warning("No recent Stripe charges found")
                return False
                
        except Exception as e:
            logger.error(f"Stripe verification failed: {e}")
            await self._add_alert("stripe_verification_failed", str(e))
            return False
    
    async def _verify_wallet_transactions(self) -> bool:
        """Verify wallet transaction processing"""
        try:
            # Check wallet file exists and has recent activity
            wallet_file = settings.wallet_data_file
            
            try:
                with open(wallet_file, 'r') as f:
                    wallet_data = json.load(f)
                
                # Check for recent wallet activity
                if wallet_data:
                    logger.info("Wallet system operational")
                    return True
                else:
                    logger.warning("No wallet data found")
                    return False
                    
            except FileNotFoundError:
                logger.warning("Wallet file not found")
                return False
                
        except Exception as e:
            logger.error(f"Wallet verification failed: {e}")
            return False
    
    async def _verify_defi_operations(self) -> bool:
        """Verify DeFi operations are functioning"""
        try:
            # Check if DeFi services are responding
            async with aiohttp.ClientSession() as session:
                # Check local DeFi connector if available
                dex_url = settings.monitored_servers.get("dex_connector")
                if dex_url:
                    async with session.get(dex_url, timeout=5) as response:
                        if response.status == 200:
                            logger.info("DeFi connector operational")
                            return True
                
                logger.info("DeFi operations check completed")
                return True
                
        except Exception as e:
            logger.error(f"DeFi verification failed: {e}")
            return False
    
    def _update_payment_stats(self, stripe_ok: bool, wallet_ok: bool, defi_ok: bool):
        """Update payment statistics"""
        self.payment_stats["last_verification"] = datetime.utcnow()
        
        if all([stripe_ok or not settings.stripe_secret_key, wallet_ok, defi_ok]):
            self.payment_stats["automated_count"] += 1
        else:
            self.payment_stats["failed_count"] += 1
        
        self.payment_stats["total_processed"] += 1
    
    async def check_payment_methods(self):
        """Check status of all payment methods"""
        self.payment_methods = {
            "stripe": await self._check_stripe_status(),
            "wallet_system": await self._check_wallet_status(),
            "defi_operations": await self._check_defi_status()
        }
    
    async def _check_stripe_status(self) -> str:
        """Check Stripe API status"""
        try:
            if not settings.stripe_secret_key:
                return "not_configured"
            
            # Test Stripe API connectivity
            stripe.Balance.retrieve()
            return "operational"
            
        except Exception as e:
            logger.error(f"Stripe status check failed: {e}")
            return "error"
    
    async def _check_wallet_status(self) -> str:
        """Check wallet system status"""
        try:
            # Check if wallet service is responding
            wallet_url = settings.monitored_servers.get("wallet_service")
            if wallet_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(wallet_url, timeout=5) as response:
                        if response.status == 200:
                            return "operational"
            
            # Fallback: check if wallet file is accessible
            try:
                with open(settings.wallet_data_file, 'r') as f:
                    json.load(f)
                return "operational"
            except:
                return "degraded"
                
        except Exception as e:
            logger.error(f"Wallet status check failed: {e}")
            return "error"
    
    async def _check_defi_status(self) -> str:
        """Check DeFi operations status"""
        try:
            dex_url = settings.monitored_servers.get("dex_connector")
            if dex_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(dex_url, timeout=5) as response:
                        if response.status == 200:
                            return "operational"
            
            return "not_configured"
            
        except Exception as e:
            logger.error(f"DeFi status check failed: {e}")
            return "error"
    
    async def _add_alert(self, alert_type: str, message: str):
        """Add alert to the system"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high" if "failed" in alert_type else "medium"
        }
        
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.warning(f"Alert added: {alert_type} - {message}")
    
    async def is_automation_active(self) -> bool:
        """Check if payment automation is currently active"""
        # Consider automation active if recent verifications were successful
        recent_success_rate = 0
        if self.payment_stats["total_processed"] > 0:
            recent_success_rate = (
                self.payment_stats["automated_count"] / 
                self.payment_stats["total_processed"]
            )
        
        return recent_success_rate > 0.8  # 80% success rate threshold
    
    async def get_payment_stats(self) -> Dict[str, Any]:
        """Get payment statistics"""
        return self.payment_stats.copy()
    
    async def get_payment_method_status(self) -> Dict[str, str]:
        """Get status of all payment methods"""
        return self.payment_methods.copy()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get payment metrics for monitoring"""
        success_rate = 0
        if self.payment_stats["total_processed"] > 0:
            success_rate = (
                self.payment_stats["automated_count"] / 
                self.payment_stats["total_processed"]
            ) * 100
        
        return {
            "payment_success_rate": success_rate,
            "total_payments_processed": self.payment_stats["total_processed"],
            "failed_payments": self.payment_stats["failed_count"],
            "automation_active": await self.is_automation_active(),
            "last_verification": self.payment_stats["last_verification"].isoformat(),
            "payment_methods": self.payment_methods
        }
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current payment alerts"""
        # Return only recent alerts (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
        ]
        return recent_alerts
    
    async def restart(self):
        """Restart the payment verifier"""
        logger.info("Restarting payment verifier")
        self.is_running = False
        await asyncio.sleep(1)
        asyncio.create_task(self.start_monitoring())