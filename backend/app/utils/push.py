import os
import json

from pywebpush import (
    webpush,
    WebPushException,
)


# ============================================================
# VAPID CONFIGURATION
# ============================================================

VAPID_PRIVATE_KEY = os.getenv(
    "VAPID_PRIVATE_KEY"
)

VAPID_PUBLIC_KEY = os.getenv(
    "VAPID_PUBLIC_KEY"
)

VAPID_CLAIMS = {
    "sub": "mailto:adminrefindx@gmail.com"
}


# ============================================================
# SEND PUSH NOTIFICATION
# ============================================================

def send_push_notification(
    subscription,
    message,
    item_id=None,
    notification_id=None,
    url="/notifications",
):
    """
    Send a Web Push notification
    to one browser/device.
    """

    # --------------------------------------------------------
    # CHECK VAPID PRIVATE KEY
    # --------------------------------------------------------

    if not VAPID_PRIVATE_KEY:

        print(
            "VAPID_PRIVATE_KEY is not configured."
        )

        return False


    # --------------------------------------------------------
    # CHECK VAPID PUBLIC KEY
    # --------------------------------------------------------

    if not VAPID_PUBLIC_KEY:

        print(
            "VAPID_PUBLIC_KEY is not configured."
        )

        return False


    # --------------------------------------------------------
    # SUBSCRIPTION DATA
    # --------------------------------------------------------

    subscription_info = {

        "endpoint":
            subscription.endpoint,

        "keys": {

            "p256dh":
                subscription.p256dh,

            "auth":
                subscription.auth,

        },

    }


    # --------------------------------------------------------
    # PUSH PAYLOAD
    # --------------------------------------------------------

    payload = {

        "title":
            "ReFindX",

        "body":
            message,

        "icon":
            "/refindx-logo.png",

        "item_id":
            item_id,

        "notification_id":
            notification_id,

        "url":
            url,

    }


    # --------------------------------------------------------
    # CONVERT TO VALID JSON
    # --------------------------------------------------------

    payload_json = json.dumps(
        payload
    )


    # --------------------------------------------------------
    # SEND WEB PUSH
    # --------------------------------------------------------

    try:

        webpush(

            subscription_info=
                subscription_info,

            data=
                payload_json,

            vapid_private_key=
                VAPID_PRIVATE_KEY,

            vapid_claims=
                VAPID_CLAIMS,

        )


        print(
            "Push notification sent successfully."
        )


        return True


    # --------------------------------------------------------
    # WEB PUSH ERROR
    # --------------------------------------------------------

    except WebPushException as error:

        print(
            "Web Push error:",
            error
        )

        return False


    # --------------------------------------------------------
    # OTHER ERROR
    # --------------------------------------------------------

    except Exception as error:

        print(
            "Unexpected push error:",
            error
        )

        return False