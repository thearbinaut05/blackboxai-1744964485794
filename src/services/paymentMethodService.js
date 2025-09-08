const { stripe } = require('../config/stripe');
const RevenueService = require('./revenueService');

class PaymentMethodService {
  constructor() {
    this.revenueService = new RevenueService();
  }

  /**
   * Automatically attach a payment method to a customer
   * Uses application revenue to fund the payment method
   */
  async attachPaymentMethodToCustomer(customerId, paymentMethodType = 'card') {
    try {
      // Get available revenue payment methods
      const availablePaymentMethods = await this.revenueService.getAvailablePaymentMethods();
      
      if (availablePaymentMethods.length === 0) {
        throw new Error('No revenue payment methods available');
      }

      // Select the best payment method from revenue sources
      const selectedPaymentMethod = this.selectOptimalPaymentMethod(availablePaymentMethods);

      // Attach the revenue-funded payment method to the customer
      const attachedPaymentMethod = await stripe.paymentMethods.attach(
        selectedPaymentMethod.id,
        { customer: customerId }
      );

      // Set as default payment method for the customer
      await stripe.customers.update(customerId, {
        invoice_settings: {
          default_payment_method: attachedPaymentMethod.id,
        },
      });

      console.log(`Payment method ${attachedPaymentMethod.id} attached to customer ${customerId}`);
      
      return attachedPaymentMethod;
    } catch (error) {
      console.error('Error attaching payment method:', error);
      throw error;
    }
  }

  /**
   * Select the optimal payment method from available revenue sources
   */
  selectOptimalPaymentMethod(paymentMethods) {
    // Sort by available balance and select the one with highest balance
    return paymentMethods.sort((a, b) => b.availableBalance - a.availableBalance)[0];
  }

  /**
   * Create a payment method from application revenue
   */
  async createRevenuePaymentMethod(paymentMethodData) {
    try {
      const paymentMethod = await stripe.paymentMethods.create({
        type: 'card',
        card: paymentMethodData.card,
        metadata: {
          source: 'application_revenue',
          created_at: new Date().toISOString()
        }
      });

      // Register this payment method as a revenue source
      await this.revenueService.registerPaymentMethod(paymentMethod);

      return paymentMethod;
    } catch (error) {
      console.error('Error creating revenue payment method:', error);
      throw error;
    }
  }

  /**
   * List all revenue-sourced payment methods
   */
  async listRevenuePaymentMethods() {
    try {
      return await this.revenueService.getAvailablePaymentMethods();
    } catch (error) {
      console.error('Error listing revenue payment methods:', error);
      throw error;
    }
  }
}

module.exports = PaymentMethodService;