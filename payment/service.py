import requests
from django.conf import settings
import uuid


class PesaPalService:
    @staticmethod
    def get_token():
        url = f"{settings.PESAPAL_BASE_URL}/api/Auth/RequestToken"

        payload = {
            "consumer_key" : settings.CONSUMER_KEY,
            "consumer_secret": settings.CONSUMER_SECRET
        }

        response = requests.post(url, json=payload)

        return response.json()
    
    @staticmethod
    def create_order(user, amount):
        token = PesaPalService.get_token()

        url = (
            f"{settings.PESAPAL_BASE_URL}",
            "/api/Transactions/SubmitOrderRequest"
        )

        payload = {

            "id": str(uuid.uuid4()),

            "currency": "KES",

            "amount": float(amount),

            "description":
                "SpyderGames Wallet Deposit",

            "callback_url":
                settings.PESAPAL_CALLBACK_URL,

            "notification_id":
                settings.PESAPAL_IPN_ID,

            "billing_address": {

                "email_address":
                    user.email,

                "phone_number":
                    "",

                "country_code":
                    "KE",

                "first_name":
                    user.username,

                "last_name":
                    "",
            }
        }

        headers = {

            "Authorization" : f"Bearer {token}",

            "Content-Type" : "application/json",
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
        )

        data = response.json()

        print(data)

        return data