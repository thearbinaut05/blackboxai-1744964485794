const fs = require('fs').promises;
const path = require('path');

class RevenueService {
  constructor() {
    this.revenueDataFile = path.join(process.cwd(), 'data', 'revenue.json');
    this.paymentMethodsFile = path.join(process.cwd(), 'data', 'revenue_payment_methods.json');
    this.initialized = false;
  }

  /**
   * Ensure initialization is completed
   */
  async ensureInitialized() {
    if (!this.initialized) {
      await this.initializeDataFiles();
      this.initialized = true;
    }
  }

  /**
   * Initialize data files if they don't exist
   */
  async initializeDataFiles() {
    try {
      await fs.mkdir(path.dirname(this.revenueDataFile), { recursive: true });
      
      // Initialize revenue data file
      try {
        await fs.access(this.revenueDataFile);
      } catch {
        const initialRevenueData = {
          totalRevenue: 0,
          availableBalance: 0,
          reservedFunds: 0,
          currency: 'usd',
          lastUpdated: new Date().toISOString(),
          transactions: []
        };
        await fs.writeFile(this.revenueDataFile, JSON.stringify(initialRevenueData, null, 2));
      }

      // Initialize payment methods file
      try {
        await fs.access(this.paymentMethodsFile);
      } catch {
        const initialPaymentMethods = {
          paymentMethods: [],
          lastUpdated: new Date().toISOString()
        };
        await fs.writeFile(this.paymentMethodsFile, JSON.stringify(initialPaymentMethods, null, 2));
      }
    } catch (error) {
      console.error('Error initializing data files:', error);
    }
  }

