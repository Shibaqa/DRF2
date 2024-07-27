import os

import stripe

from users.models import Payments
stripe_api_key = os.getenv('STRIPE_SECRET_KEY')


def create_stripe_price(payment):
    stripe.api_key = stripe_api_key
    stripe_product = stripe.Product.create(
        name=payment.paid_course.name
    )

    stripe_price = stripe.Price.create(
        currency="rub",
        unit_amount=payment.payment_amount*100,
        product_data={"name": stripe_product['name']},
    )

    return stripe_price['id']


def create_stripe_session(stripe_price_id):
    stripe.api_key = stripe_api_key
    stripe_session = stripe.checkout.Session.create(
        line_items=[{
            'price': stripe_price_id,
            'quantity': 1
        }],
        mode='payment',
        success_url='https://example.com/success',
    )

    return stripe_session['url'], stripe_session['id']