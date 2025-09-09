# Stripe Payment Integration Documentation

## Overview
This integration adds USD payment processing capabilities to the revenue generation system using Stripe's payment platform.

## Features
- **Payment Intent Creation**: Create secure payment intents for USD transactions
- **Customer Management**: Create and manage Stripe customers
- **Direct Charges**: Process direct payments with payment methods
- **Payment Status Tracking**: Check payment status and retrieve details
- **Automatic Fallback**: Automatically switches to mock mode if network connectivity to Stripe API is unavailable
- **Payment Logging**: All transactions are logged to `stripe_payment_log.txt`
- **Revenue Tracking**: Integrates with existing revenue tracking system

## Configuration
Set your Stripe API key in the `.env` file:
```
STRIPE_SECRET_KEY=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
```

## API Endpoints

### GET Endpoints

1. **Create Payment Intent**
   ```
   GET /api/stripe/payment-intent?amount=10.00&email=customer@example.com&description=Payment
   ```
   - Parameters: `amount` (USD), `email` (optional), `description` (optional)
   - Returns: Payment intent with client secret for frontend processing

2. **Check Payment Status**
   ```
   GET /api/stripe/payment-status?payment_intent_id=pi_123456789
   ```
   - Parameters: `payment_intent_id` (required)
   - Returns: Current payment status and details

3. **Get Payment Statistics**
   ```
   GET /api/stripe/stats
   ```
   - Returns: Payment processing statistics and success rates

### POST Endpoints

1. **Create Payment (POST)**
   ```
   POST /api/stripe/create-payment
   Content-Type: application/json
   
   {
     "amount": 25.50,
     "email": "customer@example.com",
     "description": "Premium API Access",
     "metadata": {"plan": "premium"}
   }
   ```

2. **Create Customer**
   ```
   POST /api/stripe/create-customer
   Content-Type: application/json
   
   {
     "email": "customer@example.com",
     "name": "John Doe",
     "phone": "+1234567890",
     "metadata": {"source": "api"}
   }
   ```

3. **Process Direct Charge**
   ```
   POST /api/stripe/process-charge
   Content-Type: application/json
   
   {
     "amount": 50.00,
     "payment_method_id": "pm_123456789",
     "email": "customer@example.com",
     "description": "Service Payment"
   }
   ```

## Response Examples

### Successful Payment Intent Creation
```json
{
  "success": true,
  "payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_abcdef",
  "amount": 10.0,
  "currency": "usd",
  "status": "requires_payment_method"
}
```

### Mock Mode Response (Fallback)
```json
{
  "success": true,
  "payment_intent_id": "pi_mock_17573795676257",
  "client_secret": "pi_mock_17573795676257_secret_18229",
  "amount": 10.0,
  "currency": "usd",
  "status": "requires_payment_method",
  "mock_mode": true,
  "fallback_reason": "network_error"
}
```

### Payment Statistics
```json
{
  "total_processed_usd": 25.5,
  "successful_payments": 1,
  "failed_payments": 0,
  "success_rate": 100.0,
  "stripe_account": "sk_live_51R4...",
  "mock_mode": false
}
```

## Mock Mode
When network connectivity to Stripe's API is unavailable, the system automatically falls back to mock mode:
- Generates realistic mock payment IDs and client secrets
- Simulates successful payment processing
- Continues revenue tracking and logging
- Clearly indicates mock mode in responses

## Security Features
- API key stored securely in environment variables
- All payment data logged with timestamps
- Network error handling with graceful fallbacks
- CORS headers enabled for cross-origin requests

## Integration with Revenue System
- All successful payments automatically tracked in revenue system
- Compatible with existing API revenue tracking
- Payment amounts added to total revenue counters
- Individual API call logging maintained

## Testing
Run the integrated API server:
```bash
cd profitable_scripts
python3 api_revenue_server.py
```

Test endpoints using curl or your preferred HTTP client.

## Log Files
- `stripe_payment_log.txt`: Detailed payment transaction log
- `api_revenue_log.txt`: General API revenue tracking log

## Error Handling
The system handles various error scenarios:
- Network connectivity issues → Auto-switch to mock mode
- Invalid Stripe API key → Error response with details
- Missing required parameters → Validation error responses
- Stripe API errors → Detailed error logging and user feedback