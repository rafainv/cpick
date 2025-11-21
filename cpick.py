import os
import time
from seleniumbase import SB
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL")
COOK = os.getenv("COOKIES")

if not URL:
    raise SystemExit("❌ ERRO: variável URL não encontrada no .env")

if not COOK:
    print("⚠ Nenhum cookie encontrado. Continuando sem cookies...")
    COOK = ""

def wait_turnstile(sb, timeout=30):
    """Espera Cloudflare Turnstile liberar automaticamente."""
    start = time.time()
    print("Aguardando Turnstile...")

    while time.time() - start < timeout:
        try:
            resp = sb.get_value('[name="cf-turnstile-response"]')
            if resp and len(resp) > 20:
                print("Turnstile OK!")
                return True
        except:
            pass

        sb.sleep(1)

    print("⚠ Turnstile não resolveu a tempo.")
    return False


def human_click(sb, selector):
    """Clique humano real (simula mouse físico)."""
    from selenium.webdriver.common.action_chains import ActionChains

    try:
        btn = sb.find_element(selector)
        sb.scroll_to(btn)
        sb.sleep(1)

        actions = ActionChains(sb.driver)
        actions.move_to_element(btn).pause(0.3).click().perform()

        print("CLICK HUMANO OK!")
        return True
    except Exception as e:
        print("ERRO NO CLICK HUMANO:", e)
        return False


with SB(uc=True, test=True, headed=False) as sb:
    print("Abrindo URL...")
    sb.open(URL)
    sb.sleep(3)

    # ------------------ COOKIES ------------------
    if COOK:
        expires = int(time.time()) + 90 * 24 * 60 * 60
        for c in COOK.split("; "):
            if "=" not in c:
                continue
            name, value = c.split("=", 1)
            sb.add_cookie({
                "name": name,
                "value": value,
                "path": "/",
                "expiry": expires,
                "sameSite": "Lax"
            })

        sb.refresh()
        sb.sleep(3)

    # ------------------ TURNO ------------------
    wait_turnstile(sb, 30)

    sb.sleep(2)

    # ------------------ CLAIM ------------------
    print("Tentando clicar no botão CLAIM...")
    human_click(sb, "#process_claim_hourly_faucet")

    sb.sleep(7)

    print("Salvando screenshot...")
    sb.save_screenshot("screen.png")

    print("=== FIM ===")
