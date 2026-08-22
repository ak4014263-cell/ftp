"""
Admin Service - Manage subscriptions, pricing, and features
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import os
import asyncpg
import bcrypt
import jwt
from datetime import datetime, timedelta
import stripe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Admin Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@swiply.io")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")  # Will be generated

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "swiply")
DB_PASSWORD = os.getenv("DB_PASSWORD", "swiply_secure_pwd_2026!")
DB_NAME = os.getenv("DB_NAME", "swiply")

security = HTTPBearer()


# Models
class AdminLogin(BaseModel):
    username: str
    password: str


class SubscriptionPlanUpdate(BaseModel):
    plan_name: str
    price: float
    stripe_price_id: str
    features: List[str]
    description: Optional[str] = None


class FeatureToggle(BaseModel):
    feature_name: str
    requires_subscription: bool
    description: Optional[str] = None


async def get_db_connection():
    """Get database connection"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "admin"}


@app.post("/login")
async def admin_login(login: AdminLogin):
    """Admin login endpoint"""
    try:
        conn = await get_db_connection()
        
        # Get admin user from database
        admin = await conn.fetchrow(
            "SELECT * FROM admin_users WHERE username = $1",
            login.username
        )
        
        await conn.close()
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not bcrypt.checkpw(login.password.encode(), admin['password_hash'].encode()):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create JWT token
        token = jwt.encode(
            {
                "username": admin['username'],
                "role": "admin",
                "exp": datetime.utcnow() + timedelta(days=7)
            },
            JWT_SECRET,
            algorithm="HS256"
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": admin['username']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.get("/dashboard/stats")
async def get_dashboard_stats(admin: dict = Depends(verify_admin_token)):
    """Get dashboard statistics"""
    try:
        conn = await get_db_connection()
        
        # Total subscriptions
        total_subs = await conn.fetchval(
            "SELECT COUNT(*) FROM subscriptions WHERE subscription_status = 'active'"
        )
        
        # Total revenue (from Stripe)
        # This is a placeholder - in production, fetch from Stripe API
        
        # Active users
        active_users = await conn.fetchval(
            "SELECT COUNT(DISTINCT user_id) FROM subscriptions WHERE subscription_status = 'active'"
        )
        
        # Recent subscriptions
        recent_subs = await conn.fetch(
            """
            SELECT s.*, u.email 
            FROM subscriptions s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
            LIMIT 10
            """
        )
        
        await conn.close()
        
        return {
            "total_subscriptions": total_subs or 0,
            "active_users": active_users or 0,
            "monthly_revenue": 0,  # Calculate from Stripe
            "recent_subscriptions": [dict(sub) for sub in recent_subs] if recent_subs else []
        }
    
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard stats")


@app.get("/subscriptions")
async def get_all_subscriptions(
    skip: int = 0,
    limit: int = 50,
    admin: dict = Depends(verify_admin_token)
):
    """Get all subscriptions"""
    try:
        conn = await get_db_connection()
        
        subscriptions = await conn.fetch(
            """
            SELECT 
                s.*,
                u.email,
                u.full_name
            FROM subscriptions s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
            LIMIT $1 OFFSET $2
            """,
            limit,
            skip
        )
        
        total = await conn.fetchval("SELECT COUNT(*) FROM subscriptions")
        
        await conn.close()
        
        return {
            "subscriptions": [dict(sub) for sub in subscriptions] if subscriptions else [],
            "total": total or 0,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error fetching subscriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch subscriptions")


@app.get("/plans")
async def get_subscription_plans(admin: dict = Depends(verify_admin_token)):
    """Get all subscription plans"""
    try:
        conn = await get_db_connection()
        
        plans = await conn.fetch("SELECT * FROM subscription_plans ORDER BY price ASC")
        
        await conn.close()
        
        return {"plans": [dict(plan) for plan in plans] if plans else []}
    
    except Exception as e:
        logger.error(f"Error fetching plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch plans")


@app.post("/plans")
async def create_subscription_plan(
    plan: SubscriptionPlanUpdate,
    admin: dict = Depends(verify_admin_token)
):
    """Create or update subscription plan"""
    try:
        conn = await get_db_connection()
        
        await conn.execute(
            """
            INSERT INTO subscription_plans (
                plan_name, price, stripe_price_id, features, description, updated_at
            ) VALUES ($1, $2, $3, $4, $5, NOW())
            ON CONFLICT (plan_name)
            DO UPDATE SET
                price = $2,
                stripe_price_id = $3,
                features = $4,
                description = $5,
                updated_at = NOW()
            """,
            plan.plan_name,
            plan.price,
            plan.stripe_price_id,
            plan.features,
            plan.description
        )
        
        await conn.close()
        
        logger.info(f"Plan {plan.plan_name} created/updated by {admin['username']}")
        
        return {"status": "success", "message": f"Plan {plan.plan_name} updated"}
    
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to create plan")


@app.get("/features")
async def get_features(admin: dict = Depends(verify_admin_token)):
    """Get all feature flags"""
    try:
        conn = await get_db_connection()
        
        features = await conn.fetch("SELECT * FROM feature_flags ORDER BY feature_name ASC")
        
        await conn.close()
        
        return {"features": [dict(feature) for feature in features] if features else []}
    
    except Exception as e:
        logger.error(f"Error fetching features: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch features")


@app.post("/features")
async def update_feature(
    feature: FeatureToggle,
    admin: dict = Depends(verify_admin_token)
):
    """Update feature flag"""
    try:
        conn = await get_db_connection()
        
        await conn.execute(
            """
            INSERT INTO feature_flags (
                feature_name, requires_subscription, description, updated_at
            ) VALUES ($1, $2, $3, NOW())
            ON CONFLICT (feature_name)
            DO UPDATE SET
                requires_subscription = $2,
                description = $3,
                updated_at = NOW()
            """,
            feature.feature_name,
            feature.requires_subscription,
            feature.description
        )
        
        await conn.close()
        
        logger.info(f"Feature {feature.feature_name} updated by {admin['username']}")
        
        return {"status": "success", "message": f"Feature {feature.feature_name} updated"}
    
    except Exception as e:
        logger.error(f"Error updating feature: {e}")
        raise HTTPException(status_code=500, detail="Failed to update feature")


@app.get("/stripe/prices")
async def get_stripe_prices(admin: dict = Depends(verify_admin_token)):
    """Get all prices from Stripe"""
    try:
        prices = stripe.Price.list(limit=100, active=True)
        
        return {
            "prices": [
                {
                    "id": price.id,
                    "product": price.product,
                    "unit_amount": price.unit_amount,
                    "currency": price.currency,
                    "recurring": price.recurring,
                    "active": price.active
                }
                for price in prices.data
            ]
        }
    
    except Exception as e:
        logger.error(f"Error fetching Stripe prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Stripe prices")


@app.get("/stripe/products")
async def get_stripe_products(admin: dict = Depends(verify_admin_token)):
    """Get all products from Stripe"""
    try:
        products = stripe.Product.list(limit=100, active=True)
        
        return {
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "active": product.active,
                    "metadata": product.metadata
                }
                for product in products.data
            ]
        }
    
    except Exception as e:
        logger.error(f"Error fetching Stripe products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Stripe products")


