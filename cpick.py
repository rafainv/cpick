import os
import time
from seleniumbase import SB
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("URL")
cookies = os.getenv("COOKIES")

def wait_turnstile(sb, timeout=30):
    print("Aguardando Turnstile...")
    start = time.time()
    while time.time() - start < timeout:
        value = sb.execute_script("""
            let el = document.querySelector('input[name="cf-turnstile-response"]');
            return el ? el.value : null;
        """)
        if value and len(value) > 50:
            print("Turnstile resolvido!")
            return True
        sb.sleep(1)
    print("⚠ Turnstile não resolveu a tempo.")
    return False

with SB(uc=True, test=True, headed=False) as sb:
    sb.open(url)

    # Adicionar cookies
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
    sb.sleep(4)

    # === AGUARDAR TURNSTILE AUTO-RESOLVE ===
    wait_turnstile(sb, timeout=40)

    sb.sleep(3)

    # === CLICK NO BOTÃO ===
    sb.scroll_to("#process_claim_hourly_faucet")
    sb.sleep(1)
    sb.click("#process_claim_hourly_faucet", timeout=20)

    sb.sleep(8)
    sb.save_screenshot("screen.png")
