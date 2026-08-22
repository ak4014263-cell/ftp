# Swiply Admin Panel Guide

## Overview
Complete admin panel system for managing Stripe payments, subscription pricing, feature access control, and user subscriptions.

## Features
✅ Admin authentication with JWT
✅ Dashboard with statistics
✅ Subscription management (view, cancel)
✅ Dynamic pricing control
✅ Feature gating system
✅ Stripe integration management
✅ User access control based on subscription status

## Default Admin Credentials
```
Username: admin@swiply.io
Password: Admin@123!Swiply
```
**⚠️ CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN!**

## Setup Instructions

### 1. Create Database Tables

```bash
# On VPS
docker exec -i swiply-postgres psql -U swiply -d swiply < create_subscriptions_table.sql
docker exec -i swiply-postgres psql -U swiply -d swiply < create_admin_tables.sql
```

### 2. Initialize Admin User

```bash
# Call the init endpoint (one-time only)
curl -X POST http://www.swiply.io/api/admin/init-admin
```

### 3. Update Environment Variables

Add to `.env.production`:
```env
# Admin Configuration
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters-long
ADMIN_USERNAME=admin@swiply.io

# Stripe Keys (get from Stripe Dashboard)
STRIPE_SECRET_KEY=sk_live_your_actual_key_here
STRIPE_PRICE_ID=price_your_actual_price_id_here
```

### 4. Deploy Services

```bash
cd /opt/swiply

# Build new services
docker-compose -f docker-compose.production.yml build admin payment

# Restart all services
docker-compose -f docker-compose.production.yml up -d

# Check logs
docker logs swiply-admin
docker logs swiply-payment
```

## Admin Panel Access

### URL
```
http://www.swiply.io/admin/login
```

### Routes
- `/admin/login` - Admin login
- `/admin/dashboard` - Main dashboard
  - Overview tab - Statistics and recent activity
  - Subscriptions tab - Manage user subscriptions
  - Plans & Pricing tab - Configure subscription plans
  - Features tab - Control feature access

## Feature Gating System

### How It Works
1. **Feature Flags** - Define which features require subscription
2. **Middleware** - Checks user subscription before allowing access
3. **User Experience** - Blocked features show upgrade prompt

### Protected Features
By default, these features require active subscription:
- ✓ Job applications (automated)
- ✓ AI-powered cover letters
- ✓ Unlimited applications per day
- ✓ Application tracking
- ✓ Email alerts
- ✓ Priority support
- ✓ Analytics dashboard

### Free Features
- Basic job recommendations
- Limited applications (5 per day)

### Usage in Code

#### Backend (Python/FastAPI)
```python
from shared.subscription_middleware import check_feature_access, check_daily_limit

@app.post("/apply-job")
async def apply_job(user_id: str, job_id: str):
    # Check if user has access to this feature
    access = await check_feature_access(user_id, "job_application")
    
    if not access['has_access']:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "subscription_required",
                "message": access['message']
            }
        )
    
    # Check daily limits for free users
    limit_check = await check_daily_limit(user_id, "applications")
    
    if not limit_check['within_limit']:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "daily_limit_exceeded",
                "message": limit_check['message']
            }
        )
    
    # Proceed with job application
    ...
```

#### Frontend (React/TypeScript)
```typescript
import { paymentService } from '../services/paymentService';

// Check subscription before showing feature
const checkAccess = async () => {
  try {
    const status = await paymentService.getSubscriptionStatus(userId);
    
    if (status.status !== 'active') {
      // Show upgrade prompt
      navigate('/payment');
      return false;
    }
    
    return true;
  } catch (error) {
    return false;
  }
};

// Usage in component
const handleApplyJob = async () => {
  const hasAccess = await checkAccess();
  if (!hasAccess) return;
  
  // Proceed with job application
  ...
};
```

## Managing Subscription Plans

### Adding a New Plan
1. Go to **Plans & Pricing** tab
2. Click **Add Plan**
3. Fill in details:
   - Plan name (e.g., "pro", "enterprise")
   - Price in USD
   - Stripe Price ID (get from Stripe Dashboard)
   - Features list
   - Description
