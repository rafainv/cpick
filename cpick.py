import os
import time
from seleniumbase import SB
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("URL")
cookies = os.getenv("COOKIES")

with SB(uc=True, test=True, headed=False) as sb:
    sb.open(url)

    # Carregar cookies
    expires = int(time.time()) + (30 * 24 * 60 * 60)
    for cookie in cookies.split("; "):
        name, value = cookie.split("=", 1)
        sb.add_cookie(
            {"name": name, "value": value, "path": "/", "expiry": expires}
        )

    sb.refresh()
    sb.sleep(3)

    # ==== SOLVE CLOUDFLARE TURNSTILE (SHADOW DOM & IFRAME) ====
    sb.solve_turnstile(timeout=25)

    sb.sleep(2)

    # ==== CLICK NO CLAIM ====
    sb.click("#process_claim_hourly_faucet", timeout=20)

    sb.sleep(10)
    sb.save_screenshot("screen.png")
