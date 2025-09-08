"""
Server monitoring system to ensure all payment-related services are live and running.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
import time

from .config import settings

logger = logging.getLogger(__name__)

class ServerMonitor:
    """Monitors server health and availability"""
    
    def __init__(self):
        self.is_running = False
        self.server_status = {}
        self.alerts = []
        self.response_times = {}
        self.uptime_stats = {}
        
        # Initialize server tracking
        for server_name in settings.monitored_servers:
            self.server_status[server_name] = False
            self.response_times[server_name] = []
            self.uptime_stats[server_name] = {
                "total_checks": 0,
                "successful_checks": 0,
                "last_check": None,
                "last_success": None,
                "consecutive_failures": 0
            }
    
    async def start_monitoring(self):
        """Start continuous server monitoring"""
        self.is_running = True
        logger.info("Starting server health monitoring")
        
        while self.is_running:
            try:
                await self.check_all_servers()
                await asyncio.sleep(settings.server_health_check_interval)
            except Exception as e:
                logger.error(f"Error in server monitoring: {e}")
                await asyncio.sleep(5)
    
    async def check_all_servers(self):
        """Check health of all monitored servers"""
        logger.debug("Checking all server health")
        
        tasks = []
        for server_name, server_url in settings.monitored_servers.items():
            task = asyncio.create_task(
                self._check_server_health(server_name, server_url)
            )
            tasks.append(task)
        
        # Wait for all health checks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for critical failures
        await self._check_critical_services()
    
    async def _check_server_health(self, server_name: str, server_url: str):
        """Check health of a specific server"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    server_url, 
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    # Update response times
                    self.response_times[server_name].append(response_time)
                    if len(self.response_times[server_name]) > 50:
                        self.response_times[server_name] = self.response_times[server_name][-50:]
                    
                    # Check if response is healthy
                    is_healthy = response.status == 200
                    
                    # Update server status
                    self.server_status[server_name] = is_healthy
                    
                    # Update uptime stats
                    stats = self.uptime_stats[server_name]
                    stats["total_checks"] += 1
                    stats["last_check"] = datetime.utcnow()
                    
                    if is_healthy:
                        stats["successful_checks"] += 1
                        stats["last_success"] = datetime.utcnow()
                        stats["consecutive_failures"] = 0
                        
                        logger.debug(f"{server_name} healthy - {response_time:.3f}s")
                    else:
                        stats["consecutive_failures"] += 1
                        logger.warning(f"{server_name} unhealthy - HTTP {response.status}")
                        await self._add_alert(
                            "server_unhealthy", 
                            f"{server_name} returned HTTP {response.status}"
                        )
        
        except asyncio.TimeoutError:
            self._handle_server_failure(server_name, "timeout")
        except aiohttp.ClientConnectionError:
            self._handle_server_failure(server_name, "connection_error")
        except Exception as e:
            self._handle_server_failure(server_name, f"error: {str(e)}")
    
    def _handle_server_failure(self, server_name: str, reason: str):
        """Handle server failure"""
        self.server_status[server_name] = False
        
        stats = self.uptime_stats[server_name]
        stats["total_checks"] += 1
        stats["last_check"] = datetime.utcnow()
        stats["consecutive_failures"] += 1
        
        logger.error(f"{server_name} check failed: {reason}")
        
        # Add alert for consecutive failures
        if stats["consecutive_failures"] >= 3:
            asyncio.create_task(self._add_alert(
                "server_down", 
                f"{server_name} has failed {stats['consecutive_failures']} consecutive health checks"
            ))
    
    async def _check_critical_services(self):
        """Check if critical services are down"""
        critical_services = ["stripe_api", "payment_processor"]
        
        down_services = []
        for service in critical_services:
            if service in self.server_status and not self.server_status[service]:
                down_services.append(service)
        
        if down_services:
            await self._add_alert(
                "critical_services_down",
                f"Critical services down: {', '.join(down_services)}"
            )
    
    async def _add_alert(self, alert_type: str, message: str):
        """Add alert to the system"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "critical" if "critical" in alert_type or "down" in alert_type else "medium"
        }
        
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.error(f"Server alert: {alert_type} - {message}")
    
    async def get_all_server_status(self) -> Dict[str, bool]:
        """Get status of all monitored servers"""
        return self.server_status.copy()
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed server status information"""
        detailed_status = {}
        
        for server_name in settings.monitored_servers:
            stats = self.uptime_stats[server_name]
            
            # Calculate uptime percentage
            uptime_pct = 0
            if stats["total_checks"] > 0:
                uptime_pct = (stats["successful_checks"] / stats["total_checks"]) * 100
            
            # Calculate average response time
            avg_response_time = 0
            if self.response_times[server_name]:
                avg_response_time = sum(self.response_times[server_name]) / len(self.response_times[server_name])
            
            detailed_status[server_name] = {
                "status": "healthy" if self.server_status.get(server_name, False) else "unhealthy",
                "url": settings.monitored_servers[server_name],
                "uptime_percentage": round(uptime_pct, 2),
                "total_checks": stats["total_checks"],
                "successful_checks": stats["successful_checks"],
                "consecutive_failures": stats["consecutive_failures"],
                "last_check": stats["last_check"].isoformat() if stats["last_check"] else None,
                "last_success": stats["last_success"].isoformat() if stats["last_success"] else None,
                "average_response_time": round(avg_response_time, 3),
                "recent_response_times": self.response_times[server_name][-10:]  # Last 10 response times
            }
        
        return detailed_status
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get server monitoring metrics"""
        total_servers = len(settings.monitored_servers)
        healthy_servers = sum(1 for status in self.server_status.values() if status)
        
        # Calculate overall system health
        system_health = (healthy_servers / total_servers) * 100 if total_servers > 0 else 0
        
        # Get critical service status
        critical_services = ["stripe_api", "payment_processor"]
        critical_healthy = sum(
            1 for service in critical_services 
            if self.server_status.get(service, False)
        )
        critical_health = (critical_healthy / len(critical_services)) * 100
        
        return {
            "total_servers": total_servers,
            "healthy_servers": healthy_servers,
            "system_health_percentage": round(system_health, 2),
            "critical_services_health": round(critical_health, 2),
            "server_status": self.server_status,
            "recent_alerts": len([
                alert for alert in self.alerts
                if datetime.fromisoformat(alert["timestamp"]) > datetime.utcnow() - timedelta(hours=1)
            ])
        }
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current server alerts"""
        # Return only recent alerts (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
        ]
        return recent_alerts
    
    async def restart(self):
        """Restart the server monitor"""
        logger.info("Restarting server monitor")
        self.is_running = False
        await asyncio.sleep(1)
        asyncio.create_task(self.start_monitoring())
    
    def get_server_uptime(self, server_name: str) -> float:
        """Get uptime percentage for a specific server"""
        if server_name not in self.uptime_stats:
            return 0.0
        
        stats = self.uptime_stats[server_name]
        if stats["total_checks"] == 0:
            return 0.0
        
        return (stats["successful_checks"] / stats["total_checks"]) * 100
    
    def is_critical_service_down(self) -> bool:
        """Check if any critical services are down"""
        critical_services = ["stripe_api", "payment_processor"]
        return any(
            not self.server_status.get(service, False) 
            for service in critical_services
        )