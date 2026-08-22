"""
Stripe Payment Service
Handles subscription payments and checkout sessions
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import stripe
import os
from datetime import datetime
import asyncpg
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "swiply")
DB_PASSWORD = os.getenv("DB_PASSWORD", "swiply_secure_pwd_2026!")
DB_NAME = os.getenv("DB_NAME", "swiply")


class CheckoutRequest(BaseModel):
    user_id: str
    email: str
    plan: str = "premium"  # premium, pro, etc.


class SubscriptionResponse(BaseModel):
    status: str
    subscription_id: Optional[str] = None
    current_period_end: Optional[str] = None


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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "payment"}


@app.post("/create-checkout-session")
async def create_checkout_session(checkout_request: CheckoutRequest):
    """
    Create a Stripe Checkout session for subscription
    """
    try:
        logger.info(f"Creating checkout session for user: {checkout_request.user_id}")
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=checkout_request.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f"{FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/payment/cancel",
            metadata={
                'user_id': checkout_request.user_id,
                'plan': checkout_request.plan
            },
            subscription_data={
                'metadata': {
                    'user_id': checkout_request.user_id,
                    'plan': checkout_request.plan
                }
            }
        )
        
        logger.info(f"Checkout session created: {checkout_session.id}")
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@app.get("/subscription/{user_id}")
async def get_subscription_status(user_id: str):
    """
    Get subscription status for a user
    """
    try:
        conn = await get_db_connection()
        
        # Get subscription from database
        subscription = await conn.fetchrow(
            """
            SELECT 
                stripe_subscription_id,
                stripe_customer_id,
                subscription_status,
                current_period_end,
                plan_type
            FROM subscriptions
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            user_id
        )
        
        await conn.close()
        
        if not subscription:
            return {
                "status": "none",
                "subscription_id": None,
                "current_period_end": None,
                "plan_type": None
            }
        
        return {
            "status": subscription['subscription_status'],
            "subscription_id": subscription['stripe_subscription_id'],
            "customer_id": subscription['stripe_customer_id'],
            "current_period_end": subscription['current_period_end'].isoformat() if subscription['current_period_end'] else None,
            "plan_type": subscription['plan_type']
        }
    
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subscription status")


@app.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhooks for subscription events
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            # For testing without webhook secret
            import json
            event = json.loads(payload)
        
        logger.info(f"Received webhook event: {event['type']}")
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            await handle_checkout_completed(session)
        
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            await handle_subscription_updated(subscription)
        
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            await handle_subscription_deleted(subscription)
        
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            await handle_payment_succeeded(invoice)
        
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            await handle_payment_failed(invoice)
        
        return {"status": "success"}
    
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def handle_checkout_completed(session):
    """Handle successful checkout completion"""
    try:
        user_id = session['metadata']['user_id']
        plan = session['metadata'].get('plan', 'premium')
        
        # Get subscription details
        subscription_id = session.get('subscription')
        customer_id = session.get('customer')
        
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            conn = await get_db_connection()
            
            # Insert or update subscription
            await conn.execute(
                """
                INSERT INTO subscriptions (
                    user_id, 
                    stripe_subscription_id, 
                    stripe_customer_id, 
                    subscription_status, 
                    plan_type,
                    current_period_start,
                    current_period_end,
                    created_at,
                    updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    stripe_subscription_id = $2,
                    stripe_customer_id = $3,
                    subscription_status = $4,
                    plan_type = $5,
                    current_period_start = $6,
                    current_period_end = $7,
                    updated_at = NOW()
                """,
                user_id,
                subscription_id,
                customer_id,
                subscription['status'],
                plan,
                datetime.fromtimestamp(subscription['current_period_start']),
                datetime.fromtimestamp(subscription['current_period_end'])
            )
            
            await conn.close()
            logger.info(f"Subscription created for user: {user_id}")
    
    except Exception as e:
        logger.error(f"Error handling checkout completion: {e}")


async def handle_subscription_updated(subscription):
    """Handle subscription update"""
    try:
        subscription_id = subscription['id']
        
        conn = await get_db_connection()
        
        await conn.execute(
            """
            UPDATE subscriptions
            SET 
                subscription_status = $1,
                current_period_start = $2,
                current_period_end = $3,
                updated_at = NOW()
            WHERE stripe_subscription_id = $4
            """,
            subscription['status'],
            datetime.fromtimestamp(subscription['current_period_start']),
            datetime.fromtimestamp(subscription['current_period_end']),
            subscription_id
        )
        
        await conn.close()
        logger.info(f"Subscription updated: {subscription_id}")
    
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")


async def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        subscription_id = subscription['id']
        
        conn = await get_db_connection()
        
        await conn.execute(
            """
            UPDATE subscriptions
            SET 
                subscription_status = 'canceled',
                updated_at = NOW()
            WHERE stripe_subscription_id = $1
            """,
            subscription_id
        )
        
        await conn.close()
        logger.info(f"Subscription canceled: {subscription_id}")
    
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")


async def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    try:
        subscription_id = invoice.get('subscription')
        
        if subscription_id:
            conn = await get_db_connection()
            
            await conn.execute(
                """
                UPDATE subscriptions
                SET 
                    subscription_status = 'active',
                    updated_at = NOW()
                WHERE stripe_subscription_id = $1
                """,
                subscription_id
            )
            
            await conn.close()
            logger.info(f"Payment succeeded for subscription: {subscription_id}")
    
    except Exception as e:
        logger.error(f"Error handling payment success: {e}")


async def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        subscription_id = invoice.get('subscription')
        
        if subscription_id:
            conn = await get_db_connection()
            
            await conn.execute(
                """
                UPDATE subscriptions
                SET 
                    subscription_status = 'past_due',
                    updated_at = NOW()
                WHERE stripe_subscription_id = $1
                """,
                subscription_id
            )
            
            await conn.close()
            logger.info(f"Payment failed for subscription: {subscription_id}")
    
    except Exception as e:
        logger.error(f"Error handling payment failure: {e}")


@app.post("/cancel-subscription/{user_id}")
async def cancel_subscription(user_id: str):
    """Cancel a user's subscription"""
    try:
        conn = await get_db_connection()
        
        # Get subscription
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
            """
            UPDATE subscriptions
            SET subscription_status = 'canceled', updated_at = NOW()
            WHERE user_id = $1
            """,
            user_id
        )
        
        await conn.close()
        
        return {"status": "success", "message": "Subscription canceled"}
    
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
