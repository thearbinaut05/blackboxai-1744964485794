require('dotenv').config();
const stripe = require('stripe');

const stripeClient = stripe(process.env.STRIPE_SECRET_KEY);

module.exports = {
  stripe: stripeClient,
  webhookSecret: process.env.STRIPE_WEBHOOK_SECRET,
  applicationAccountId: process.env.STRIPE_APPLICATION_ACCOUNT_ID
};