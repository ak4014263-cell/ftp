"""
Subscription Middleware - Check user subscription before allowing access to features
"""
import asyncpg
import os
from fastapi import HTTPException, Request
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Database configuration
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "swiply")
DB_PASSWORD = os.getenv("DB_PASSWORD", "swiply_secure_pwd_2026!")
DB_NAME = os.getenv("DB_NAME", "swiply")


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


async def check_feature_access(user_id: str, feature_name: str) -> dict:
    """
    Check if user has access to a feature
    Returns dict with: { "has_access": bool, "message": str, "subscription_required": bool }
    """
    try:
        conn = await get_db_connection()
        
        # Check if feature requires subscription
        feature = await conn.fetchrow(
            "SELECT requires_subscription FROM feature_flags WHERE feature_name = $1",
            feature_name
        )
        
        if not feature:
            # Feature not found, allow access by default
            await conn.close()
            return {
                "has_access": True,
                "message": "Feature access granted",
                "subscription_required": False
            }
        
        # If feature doesn't require subscription, allow access
        if not feature['requires_subscription']:
            await conn.close()
            return {
                "has_access": True,
                "message": "Feature access granted",
                "subscription_required": False
            }
        
        # Check user subscription status
        subscription = await conn.fetchrow(
            """
            SELECT subscription_status, current_period_end, plan_type
            FROM subscriptions
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            user_id
        )
        
        await conn.close()
        
        # No subscription found
        if not subscription:
            return {
                "has_access": False,
                "message": "This feature requires an active subscription",
                "subscription_required": True,
                "subscription_status": "none"
            }
        
        # Check if subscription is active
        if subscription['subscription_status'] != 'active':
            return {
                "has_access": False,
                "message": f"Subscription is {subscription['subscription_status']}. Please activate your subscription to use this feature.",
                "subscription_required": True,
                "subscription_status": subscription['subscription_status']
            }
        
        # All checks passed
        return {
            "has_access": True,
            "message": "Feature access granted",
            "subscription_required": True,
            "subscription_status": "active",
            "plan_type": subscription['plan_type']
        }
    
    except Exception as e:
        logger.error(f"Error checking feature access: {e}")
        # On error, deny access to be safe
        return {
            "has_access": False,
            "message": "Error checking subscription status",
            "subscription_required": True
        }


async def check_daily_limit(user_id: str, limit_type: str = "applications") -> dict:
    """
    Check if user has exceeded daily limits (for free tier)
    Returns dict with: { "within_limit": bool, "used": int, "limit": int }
    """
    try:
        conn = await get_db_connection()
        
        # Check subscription status
        subscription = await conn.fetchrow(
            "SELECT subscription_status FROM subscriptions WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1",
            user_id
        )
        
        # If user has active subscription, no limits
        if subscription and subscription['subscription_status'] == 'active':
            await conn.close()
            return {
                "within_limit": True,
                "used": 0,
                "limit": -1,  # -1 means unlimited
                "message": "Unlimited access with active subscription"
            }
        
        # Count today's usage
        today_count = await conn.fetchval(
            f"""
            SELECT COUNT(*) FROM applications
            WHERE user_id = $1 AND created_at >= CURRENT_DATE
            """,
            user_id
        )
        
        await conn.close()
        
        # Free tier limit
        free_limit = 5
        
        if today_count >= free_limit:
            return {
                "within_limit": False,
                "used": today_count,
                "limit": free_limit,
                "message": f"Daily limit of {free_limit} applications reached. Upgrade to Premium for unlimited access."
            }
        
        return {
            "within_limit": True,
            "used": today_count,
            "limit": free_limit,
            "message": f"Used {today_count} of {free_limit} daily applications"
        }
    
    except Exception as e:
        logger.error(f"Error checking daily limit: {e}")
        return {
            "within_limit": False,
            "used": 0,
            "limit": 0,
            "message": "Error checking daily limit"
        }


def require_subscription(feature_name: str):
    """
    Decorator to protect routes that require subscription
    Usage:
        @app.post("/apply-job")
        @require_subscription("job_application")
        async def apply_job(user_id: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or request
            user_id = kwargs.get('user_id')
            request = kwargs.get('request')
            
            if not user_id and request:
                # Try to get user_id from request body or query
                try:
                    body = await request.json()
                    user_id = body.get('user_id')
                except:
                    pass
            
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID required")
            
            # Check feature access
            access = await check_feature_access(user_id, feature_name)
            
            if not access['has_access']:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "subscription_required",
                        "message": access['message'],
                        "feature": feature_name,
                        "subscription_status": access.get('subscription_status', 'none')
                    }
                )
            
            # Access granted, proceed with function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
