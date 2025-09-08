# Stripe Payment Automation System

An automated payment method attachment system for Stripe that uses application revenue to fund all payments. This system provides complete automation of the payment workflow including payment method attachment, payment intent creation, and revenue management.

## 🚀 Features

- **Automated Payment Method Attachment**: Automatically attaches payment methods from application revenue to payment intents
- **Revenue-Funded Payments**: All payments are funded from application revenue pools
- **Bulk Payment Processing**: Process multiple payments in a single batch operation
- **Real-time Webhook Processing**: Handle Stripe events automatically
- **Revenue Management**: Track, reserve, and manage application funds
- **Error Handling**: Comprehensive error handling for insufficient funds and failed payments
- **Data Persistence**: All revenue and payment data is persisted to JSON files

## 📁 Project Structure

```
├── src/
│   ├── app.js                      # Main Express application
│   ├── config/
│   │   └── stripe.js              # Stripe configuration
│   ├── services/
│   │   ├── paymentMethodService.js  # Payment method management
│   │   ├── paymentIntentService.js  # Payment intent automation
│   │   └── revenueService.js       # Revenue management
│   └── routes/
│       └── payments.js             # API routes
├── scripts/
│   ├── initRevenue.js              # Initialize application revenue
│   ├── testPaymentFlow.js          # Test with real Stripe
│   └── testPaymentFlowMocked.js    # Test with mocked operations
├── data/                           # Auto-created data directory
│   ├── revenue.json               # Revenue data storage
│   └── revenue_payment_methods.json # Payment methods storage
└── package.json
```

## 🔧 Installation

1. **Clone and install dependencies**:
```bash
npm install
```

2. **Configure environment variables**:
Create a `.env` file with your Stripe credentials:
```bash
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_APPLICATION_ACCOUNT_ID=acct_your_application_account_id
NODE_ENV=development
PORT=3000
```

3. **Initialize application revenue**:
```bash
npm run init-revenue
```

4. **Start the server**:
```bash
npm start
```

## 📊 API Endpoints

### Core Payment Operations

#### Create Automated Payment
```bash
POST /api/payments/create-automated-payment
Content-Type: application/json

{
  "customerId": "cus_customer_id",
  "amount": 2000,  // Amount in cents
  "currency": "usd",
  "autoConfirm": true
}
```

#### Process Bulk Payments
```bash
POST /api/payments/bulk-payments
Content-Type: application/json

{
  "payments": [
    {
      "customerId": "cus_customer1",
      "amount": 1000,
      "currency": "usd"
    },
    {
      "customerId": "cus_customer2", 
      "amount": 1500,
      "currency": "usd"
    }
  ]
}
```

### Revenue Management

#### Add Revenue
```bash
POST /api/payments/add-revenue
Content-Type: application/json

{
  "amount": 100000,  // Amount in cents
  "currency": "usd",
  "source": "application_earnings"
}
```

#### Get Revenue Statistics
```bash
GET /api/payments/revenue-stats
```

### Manual Operations

#### Attach Payment Method
```bash
POST /api/payments/attach-payment-method
Content-Type: application/json

{
  "paymentIntentId": "pi_payment_intent_id",
  "customerId": "cus_customer_id"
}
```

#### Confirm Payment Intent
```bash
POST /api/payments/confirm-payment-intent
Content-Type: application/json

{
  "paymentIntentId": "pi_payment_intent_id"
}
```

### Webhook Handler
```bash
POST /api/payments/webhook
Content-Type: application/json
Stripe-Signature: webhook_signature_header

# Handles Stripe webhook events automatically
```

## 🧪 Testing

### Test with Mocked Operations (Recommended for Demo)
```bash
npm run test-payment-flow-mocked
```

### Test with Real Stripe (Requires valid API keys)
```bash
npm run test-payment-flow
```

### Initialize Revenue
```bash
npm run init-revenue
```

## 🔄 Automated Workflow

The system automates the entire payment process:

1. **Revenue Check**: Verifies sufficient application funds
2. **Payment Method Selection**: Automatically selects optimal payment method from revenue sources
3. **Payment Method Attachment**: Attaches selected payment method to customer
4. **Payment Intent Creation**: Creates payment intent with automated settings
5. **Fund Reservation**: Reserves funds from application revenue
6. **Payment Confirmation**: Confirms payment using reserved funds
7. **Fund Deduction**: Deducts confirmed payment from revenue
8. **Event Processing**: Handles webhook events for status updates

## 💰 Revenue Management

### Revenue Sources
- Application earnings
- Transaction fees
- Subscription payments
- API usage fees

### Fund Operations
- **Add Revenue**: Increase available balance
- **Reserve Funds**: Lock funds for pending payments
- **Deduct Funds**: Remove funds after successful payments
- **Release Funds**: Return reserved funds if payment fails

### Data Persistence
All revenue and payment data is automatically saved to JSON files:
- `data/revenue.json`: Revenue balances and transaction history
- `data/revenue_payment_methods.json`: Registered payment methods

## 🔐 Security Features

- Environment variable configuration for API keys
- Request validation and error handling
- Fund reservation system prevents double-spending
- Automatic cleanup of failed transactions
- Webhook signature verification

## 📈 Monitoring

### Health Check
```bash
GET /health
```

### Revenue Statistics
- Total revenue
- Available balance
- Reserved funds
- Payment method count
- Last update timestamp

## 🚨 Error Handling

The system handles various error scenarios:
- Insufficient application funds
- Failed Stripe API calls
- Invalid payment parameters
- Webhook processing errors
- Data persistence failures

## 🔧 Configuration

### Environment Variables
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_WEBHOOK_SECRET`: Webhook endpoint secret
- `NODE_ENV`: Environment (development/production)
- `PORT`: Server port (default: 3000)
- `INITIAL_REVENUE_AMOUNT`: Starting revenue amount in cents

### Revenue Configuration
- Default currency: USD
- Minimum payment amount: $0.50 (50 cents)
- Maximum concurrent reservations: Unlimited
- Data auto-save: After every operation

## 📝 Usage Examples

### Simple Payment
```javascript
// Create an automated payment
const response = await fetch('/api/payments/create-automated-payment', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    customerId: 'cus_example123',
    amount: 2000, // $20.00
    currency: 'usd'
  })
});
```

### Bulk Processing
```javascript
// Process multiple payments
const bulkPayments = {
  payments: [
    { customerId: 'cus_1', amount: 1000 },
    { customerId: 'cus_2', amount: 1500 },
    { customerId: 'cus_3', amount: 2000 }
  ]
};

const response = await fetch('/api/payments/bulk-payments', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(bulkPayments)
});
```

## 📞 Support

For issues or questions:
1. Check the logs for error details
2. Verify Stripe API key configuration
3. Ensure sufficient application revenue
4. Review webhook endpoint configuration

## 📄 License

MIT License - Use freely for commercial and non-commercial projects.