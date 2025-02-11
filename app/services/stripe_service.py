import app.services.stripe_service as stripe_service
from sqlalchemy.orm import Session
from app import models
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Stripe with your secret key
stripe_service.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_service.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

def construct_event(payload, sig_header):
    """
    Construct a Stripe event from the webhook payload and signature.
    """
    try:
        event = stripe_service.Webhook.construct_event(
            payload, sig_header, stripe_service.webhook_secret
        )
        return event
    except ValueError as e:
        # Invalid payload
        raise ValueError("Invalid payload")
    except stripe_service.error.SignatureVerificationError as e:
        # Invalid signature
        raise ValueError("Invalid signature")

def handle_stripe_event(event, db: Session):
    """
    Handle different types of Stripe events.
    """
    event_type = event['type']
    
    if event_type == 'customer.created':
        handle_customer_created(event['data']['object'], db)
    elif event_type == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'], db)
    elif event_type == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'], db)
    elif event_type == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'], db)
        
def handle_checkout_completed(checkout_session, db: Session):
    if checkout_session['mode'] == 'payment':
        # This is a one-off payment
        handle_one_off_payment(checkout_session, db)
    elif checkout_session['mode'] == 'subscription':
        # This is a subscription
        handle_subscription_payment(checkout_session, db)

def handle_customer_created(customer, db: Session):
    # Check if the user already exists in our database
    user = db.query(models.User).filter(models.User.email == customer['email']).first()
    
    if user:
        # Update the existing user with the Stripe customer ID
        user.stripe_customer_id = customer['id']
    else:
        # Create a new user if they don't exist
        user = models.User(
            email=customer['email'],
            stripe_customer_id=customer['id']
        )
        db.add(user)
    
    db.commit()
    
def handle_one_off_payment(payment_data, db: Session):
    """
    Handle one-off payments and update user's lifetime access status and total paid amount.
    """
    customer_id = payment_data.get('customer')
    if not customer_id:
        return  # No customer associated with this payment

    # Get the amount paid in cents
    amount_paid = payment_data.get('amount_total', 0)  # For Checkout Session
    if amount_paid == 0:
        amount_paid = payment_data.get('amount', 0)  # For PaymentIntent

    # Convert amount from cents to dollars
    amount_paid_dollars = amount_paid / 100

    user = db.query(models.User).filter(models.User.stripe_customer_id == customer_id).first()
    if user:
        user.lifetime_access = True
        user.total_paid = (user.total_paid or 0) + amount_paid_dollars
        db.commit()
        print(f"Updated lifetime access and total paid for user: {user.email}. New total: ${user.total_paid:.2f}")
    else:
        print(f"User not found for Stripe customer ID: {customer_id}")
        
def handle_subscription_payment(payment_data, db: Session):
    # Existing subscription payment logic
    pass

def handle_subscription_created(subscription, db: Session):
    user = db.query(models.User).filter(models.User.stripe_customer_id == subscription['customer']).first()
    
    if user:
        user.stripe_subscription_id = subscription['id']
        user.stripe_product_id = subscription['items']['data'][0]['price']['product']
        user.stripe_price_id = subscription['items']['data'][0]['price']['id']
        user.subscription_status = subscription['status']
        user.subscription_end_date = datetime.fromtimestamp(subscription['current_period_end'])
        db.commit()

def handle_subscription_updated(subscription, db: Session):
    user = db.query(models.User).filter(models.User.stripe_subscription_id == subscription['id']).first()
    
    if user:
        user.stripe_product_id = subscription['items']['data'][0]['price']['product']
        user.stripe_price_id = subscription['items']['data'][0]['price']['id']
        user.subscription_status = subscription['status']
        user.subscription_end_date = datetime.fromtimestamp(subscription['current_period_end'])
        db.commit()

def handle_subscription_deleted(subscription, db: Session):
    user = db.query(models.User).filter(models.User.stripe_subscription_id == subscription['id']).first()
    
    if user:
        user.stripe_subscription_id = None
        user.stripe_product_id = None
        user.stripe_price_id = None
        user.subscription_status = 'canceled'
        user.subscription_end_date = datetime.fromtimestamp(subscription['canceled_at'])
        db.commit()

# Add more helper functions as needed
