import os
import time
from seleniumbase import SB
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("URL")
cookies = os.getenv("COOKIES")

with SB(uc=True, test=True, headed=False) as sb:
    sb.open(url)

    expires = int(time.time()) + (30 * 24 * 60 * 60)
    expires_date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expires))

    for cookie in cookies.split("; "):
        name, value = cookie.split("=", 1)
        sb.add_cookie(
            {
                "name": name,
                "value": value,
                "path": "/",
                "expiry": expires,
                "sameSite": "Lax",
            }
        )

    sb.refresh()
    sb.sleep(5)

    try:
        sb.solve_captcha()
    except:
        pass

    sb.sleep(5)

    sb.click("#process_claim_hourly_faucet", timeout=15)
    sb.sleep(10)

    sb.save_screenshot("screen.png")
