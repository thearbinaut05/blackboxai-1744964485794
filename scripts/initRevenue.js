const RevenueService = require('../src/services/revenueService');

/**
 * Initialize the application with some demo revenue
 */
async function initializeRevenue() {
  const revenueService = new RevenueService();
  
  try {
    // Add initial revenue for demonstration
    const initialAmount = process.env.INITIAL_REVENUE_AMOUNT || 1000000; // $10,000 in cents
    const currency = process.env.INITIAL_REVENUE_CURRENCY || 'usd';
    
    await revenueService.addRevenue(
      parseInt(initialAmount), 
      currency, 
      'initial_setup'
    );
    
    console.log(`✅ Initialized application with $${initialAmount/100} ${currency.toUpperCase()} revenue`);
    
    // Get and display revenue stats
    const stats = await revenueService.getRevenueStats();
    console.log('📊 Revenue Statistics:');
    console.log(`   Total Revenue: $${stats.totalRevenue/100} ${stats.currency.toUpperCase()}`);
    console.log(`   Available Balance: $${stats.availableBalance/100} ${stats.currency.toUpperCase()}`);
    console.log(`   Reserved Funds: $${stats.reservedFunds/100} ${stats.currency.toUpperCase()}`);
    
  } catch (error) {
    console.error('❌ Error initializing revenue:', error.message);
  }
}

if (require.main === module) {
  initializeRevenue();
}

module.exports = { initializeRevenue };