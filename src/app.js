require('dotenv').config();
const express = require('express');
const cors = require('cors');
const paymentRoutes = require('./routes/payments');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use('/webhook', express.raw({ type: 'application/json' })); // Raw body for webhooks
app.use(express.json()); // JSON body parser for other routes

// Routes
app.use('/api/payments', paymentRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'stripe-payment-automation'
  });
});

// Root endpoint with API documentation
app.get('/', (req, res) => {
  res.json({
    service: 'Stripe Payment Automation System',
    version: '1.0.0',
    description: 'Automated payment method attachment for Stripe with revenue funding',
    endpoints: {
      'POST /api/payments/create-automated-payment': 'Create and process automated payment',
      'POST /api/payments/bulk-payments': 'Process multiple payments at once',
      'POST /api/payments/add-revenue': 'Add revenue to application funds',
      'GET /api/payments/revenue-stats': 'Get revenue statistics',
      'POST /api/payments/attach-payment-method': 'Manually attach payment method',
      'POST /api/payments/confirm-payment-intent': 'Confirm payment with revenue funding',
      'POST /api/payments/webhook': 'Stripe webhook handler',
      'GET /health': 'Health check'
    },
    features: [
      'Automatic payment method attachment',
      'Revenue-funded payments',
      'Bulk payment processing',
      'Real-time webhook processing',
      'Revenue management',
      'Payment tracking'
    ]
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ 
    error: 'Endpoint not found',
    path: req.path,
    method: req.method
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Stripe Payment Automation Server running on port ${PORT}`);
  console.log(`📝 API Documentation available at http://localhost:${PORT}`);
  console.log(`💚 Health check available at http://localhost:${PORT}/health`);
});

module.exports = app;