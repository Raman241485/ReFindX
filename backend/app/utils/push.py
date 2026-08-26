import os

from pywebpush import webpush, WebPushException


VAPID_PRIVATE_KEY = os.getenv(
    "VAPID_PRIVATE_KEY"
)

VAPID_PUBLIC_KEY = os.getenv(
    "VAPID_PUBLIC_KEY"
)

VAPID_CLAIMS = {
    "sub": "mailto:adminrefindx@gmail.com"
}


def send_push_notification(
    subscription,
    message,
):
    """
    Send a Web Push notification
    to one browser/device.
    """

    if not VAPID_PRIVATE_KEY:
        print(
            "VAPID_PRIVATE_KEY is not configured."
        )
        return False

    if not VAPID_PUBLIC_KEY:
        print(
            "VAPID_PUBLIC_KEY is not configured."
        )
        return False


    subscription_info = {
        "endpoint": subscription.endpoint,
        "keys": {
            "p256dh": subscription.p256dh,
            "auth": subscription.auth,
        },
    }


    payload = {
        "title": "ReFindX",
        "body": message,
        "icon": "/refindx-logo.png",
    }


    try:

        webpush(
            subscription_info=subscription_info,
            data=str(payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )

        return True

    except WebPushException as error:

        print(
            "Web Push error:",
            error
        )

        return False

    except Exception as error:

        print(
            "Unexpected push error:",
            error
        )

        return False