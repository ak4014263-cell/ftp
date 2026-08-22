# Stripe Payment Integration Setup

## Overview
Swiply now includes Stripe payment integration for subscription management.

## Features
- ✅ Stripe Checkout integration
- ✅ Subscription management
- ✅ Webhook handling for payment events
- ✅ Database-backed subscription tracking
- ✅ Beautiful payment UI

## Configuration

### 1. Stripe Keys (Already Configured)
Add your Stripe keys to `.env.production`:

```env
STRIPE_SECRET_KEY=sk_live_your_actual_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_key_here
STRIPE_PRICE_ID=price_your_actual_price_id_here
STRIPE_PRODUCT_ID=prod_your_actual_product_id_here
```

### 2. Database Setup

Run the SQL migration to create the subscriptions table:

```bash
# On VPS
docker exec -i swiply-postgres psql -U swiply -d swiply < create_subscriptions_table.sql
```

Or manually:

```sql
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    subscription_status VARCHAR(50) NOT NULL DEFAULT 'none',
    plan_type VARCHAR(50) DEFAULT 'premium',
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Deploy to VPS

```bash
# 1. Update environment variables
cd /opt/swiply
nano .env.production  # Add Stripe keys from .env.production.example

# 2. Pull latest code
git pull origin main

# 3. Rebuild services
docker-compose -f docker-compose.production.yml build payment gateway frontend

# 4. Restart services
docker-compose -f docker-compose.production.yml up -d

# 5. Check payment service is running
docker ps | grep payment
docker logs swiply-payment
```

### 4. Configure Stripe Webhooks (Optional but Recommended)

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://www.swiply.io/api/payment/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy the webhook signing secret
5. Update `.env.production`:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```
6. Restart payment service:
   ```bash
   docker restart swiply-payment
   ```

## Frontend Routes

The following payment routes are available:

- `/payment` - Main pricing/subscription page
- `/payment/success` - Payment success confirmation
- `/payment/cancel` - Payment cancellation page

## API Endpoints

### Payment Service (Port 8011)
- `POST /create-checkout-session` - Create Stripe checkout session
- `GET /subscription/{user_id}` - Get subscription status
- `POST /cancel-subscription/{user_id}` - Cancel subscription
- `POST /webhook` - Handle Stripe webhooks
- `GET /health` - Health check

### Via API Gateway
All endpoints are accessible via `/api/payment/...`

Example:
```bash
# Create checkout session
curl -X POST http://www.swiply.io/api/payment/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "email": "user@example.com",
    "plan": "premium"
  }'

# Get subscription status
curl http://www.swiply.io/api/payment/subscription/user123
```

## Testing

### Test Subscription Flow

1. Navigate to `http://www.swiply.io/payment`
2. Click "Upgrade Now" on Premium plan
3. Complete checkout with Stripe test card (if using test mode)
4. Verify redirect to success page
5. Check database for subscription record:
   ```sql
   SELECT * FROM subscriptions WHERE user_id = 'your_user_id';
   ```

### Test Webhook Locally (Optional)

Use Stripe CLI to forward webhooks to local environment:

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward webhooks
stripe listen --forward-to localhost:8011/webhook
```

## Subscription Status Values

- `none` - No subscription
- `active` - Active subscription
- `past_due` - Payment failed
- `canceled` - Subscription canceled
- `trialing` - In trial period (if configured)

## Pricing

Current pricing configuration:
- **Free Plan**: $0/month - 5 applications per day
- **Premium Plan**: $29/month - Unlimited applications

To update pricing:
1. Create new price in Stripe Dashboard
2. Update `STRIPE_PRICE_ID` in `.env.production`
3. Restart payment service

## Security Notes

- ✅ Stripe keys are stored in environment variables (not in code)
- ✅ Payment processing happens on Stripe's servers (PCI compliant)
- ✅ Webhook signatures are verified (when `STRIPE_WEBHOOK_SECRET` is set)
- ✅ All communication uses HTTPS in production

## Troubleshooting

### Payment service not starting
```bash
docker logs swiply-payment
```

### Checkout session creation fails
- Verify Stripe secret key is correct
- Check payment service logs
- Ensure price ID exists in Stripe Dashboard

### Webhooks not received
- Verify webhook endpoint is configured in Stripe
- Check webhook signing secret
- Test with Stripe CLI webhook forwarding

## Support

For Stripe-related issues:
- Stripe Dashboard: https://dashboard.stripe.com
- Stripe Docs: https://stripe.com/docs
- Stripe Support: https://support.stripe.com

For Swiply integration issues:
- Check service logs: `docker logs swiply-payment`
- Review API Gateway logs: `docker logs swiply-gateway`
- Contact: support@swiply.io