@app.post("/subscription/{user_id}/cancel")
async def cancel_user_subscription(
    user_id: str,
    admin: dict = Depends(verify_admin_token)
):
    """Cancel a user's subscription (admin override)"""
    try:
        conn = await get_db_connection()
        
        subscription = await conn.fetchrow(
            "SELECT stripe_subscription_id FROM subscriptions WHERE user_id = $1",
            user_id
        )
        
        if not subscription:
            await conn.close()
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Cancel in Stripe
        stripe.Subscription.delete(subscription['stripe_subscription_id'])
        
        # Update in database
        await conn.execute(
            "UPDATE subscriptions SET subscription_status = 'canceled', updated_at = NOW() WHERE user_id = $1",
            user_id
        )
        
        await conn.close()
        
        logger.info(f"Subscription for user {user_id} canceled by admin {admin['username']}")
        
        return {"status": "success", "message": "Subscription canceled"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@app.post("/init-admin")
async def initialize_admin():
    """Initialize admin user (run once)"""
    try:
        default_password = "Admin@123!Swiply"
        password_hash = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()
        
        conn = await get_db_connection()
        
        # Create admin user
        await conn.execute(
            """
            INSERT INTO admin_users (username, password_hash, created_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (username) DO NOTHING
            """,
            ADMIN_USERNAME,
            password_hash
        )
        
        await conn.close()
        
        return {
            "status": "success",
            "username": ADMIN_USERNAME,
            "default_password": default_password,
            "message": "Admin user created. CHANGE PASSWORD IMMEDIATELY!"
        }
    
    except Exception as e:
        logger.error(f"Error initializing admin: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize admin")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)
