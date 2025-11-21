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

    # === CLICK CLOUDLFLARE TURNSTILE ===
    try:
        sb.sleep(2)

        iframe = sb.find_element('iframe[src*="turnstile"]')
        sb.switch_to_frame(iframe)

        sb.click("input[type='checkbox']", timeout=10)
        sb.sleep(3)

        sb.switch_to_default_content()
    except Exception as e:
        print("Turnstile não encontrado ou já validado.", e)

    # resolver qualquer captcha extra
    try:
        sb.solve_captcha()
    except:
        pass

    sb.sleep(5)

    sb.click("#process_claim_hourly_faucet", timeout=20)
    sb.sleep(10)

    sb.save_screenshot("screen.png")
