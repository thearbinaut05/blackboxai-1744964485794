const express = require('express');
const { stripe, webhookSecret } = require('../config/stripe');
const PaymentIntentService = require('../services/paymentIntentService');
const RevenueService = require('../services/revenueService');

const router = express.Router();
const paymentIntentService = new PaymentIntentService();
const revenueService = new RevenueService();

/**
 * Create automated payment with revenue funding
 */
router.post('/create-automated-payment', async (req, res) => {
  try {
    const { customerId, amount, currency = 'usd', autoConfirm = true } = req.body;

    if (!customerId || !amount) {
      return res.status(400).json({ 
        error: 'customerId and amount are required' 
      });
    }

    const payment = await paymentIntentService.processAutomatedPayment({
      customerId,
      amount,
      currency,
      autoConfirm
    });

    res.json({
      success: true,
      payment: {
        id: payment.id,
        amount: payment.amount,
        currency: payment.currency,
        status: payment.status,
        customer: payment.customer
      }
    });
  } catch (error) {
    console.error('Error creating automated payment:', error);
    res.status(500).json({ 
      error: error.message 
    });
  }
});

/**
 * Process bulk payments
 */
router.post('/bulk-payments', async (req, res) => {
  try {
    const { payments } = req.body;

    if (!payments || !Array.isArray(payments)) {
      return res.status(400).json({ 
        error: 'payments array is required' 
      });
    }

    const results = await paymentIntentService.processBulkPayments(payments);

    res.json({
      success: true,
      results,
      summary: {
        total: results.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length
      }
    });
  } catch (error) {
    console.error('Error processing bulk payments:', error);
    res.status(500).json({ 
      error: error.message 
    });
  }
});

/**
 * Add revenue to the application
 */
router.post('/add-revenue', async (req, res) => {
  try {
    const { amount, currency = 'usd', source = 'application' } = req.body;

    if (!amount || amount <= 0) {
      return res.status(400).json({ 
        error: 'Valid amount is required' 
      });
    }

    const revenueData = await revenueService.addRevenue(amount, currency, source);

    res.json({
      success: true,
      revenue: {
        totalRevenue: revenueData.totalRevenue,
        availableBalance: revenueData.availableBalance,
        currency: revenueData.currency
      }
    });
  } catch (error) {
    console.error('Error adding revenue:', error);
    res.status(500).json({ 
      error: error.message 
    });
  }
});

/**
 * Get revenue statistics
 */
router.get('/revenue-stats', async (req, res) => {
  try {
    const stats = await revenueService.getRevenueStats();

    res.json({
      success: true,
      stats
    });
  } catch (error) {
    console.error('Error getting revenue stats:', error);
    res.status(500).json({ 
      error: error.message 
    });
  }
});

/**
 * Manually attach payment method to payment intent
 */
router.post('/attach-payment-method', async (req, res) => {
  try {
    const { paymentIntentId, customerId } = req.body;

    if (!paymentIntentId || !customerId) {
      return res.status(400).json({ 
        error: 'paymentIntentId and customerId are required' 
      });
    }

    const updatedPaymentIntent = await paymentIntentService.attachRevenuePaymentMethod(
      paymentIntentId, 
      customerId
    );

    res.json({
      success: true,
      paymentIntent: {
        id: updatedPaymentIntent.id,
        payment_method: updatedPaymentIntent.payment_method,
        status: updatedPaymentIntent.status
      }
    });
  } catch (error) {
    console.error('Error attaching payment method:', error);
    res.status(500).json({ 
      error: error.message 
    });
  }
});

/**
 * Confirm payment intent with revenue funding
 */
router.post('/confirm-payment-intent', async (req, res) => {
  try {
    const { paymentIntentId } = req.body;

    if (!paymentIntentId) {
      return res.status(400).json({ 
        error: 'paymentIntentId is required' 
      });
    }

    const confirmedPayment = await paymentIntentService.confirmPaymentIntentWithRevenue(paymentIntentId);

    res.json({
      success: true,
      payment: {
        id: confirmedPayment.id,
        status: confirmedPayment.status,
        amount: confirmedPayment.amount,
        currency: confirmedPayment.currency
      }
    });
  } catch (error) {
    console.error('Error confirming payment intent:', error);
    res.status(500).json({ 
      error: error.message 
    });
  }
});

/**
 * Stripe webhook handler for automated processing
 */
router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    console.error('Webhook signature verification failed.', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  try {
    switch (event.type) {
      case 'payment_intent.succeeded':
        console.log('Payment succeeded:', event.data.object.id);
        // Additional processing can be added here
        break;
        
      case 'payment_intent.payment_failed':
        console.log('Payment failed:', event.data.object.id);
        // Release reserved funds
        await revenueService.releaseReservedFunds(event.data.object.id);
        break;
        
      case 'payment_method.attached':
        console.log('Payment method attached:', event.data.object.id);
        break;
        
      default:
        console.log(`Unhandled event type ${event.type}`);
    }

    res.json({ received: true });
  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).json({ error: 'Webhook processing failed' });
  }
});

module.exports = router;