  /**
   * Get current revenue data
   */
  async getRevenueData() {
    await this.ensureInitialized();
    try {
      const data = await fs.readFile(this.revenueDataFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error('Error reading revenue data:', error);
      return null;
    }
  }

  /**
   * Update revenue data
   */
  async updateRevenueData(data) {
    try {
      data.lastUpdated = new Date().toISOString();
      await fs.writeFile(this.revenueDataFile, JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error updating revenue data:', error);
      throw error;
    }
  }

  /**
   * Add revenue to the application
   */
  async addRevenue(amount, currency = 'usd', source = 'application') {
    try {
      await this.ensureInitialized();
      const revenueData = await this.getRevenueData();
      
      if (!revenueData) {
        throw new Error('Failed to initialize revenue data');
      }
      
      revenueData.totalRevenue += amount;
      revenueData.availableBalance += amount;
      revenueData.currency = currency;
      
      revenueData.transactions.push({
        type: 'revenue_add',
        amount,
        currency,
        source,
        timestamp: new Date().toISOString()
      });

      await this.updateRevenueData(revenueData);
      
      console.log(`Added ${amount} ${currency} to revenue. New balance: ${revenueData.availableBalance}`);
      return revenueData;
    } catch (error) {
      console.error('Error adding revenue:', error);
      throw error;
    }
  }

  /**
   * Check if there are sufficient funds for a payment
   */
  async checkSufficientFunds(amount, currency = 'usd') {
    try {
      const revenueData = await this.getRevenueData();
      return revenueData.availableBalance >= amount && revenueData.currency === currency;
    } catch (error) {
      console.error('Error checking sufficient funds:', error);
      return false;
    }
  }

  /**
   * Reserve funds for a payment
   */
  async reserveFunds(amount, currency = 'usd', paymentIntentId = null) {
    try {
      const revenueData = await this.getRevenueData();
      
      if (revenueData.availableBalance < amount) {
        throw new Error('Insufficient funds to reserve');
      }

      revenueData.availableBalance -= amount;
      revenueData.reservedFunds += amount;
      
      revenueData.transactions.push({
        type: 'funds_reserved',
        amount,
        currency,
        paymentIntentId,
        timestamp: new Date().toISOString()
      });

      await this.updateRevenueData(revenueData);
      
      console.log(`Reserved ${amount} ${currency}. Available balance: ${revenueData.availableBalance}`);
      return revenueData;
    } catch (error) {
      console.error('Error reserving funds:', error);
      throw error;
    }
  }

  /**
   * Deduct funds after successful payment
   */
  async deductFunds(amount, currency = 'usd', paymentIntentId = null) {
    try {
      const revenueData = await this.getRevenueData();
      
      revenueData.reservedFunds -= amount;
      
      revenueData.transactions.push({
        type: 'funds_deducted',
        amount,
        currency,
        paymentIntentId,
        timestamp: new Date().toISOString()
      });

      await this.updateRevenueData(revenueData);
      
      console.log(`Deducted ${amount} ${currency}. Reserved funds: ${revenueData.reservedFunds}`);
      return revenueData;
    } catch (error) {
      console.error('Error deducting funds:', error);
      throw error;
    }
  }

  /**
   * Release reserved funds if payment fails
   */
  async releaseReservedFunds(paymentIntentId) {
    try {
      const revenueData = await this.getRevenueData();
      
      // Find the reservation transaction
      const reservationTransaction = revenueData.transactions
        .reverse()
        .find(t => t.type === 'funds_reserved' && t.paymentIntentId === paymentIntentId);
      
      if (reservationTransaction) {
        const amount = reservationTransaction.amount;
        revenueData.availableBalance += amount;
        revenueData.reservedFunds -= amount;
        
        revenueData.transactions.push({
          type: 'funds_released',
          amount,
          currency: reservationTransaction.currency,
          paymentIntentId,
          timestamp: new Date().toISOString()
        });

        await this.updateRevenueData(revenueData);
        console.log(`Released ${amount} reserved funds for payment intent ${paymentIntentId}`);
      }
      
      return revenueData;
    } catch (error) {
      console.error('Error releasing reserved funds:', error);
      throw error;
    }
  }

  /**
   * Register a payment method as a revenue source
   */
  async registerPaymentMethod(paymentMethod) {
    try {
      const data = await fs.readFile(this.paymentMethodsFile, 'utf8');
      const paymentMethodsData = JSON.parse(data);
      
      paymentMethodsData.paymentMethods.push({
        id: paymentMethod.id,
        type: paymentMethod.type,
        availableBalance: 10000000, // Default high balance for demo
        currency: 'usd',
        metadata: paymentMethod.metadata,
        created: new Date().toISOString()
      });
      
      paymentMethodsData.lastUpdated = new Date().toISOString();
      
      await fs.writeFile(this.paymentMethodsFile, JSON.stringify(paymentMethodsData, null, 2));
      
      console.log(`Registered payment method ${paymentMethod.id} as revenue source`);
    } catch (error) {
      console.error('Error registering payment method:', error);
      throw error;
    }
  }

  /**
   * Get available payment methods from revenue sources
   */
  async getAvailablePaymentMethods() {
    try {
      const data = await fs.readFile(this.paymentMethodsFile, 'utf8');
      const paymentMethodsData = JSON.parse(data);
      
      return paymentMethodsData.paymentMethods.filter(pm => pm.availableBalance > 0);
    } catch (error) {
      console.error('Error getting available payment methods:', error);
      return [];
    }
  }

  /**
   * Get revenue statistics
   */
  async getRevenueStats() {
    try {
      const revenueData = await this.getRevenueData();
      const paymentMethodsData = await fs.readFile(this.paymentMethodsFile, 'utf8');
      const paymentMethods = JSON.parse(paymentMethodsData);
      
      return {
        totalRevenue: revenueData.totalRevenue,
        availableBalance: revenueData.availableBalance,
        reservedFunds: revenueData.reservedFunds,
        currency: revenueData.currency,
        totalPaymentMethods: paymentMethods.paymentMethods.length,
        lastUpdated: revenueData.lastUpdated
      };
    } catch (error) {
      console.error('Error getting revenue stats:', error);
      throw error;
    }
  }
}

module.exports = RevenueService;