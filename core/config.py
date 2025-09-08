"""
Configuration settings for the click-clack-cash-flow system.
"""

import os
from typing import Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Stripe Configuration
    stripe_public_key: str = os.getenv("STRIPE_PUBLIC_KEY", "")
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Monitoring Configuration
    monitoring_interval: int = 30  # seconds
    payment_verification_interval: int = 60  # seconds
    server_health_check_interval: int = 15  # seconds
    
    # Payment Thresholds
    min_payment_amount: float = 0.01
    max_payment_failures: int = 5
    payment_timeout: int = 300  # seconds
    
    # Server Configuration
    monitored_servers: Dict[str, str] = {
        "stripe_api": "https://api.stripe.com/v1/charges",
        "payment_processor": "http://localhost:8001/health",
        "wallet_service": "http://localhost:8002/health",
        "dex_connector": "http://localhost:8003/health"
    }
    
    # Database Configuration
    wallet_data_file: str = "wallets.json"
    payment_log_file: str = "payment_log.json"
    monitoring_log_file: str = "monitoring.log"
    
    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
    token_expiry: int = 3600  # seconds
    
    # Performance Configuration
    max_concurrent_payments: int = 10
    payment_batch_size: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Validation function
def validate_settings() -> bool:
    """Validate critical settings"""
    required_stripe_keys = [
        settings.stripe_public_key,
        settings.stripe_secret_key
    ]
    
    if not all(required_stripe_keys):
        print("Warning: Stripe API keys not configured. Payment processing will be limited.")
        return False
    
    return True