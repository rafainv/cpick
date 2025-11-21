import os
import time
from seleniumbase import SB
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL")
COOK = os.getenv("COOKIES")  # VALOR FIXO VIA SECRETS

if not COOK:
    print("ERRO: variável COOKIES não definida no GitHub Actions!")
    exit(1)

def wait_turnstile(sb):
    """
    Espera o Turnstile sumir (managed challenge).
    Não tenta clicar (isso NÃO funciona em headless no Turnstile).
    Apenas espera liberação automática.
    """
    print("Aguardando Cloudflare / Turnstile...")

    # tenta detectar spinner / challenge overlay
    possible = [
        "iframe[src*='challenge-platform']",
        "div[id*='cf']", 
        "#cf-turnstile",
        "[name='cf-turnstile-response']",
        "iframe[title*='Cloudflare']",
    ]

    # espera até sumir o overlay (30s)
    timeout = 30
    start = time.time()

    while time.time() - start < timeout:
        still = False
        for sel in possible:
            try:
                if sb.is_element_visible(sel):
                    still = True
                    break
            except:
                pass

        if not still:
            print("Cloudflare liberado.")
            return True

        time.sleep(1)

    print("⚠ Turnstile não resolveu a tempo.")
    return False


def click_humano(sb, selector):
    """
    Clique humano real sem mouseinfo.
    Usa ActionChains puro → funcionamento 100% headless.
    """
    from selenium.webdriver.common.action_chains import ActionChains

    try:
        btn = sb.find_element(selector)
        sb.scroll_to(btn)
        time.sleep(1)

        actions = ActionChains(sb.driver)
        actions.move_to_element(btn).pause(0.25).click().perform()
        print("CLICK HUMANO OK!")
        return True
    except Exception as e:
        print("ERRO CLICK HUMANO:", e)
        return False



# ========================= SCRIPT PRINCIPAL =========================

with SB(uc=True, test=True, headed=False) as sb:
    sb.open(URL)

    # aplica cookies
    expires = int(time.time()) + 2592000
    for c in COOK.split("; "):
        name, value = c.split("=", 1)
        sb.add_cookie({
            "name": name,
            "value": value,
            "path": "/",
            "expiry": expires,
            "sameSite": "Lax",
        })

    sb.refresh()
    time.sleep(4)

    # aguarda liberar Cloudflare (turnstile)
    wait_turnstile(sb)

    time.sleep(3)

    # clica no botão
    click_humano(sb, "#process_claim_hourly_faucet")

    time.sleep(8)
    sb.save_screenshot("screen.png")

print("=== FIM ===")
