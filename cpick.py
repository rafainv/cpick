import os
import time
from seleniumbase import SB
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("URL")
cookies = os.getenv("COOKIES")

with SB(uc=True, test=True, headed=False) as sb:
    sb.open(url)

    # cookies
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
    sb.sleep(3)

    # ==== WAIT CLOUDFLARE AUTO-CHALLENGE ==== #
    try:
        print("Aguardando Cloudflare liberar...")

        sb.wait_for_element_absent(
            "div[id*='cf-spinner'], div[class*='challenge'], #challenge-stage",
            timeout=25
        )

        sb.sleep(2)
        print("Cloudflare liberado!")
    except Exception:
        print("Cloudflare talvez já esteja liberado.")

    # solve fallback captcha
    try:
        sb.solve_captcha()
    except:
        pass

    sb.sleep(5)

    # claim
    sb.click("#process_claim_hourly_faucet", timeout=20)
    sb.sleep(10)

    sb.save_screenshot("screen.png")
