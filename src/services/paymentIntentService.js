const { stripe } = require('../config/stripe');
const PaymentMethodService = require('./paymentMethodService');
const RevenueService = require('./revenueService');

class PaymentIntentService {
  constructor() {
    this.paymentMethodService = new PaymentMethodService();
    this.revenueService = new RevenueService();
  }

  /**
   * Create a payment intent with automatic payment method attachment
   * All payments are funded from application revenue
   */
  async createPaymentIntentWithAutoAttachment(params) {
    const { customerId, amount, currency = 'usd', automaticPaymentMethods = true } = params;

    try {
      // Check if application has sufficient revenue
      const hasRevenue = await this.revenueService.checkSufficientFunds(amount, currency);
      if (!hasRevenue) {
        throw new Error('Insufficient application revenue for this payment');
      }

      // Create payment intent
      const paymentIntent = await stripe.paymentIntents.create({
        customer: customerId,
        amount: amount,
        currency: currency,
        automatic_payment_methods: {
          enabled: automaticPaymentMethods,
        },
        metadata: {
          funded_by: 'application_revenue',
          created_at: new Date().toISOString()
        }
      });

      // Automatically attach payment method from revenue
      await this.attachRevenuePaymentMethod(paymentIntent.id, customerId);

      console.log(`Payment intent ${paymentIntent.id} created and payment method attached`);
      
      return paymentIntent;
    } catch (error) {
      console.error('Error creating payment intent with auto attachment:', error);
      throw error;
    }
  }

  /**
   * Attach a revenue-sourced payment method to an existing payment intent
   */
  async attachRevenuePaymentMethod(paymentIntentId, customerId) {
    try {
      // Get or create a revenue payment method for the customer
      const paymentMethod = await this.paymentMethodService.attachPaymentMethodToCustomer(customerId);

      // Update payment intent with the attached payment method
      const updatedPaymentIntent = await stripe.paymentIntents.update(paymentIntentId, {
        payment_method: paymentMethod.id
      });

      console.log(`Revenue payment method ${paymentMethod.id} attached to payment intent ${paymentIntentId}`);
      
      return updatedPaymentIntent;
    } catch (error) {
      console.error('Error attaching revenue payment method:', error);
      throw error;
    }
  }

  /**
   * Confirm payment intent automatically using revenue funds
   */
  async confirmPaymentIntentWithRevenue(paymentIntentId) {
    try {
      const paymentIntent = await stripe.paymentIntents.retrieve(paymentIntentId);
      
      // Verify this payment is funded by application revenue
      if (paymentIntent.metadata.funded_by !== 'application_revenue') {
        throw new Error('Payment intent is not funded by application revenue');
      }

      // Reserve funds from revenue
      await this.revenueService.reserveFunds(paymentIntent.amount, paymentIntent.currency);

      // Confirm the payment intent
      const confirmedPaymentIntent = await stripe.paymentIntents.confirm(paymentIntentId);

      // If successful, deduct from revenue
      if (confirmedPaymentIntent.status === 'succeeded') {
        await this.revenueService.deductFunds(paymentIntent.amount, paymentIntent.currency);
        console.log(`Payment confirmed and ${paymentIntent.amount} ${paymentIntent.currency} deducted from revenue`);
      }

      return confirmedPaymentIntent;
    } catch (error) {
      console.error('Error confirming payment intent with revenue:', error);
      // Release reserved funds on error
      await this.revenueService.releaseReservedFunds(paymentIntentId);
      throw error;
    }
  }

  /**
   * Process automated payment workflow
   */
  async processAutomatedPayment(params) {
    const { customerId, amount, currency = 'usd', autoConfirm = true } = params;

    try {
      // Step 1: Create payment intent with auto-attached payment method
      const paymentIntent = await this.createPaymentIntentWithAutoAttachment({
        customerId,
        amount,
        currency
      });

      // Step 2: Auto-confirm if requested
      if (autoConfirm) {
        const confirmedPayment = await this.confirmPaymentIntentWithRevenue(paymentIntent.id);
        return confirmedPayment;
      }

      return paymentIntent;
    } catch (error) {
      console.error('Error processing automated payment:', error);
      throw error;
    }
  }

  /**
   * Bulk process multiple payments
   */
  async processBulkPayments(payments) {
    const results = [];
    
    for (const payment of payments) {
      try {
        const result = await this.processAutomatedPayment(payment);
        results.push({ success: true, payment: result });
      } catch (error) {
        results.push({ success: false, error: error.message, payment });
      }
    }

    return results;
  }
}

module.exports = PaymentIntentService;