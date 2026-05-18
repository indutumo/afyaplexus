# analytics/utils.py

import uuid
import requests

def generate_visitor_id():
    return str(uuid.uuid4())


def get_client_ip(request):

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    # 🚨 FIX LOCAL IPS
    if ip in ["127.0.0.1", "::1"]:
        return None

    return ip



def get_geo_data(ip):

    if not ip:
        return {}

    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}",
            timeout=2
        )

        data = response.json()

        # 🚨 IMPORTANT CHECK
        if data.get("status") != "success":
            return {}

        return data

    except:
        return {}