4. Click **Create Plan**

### Editing Existing Plans
1. Click **Edit** button on any plan card
2. Modify details
3. Click **Update Plan**

### Connecting to Stripe
- Plans are linked via Stripe Price ID
- Create prices in Stripe Dashboard first
- Then reference them in admin panel

## Managing Features

### Toggle Feature Access
1. Go to **Features** tab
2. View all available features
3. Click **Lock** to require subscription
4. Click **Unlock** to make free

### Adding New Features
To add new features to the system:

1. Add to database:
```sql
INSERT INTO feature_flags (feature_name, requires_subscription, description)
VALUES ('new_feature', TRUE, 'Description of feature');
```

2. Implement in code:
```python
access = await check_feature_access(user_id, "new_feature")
```

## Managing Subscriptions

### View All Subscriptions
- See all active and inactive subscriptions
- Filter by email or user ID
- View subscription status and expiry

### Cancel Subscription
1. Find user subscription
2. Click **Cancel** button
3. Confirm cancellation
4. Subscription will be canceled in Stripe and database

## API Endpoints

### Admin Service (Port 8014)
```
POST /login - Admin login
GET  /dashboard/stats - Dashboard statistics
GET  /subscriptions - List all subscriptions
GET  /plans - List subscription plans
POST /plans - Create/update plan
GET  /features - List feature flags
POST /features - Update feature flag
GET  /stripe/prices - Get Stripe prices
GET  /stripe/products - Get Stripe products
POST /subscription/{user_id}/cancel - Cancel subscription
POST /init-admin - Initialize admin user
```

### Via API Gateway
All endpoints accessible via `/api/admin/...`

## Security Best Practices

1. **Change Default Password**
   - Immediately after first login
   - Use strong password (min 12 characters)

2. **Secure JWT Secret**
   - Use strong random string (32+ characters)
   - Never commit to git

3. **HTTPS Only**
   - Always use HTTPS in production
   - Admin panel should never be accessed over HTTP

4. **Access Logging**
   - All admin actions are logged
   - Monitor logs regularly

5. **IP Whitelist** (Optional)
   - Configure nginx to restrict admin access to specific IPs

## Troubleshooting

### Cannot Login to Admin Panel
```bash
# Check if admin service is running
docker logs swiply-admin

# Reinitialize admin user
curl -X POST http://localhost/api/admin/init-admin

# Check database
docker exec -it swiply-postgres psql -U swiply -d swiply
SELECT * FROM admin_users;
```

### Feature Access Not Working
```bash
# Check feature flags
docker exec -it swiply-postgres psql -U swiply -d swiply
SELECT * FROM feature_flags;

# Check subscription status
SELECT * FROM subscriptions WHERE user_id = 'user123';
```

### Stripe Integration Issues
```bash
# Verify Stripe keys
docker exec swiply-payment env | grep STRIPE

# Check payment service logs
docker logs swiply-payment

# Test Stripe connection
curl http://localhost/api/admin/stripe/prices
```

## Database Schema

### admin_users
- id (serial)
- username (unique)
- password_hash
- created_at
- last_login

### subscription_plans
- id (serial)
- plan_name (unique)
- price (decimal)
- stripe_price_id
- features (text[])
- description
- created_at, updated_at

### feature_flags
- id (serial)
- feature_name (unique)
- requires_subscription (boolean)
- description
- created_at, updated_at

### subscriptions (already exists)
- id (serial)
- user_id (unique)
- stripe_subscription_id
- subscription_status
- plan_type
- current_period_start/end
- created_at, updated_at

## Future Enhancements

- [ ] Multi-admin user support with roles
- [ ] Activity audit log
- [ ] Subscription analytics and reports
- [ ] Automated email notifications
- [ ] Webhook status monitoring
- [ ] Revenue forecasting
- [ ] Custom discount codes
- [ ] Trial period management

## Support

For issues or questions:
- Check logs: `docker logs swiply-admin`
- Review this documentation
- Contact: support@swiply.io
