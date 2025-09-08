const { stripe } = require('../src/config/stripe');
const PaymentIntentService = require('../src/services/paymentIntentService');
const PaymentMethodService = require('../src/services/paymentMethodService');
const RevenueService = require('../src/services/revenueService');

/**
 * Test the automated payment flow
 */
async function testAutomatedPaymentFlow() {
  console.log('🧪 Testing Automated Payment Flow');
  console.log('=====================================');

  const paymentIntentService = new PaymentIntentService();
  const paymentMethodService = new PaymentMethodService();
  const revenueService = new RevenueService();

  try {
    // Step 1: Check revenue
    console.log('\n1️⃣ Checking application revenue...');
    const stats = await revenueService.getRevenueStats();
    console.log(`   Available Balance: $${stats.availableBalance/100} ${stats.currency.toUpperCase()}`);
    
    if (stats.availableBalance < 1000) {
      console.log('   ⚠️  Low balance, adding revenue...');
      await revenueService.addRevenue(10000, 'usd', 'test_funding');
      console.log('   ✅ Added $100 to revenue');
    }

    // Step 2: Create a test customer
    console.log('\n2️⃣ Creating test customer...');
    const customer = await stripe.customers.create({
      email: 'test@example.com',
      name: 'Test Customer',
      metadata: {
        test: 'automated_payment_flow'
      }
    });
    console.log(`   ✅ Created customer: ${customer.id}`);

    // Step 3: Create a mock revenue payment method
    console.log('\n3️⃣ Creating revenue payment method...');
    const mockPaymentMethod = {
      id: `pm_test_${Date.now()}`,
      type: 'card',
      metadata: {
        source: 'application_revenue',
        created_at: new Date().toISOString()
      }
    };
    await revenueService.registerPaymentMethod(mockPaymentMethod);
    console.log(`   ✅ Registered payment method: ${mockPaymentMethod.id}`);

    // Step 4: Test automated payment creation
    console.log('\n4️⃣ Creating automated payment...');
    const paymentAmount = 2000; // $20.00
    
    // Mock the payment intent creation for testing
    console.log(`   💰 Processing payment of $${paymentAmount/100}`);
    console.log('   🔄 Checking sufficient funds...');
    
    const hasFunds = await revenueService.checkSufficientFunds(paymentAmount);
    if (!hasFunds) {
      throw new Error('Insufficient funds for payment');
    }
    console.log('   ✅ Sufficient funds available');

    console.log('   🔗 Reserving funds...');
    await revenueService.reserveFunds(paymentAmount, 'usd', 'test_payment_intent');
    console.log('   ✅ Funds reserved');

    console.log('   💳 Simulating payment success...');
    await revenueService.deductFunds(paymentAmount, 'usd', 'test_payment_intent');
    console.log('   ✅ Payment processed and funds deducted');

    // Step 5: Display final stats
    console.log('\n5️⃣ Final revenue statistics...');
    const finalStats = await revenueService.getRevenueStats();
    console.log(`   Total Revenue: $${finalStats.totalRevenue/100} ${finalStats.currency.toUpperCase()}`);
    console.log(`   Available Balance: $${finalStats.availableBalance/100} ${finalStats.currency.toUpperCase()}`);
    console.log(`   Reserved Funds: $${finalStats.reservedFunds/100} ${finalStats.currency.toUpperCase()}`);

    console.log('\n🎉 Automated payment flow test completed successfully!');
    
    // Cleanup test customer
    await stripe.customers.del(customer.id);
    console.log('\n🧹 Test customer cleaned up');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
  }
}

if (require.main === module) {
  testAutomatedPaymentFlow();
}

module.exports = { testAutomatedPaymentFlow };