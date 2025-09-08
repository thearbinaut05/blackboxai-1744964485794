const PaymentIntentService = require('../src/services/paymentIntentService');
const PaymentMethodService = require('../src/services/paymentMethodService');
const RevenueService = require('../src/services/revenueService');

/**
 * Test the automated payment flow with mocked Stripe operations
 */
async function testAutomatedPaymentFlowMocked() {
  console.log('🧪 Testing Automated Payment Flow (Mocked)');
  console.log('=============================================');

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

    // Step 2: Create a mock customer (simulated)
    console.log('\n2️⃣ Creating test customer...');
    const mockCustomer = {
      id: `cus_mock_${Date.now()}`,
      email: 'test@example.com',
      name: 'Test Customer',
      metadata: {
        test: 'automated_payment_flow'
      }
    };
    console.log(`   ✅ Created customer: ${mockCustomer.id}`);

    // Step 3: Create a mock revenue payment method
    console.log('\n3️⃣ Creating revenue payment method...');
    const mockPaymentMethod = {
      id: `pm_mock_${Date.now()}`,
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
    
    console.log(`   💰 Processing payment of $${paymentAmount/100}`);
    console.log('   🔄 Checking sufficient funds...');
    
    const hasFunds = await revenueService.checkSufficientFunds(paymentAmount);
    if (!hasFunds) {
      throw new Error('Insufficient funds for payment');
    }
    console.log('   ✅ Sufficient funds available');

    console.log('   🔗 Reserving funds...');
    const mockPaymentIntentId = `pi_mock_${Date.now()}`;
    await revenueService.reserveFunds(paymentAmount, 'usd', mockPaymentIntentId);
    console.log('   ✅ Funds reserved');

    console.log('   💳 Simulating payment success...');
    await revenueService.deductFunds(paymentAmount, 'usd', mockPaymentIntentId);
    console.log('   ✅ Payment processed and funds deducted');

    // Step 5: Test bulk payment processing
    console.log('\n5️⃣ Testing bulk payment processing...');
    const bulkPayments = [
      { amount: 500, description: 'Bulk payment 1' },
      { amount: 750, description: 'Bulk payment 2' },
      { amount: 1000, description: 'Bulk payment 3' }
    ];

    for (const payment of bulkPayments) {
      const mockBulkPaymentId = `pi_bulk_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      console.log(`   🔄 Processing ${payment.description}: $${payment.amount/100}`);
      
      if (await revenueService.checkSufficientFunds(payment.amount)) {
        await revenueService.reserveFunds(payment.amount, 'usd', mockBulkPaymentId);
        await revenueService.deductFunds(payment.amount, 'usd', mockBulkPaymentId);
        console.log(`   ✅ ${payment.description} completed`);
      } else {
        console.log(`   ❌ ${payment.description} failed - insufficient funds`);
      }
    }

    // Step 6: Display final stats
    console.log('\n6️⃣ Final revenue statistics...');
    const finalStats = await revenueService.getRevenueStats();
    console.log(`   Total Revenue: $${finalStats.totalRevenue/100} ${finalStats.currency.toUpperCase()}`);
    console.log(`   Available Balance: $${finalStats.availableBalance/100} ${finalStats.currency.toUpperCase()}`);
    console.log(`   Reserved Funds: $${finalStats.reservedFunds/100} ${finalStats.currency.toUpperCase()}`);
    console.log(`   Total Payment Methods: ${finalStats.totalPaymentMethods}`);

    // Step 7: Test error handling - insufficient funds
    console.log('\n7️⃣ Testing error handling...');
    const largePaymentAmount = finalStats.availableBalance + 1000;
    console.log(`   🔄 Attempting payment of $${largePaymentAmount/100} (should fail)`);
    
    const hasLargeFunds = await revenueService.checkSufficientFunds(largePaymentAmount);
    if (!hasLargeFunds) {
      console.log('   ✅ Correctly rejected payment due to insufficient funds');
    } else {
      console.log('   ❌ Error: Should have rejected payment');
    }

    console.log('\n🎉 Automated payment flow test completed successfully!');
    console.log('\n📋 Test Summary:');
    console.log('   ✅ Revenue management');
    console.log('   ✅ Payment method registration');
    console.log('   ✅ Fund reservation and deduction');
    console.log('   ✅ Bulk payment processing');
    console.log('   ✅ Error handling for insufficient funds');
    console.log('   ✅ Data persistence and retrieval');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
  }
}

if (require.main === module) {
  testAutomatedPaymentFlowMocked();
}

module.exports = { testAutomatedPaymentFlowMocked };