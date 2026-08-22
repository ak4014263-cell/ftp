-- Admin Users Table
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Subscription Plans Table
CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stripe_price_id VARCHAR(255) NOT NULL,
    features TEXT[] NOT NULL DEFAULT '{}',
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Feature Flags Table (for controlling which features require subscription)
CREATE TABLE IF NOT EXISTS feature_flags (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) UNIQUE NOT NULL,
    requires_subscription BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default subscription plans
INSERT INTO subscription_plans (plan_name, price, stripe_price_id, features, description)
VALUES 
    ('free', 0.00, 'price_free', ARRAY['5 applications per day', 'Basic job recommendations', 'Standard support'], 'Free tier with limited features'),
    ('premium', 29.00, 'price_1U5l89AM5V5laBzu61PnRBrM', ARRAY['Unlimited applications', 'AI-powered automation', 'Priority support', 'Advanced analytics'], 'Premium plan with full access')
ON CONFLICT (plan_name) DO NOTHING;

-- Insert default feature flags
INSERT INTO feature_flags (feature_name, requires_subscription, description)
VALUES 
    ('job_application', TRUE, 'Apply to jobs'),
    ('automated_application', TRUE, 'Automated job applications'),
    ('ai_cover_letter', TRUE, 'AI-generated cover letters'),
    ('unlimited_applications', TRUE, 'Unlimited job applications per day'),
    ('job_recommendations', FALSE, 'Basic job recommendations'),
    ('application_tracking', TRUE, 'Track application status'),
    ('email_alerts', TRUE, 'Email notifications for job matches'),
    ('priority_support', TRUE, 'Priority customer support'),
    ('analytics_dashboard', TRUE, 'Advanced analytics and insights')
ON CONFLICT (feature_name) DO NOTHING;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_feature_flags_name ON feature_flags(feature_name);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON subscription_plans(plan_name);

COMMENT ON TABLE admin_users IS 'Admin users for Swiply admin panel';
COMMENT ON TABLE subscription_plans IS 'Subscription plans configuration';
COMMENT ON TABLE feature_flags IS 'Feature access control flags';
