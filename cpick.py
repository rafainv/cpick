import os
import time
from seleniumbase import sb_cdp
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("URL")
cookies = os.getenv("COOKIES")

sb = sb_cdp.Chrome(url)

expires = int(time.time()) + (30 * 24 * 60 * 60)
expires_date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expires))
for cookie in cookies.split("; "):
    name, value = cookie.split("=", 1)
    sb.execute_script(
        f"document.cookie='{name}={value};expires={expires_date};path=/;SameSite=Lax'"
    )

sb.refresh()

sb.solve_captcha()
token = None
start_time = time.time()
while not token and (time.time() - start_time) < 30:
    token = sb.execute_script("""
        (() => {
            try {
                let item = document.querySelector('[name="cf-turnstile-response"]').value;
                return item && item.length > 20 ? item : null;
            } catch (e) {
                return null;
            }
        })()
    """)
    sb.sleep(1)

sb.sleep(5)

for i in range(5):
    try:
        sb.click("#process_claim_hourly_faucet", timeout=10)
        sb.sleep(10)
        break
    except Exception as e:
        pass
    sb.sleep(10)

sb.save_screenshot("screen.png")

sb.driver.stop()
