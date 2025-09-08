"""
Wallet management system with persistence and monitoring capabilities.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
import os

from .config import settings

logger = logging.getLogger(__name__)

class WalletManager:
    """Manages user wallets with persistence and monitoring"""
    
    def __init__(self):
        self.wallets = {}
        self.wallet_file = settings.wallet_data_file
        self.metrics = {
            "total_wallets": 0,
            "total_balance": 0.0,
            "last_update": datetime.utcnow(),
            "operations_count": 0
        }
        self.load_from_file()
        
        # Start auto-save task
        asyncio.create_task(self._auto_save_loop())
    
    def load_from_file(self):
        """Load wallet data from file"""
        try:
            if os.path.exists(self.wallet_file):
                with open(self.wallet_file, 'r') as f:
                    self.wallets = json.load(f)
                logger.info(f"Loaded {len(self.wallets)} wallets from {self.wallet_file}")
            else:
                logger.info(f"Wallet file {self.wallet_file} not found, starting with empty wallets")
                self.wallets = {}
        except Exception as e:
            logger.error(f"Failed to load wallet data: {e}")
            self.wallets = {}
        
        self._update_metrics()
    
    def save_to_file(self):
        """Save wallet data to file"""
        try:
            # Create backup first
            if os.path.exists(self.wallet_file):
                backup_file = f"{self.wallet_file}.backup"
                with open(self.wallet_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            # Save current data
            with open(self.wallet_file, 'w') as f:
                json.dump(self.wallets, f, indent=2, default=str)
            
            logger.debug(f"Saved {len(self.wallets)} wallets to {self.wallet_file}")
            
        except Exception as e:
            logger.error(f"Failed to save wallet data: {e}")
    
    async def _auto_save_loop(self):
        """Automatically save wallet data periodically"""
        while True:
            try:
                await asyncio.sleep(300)  # Save every 5 minutes
                self.save_to_file()
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")
    
    def get_wallet(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get wallet for a user"""
        return self.wallets.get(user_id)
    
    def create_wallet(self, user_id: str, initial_balance: float = 0.0) -> Dict[str, Any]:
        """Create a new wallet for a user"""
        if user_id in self.wallets:
            logger.warning(f"Wallet already exists for user {user_id}")
            return self.wallets[user_id]
        
        wallet = {
            "user_id": user_id,
            "balance": initial_balance,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "transaction_count": 0,
            "total_received": 0.0,
            "total_sent": 0.0,
            "status": "active"
        }
        
        self.wallets[user_id] = wallet
        self._update_metrics()
        self.metrics["operations_count"] += 1
        
        logger.info(f"Created wallet for user {user_id} with balance {initial_balance}")
        return wallet
    
    def update_balance(self, user_id: str, amount: float, operation_type: str = "adjustment") -> bool:
        """Update wallet balance"""
        if user_id not in self.wallets:
            logger.error(f"Wallet not found for user {user_id}")
            return False
        
        wallet = self.wallets[user_id]
        old_balance = wallet["balance"]
        
        wallet["balance"] += amount
        wallet["last_updated"] = datetime.utcnow()
        wallet["transaction_count"] += 1
        
        # Track totals
        if amount > 0:
            wallet["total_received"] += amount
        else:
            wallet["total_sent"] += abs(amount)
        
        self._update_metrics()
        self.metrics["operations_count"] += 1
        
        logger.info(f"Updated balance for user {user_id}: {old_balance} -> {wallet['balance']} ({operation_type})")
        return True
    
    def transfer(self, from_user: str, to_user: str, amount: float) -> bool:
        """Transfer funds between wallets"""
        if amount <= 0:
            logger.error("Transfer amount must be positive")
            return False
        
        # Check if both wallets exist
        if from_user not in self.wallets:
            logger.error(f"Source wallet not found: {from_user}")
            return False
        
        if to_user not in self.wallets:
            logger.error(f"Destination wallet not found: {to_user}")
            return False
        
        # Check sufficient balance
        if self.wallets[from_user]["balance"] < amount:
            logger.error(f"Insufficient balance for user {from_user}")
            return False
        
        # Perform transfer
        self.update_balance(from_user, -amount, "transfer_out")
        self.update_balance(to_user, amount, "transfer_in")
        
        logger.info(f"Transferred {amount} from {from_user} to {to_user}")
        return True
    
    def get_all_wallets(self) -> Dict[str, Dict[str, Any]]:
        """Get all wallets"""
        return self.wallets.copy()
    
    def get_wallet_count(self) -> int:
        """Get total number of wallets"""
        return len(self.wallets)
    
    def get_total_balance(self) -> float:
        """Get total balance across all wallets"""
        return sum(wallet.get("balance", 0.0) for wallet in self.wallets.values())
    
    def _update_metrics(self):
        """Update wallet metrics"""
        self.metrics.update({
            "total_wallets": len(self.wallets),
            "total_balance": self.get_total_balance(),
            "last_update": datetime.utcnow()
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get wallet system metrics"""
        active_wallets = sum(
            1 for wallet in self.wallets.values() 
            if wallet.get("status") == "active"
        )
        
        recent_activity = sum(
            1 for wallet in self.wallets.values()
            if isinstance(wallet.get("last_updated"), datetime) and
            wallet["last_updated"] > datetime.utcnow() - timedelta(hours=24)
        )
        
        return {
            "total_wallets": self.metrics["total_wallets"],
            "active_wallets": active_wallets,
            "total_balance": round(self.metrics["total_balance"], 2),
            "operations_count": self.metrics["operations_count"],
            "recent_activity_24h": recent_activity,
            "last_update": self.metrics["last_update"].isoformat(),
            "file_status": "exists" if os.path.exists(self.wallet_file) else "missing"
        }
    
    def get_user_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get summary for a specific user"""
        if user_id not in self.wallets:
            return None
        
        wallet = self.wallets[user_id]
        return {
            "user_id": user_id,
            "balance": wallet.get("balance", 0.0),
            "transaction_count": wallet.get("transaction_count", 0),
            "total_received": wallet.get("total_received", 0.0),
            "total_sent": wallet.get("total_sent", 0.0),
            "status": wallet.get("status", "unknown"),
            "created_at": wallet.get("created_at"),
            "last_updated": wallet.get("last_updated")
        }
    
    def validate_wallet_integrity(self) -> Dict[str, Any]:
        """Validate wallet data integrity"""
        issues = []
        
        for user_id, wallet in self.wallets.items():
            # Check required fields
            required_fields = ["balance", "created_at", "last_updated"]
            for field in required_fields:
                if field not in wallet:
                    issues.append(f"Missing field '{field}' in wallet {user_id}")
            
            # Check balance is numeric
            try:
                float(wallet.get("balance", 0))
            except (ValueError, TypeError):
                issues.append(f"Invalid balance in wallet {user_id}")
            
            # Check negative balance
            if wallet.get("balance", 0) < 0:
                issues.append(f"Negative balance in wallet {user_id}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_wallets_checked": len(self.wallets)
        }

# Import timedelta for metrics calculation
from datetime import timedelta