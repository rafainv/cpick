import os
import time
from dotenv import load_dotenv
from seleniumbase import SB
from selenium.webdriver.common.action_chains import ActionChains

load_dotenv()

URL = os.getenv("URL")
COOK = os.getenv("COOKIES")


def wait_turnstile(sb, timeout=35):
    """
    Detecta e espera o Turnstile liberar automaticamente.
    (sem clicar, sem tkinter)
    """
    print("Aguardando Turnstile...")

    start = time.time()

    while time.time() - start < timeout:
        sb.sleep(1)

        # verifica se já liberou capturando o token oculto
        try:
            token = sb.get_attribute('input[name="cf-turnstile-response"]', "value")
            if token and len(token) > 10:
                print("Turnstile liberou!")
                return True
        except:
            pass

    print("⚠ Turnstile não resolveu a tempo.")
    return False


def click_humano(sb, selector):
    """
    Clique compatível com Cloudflare. Não usa tkinter.
    """
    print("Clicando com ActionChains (humano real)...")

    btn = sb.find_element(selector)
    sb.scroll_to(btn)
    sb.sleep(1)

    actions = ActionChains(sb.driver)
    actions.move_to_element(btn).pause(0.4).click().perform()

    sb.sleep(2)
    print("Clique enviado (ActionChains).")


# ===================================================================
#                            SCRIPT PRINCIPAL
# ===================================================================

with SB(uc=True, test=True, headed=False) as sb:

    if not URL:
        raise SystemExit("ERRO: variável URL não está definida no .env")

    if not COOK:
        raise SystemExit("ERRO: variável COOKIES não está definida no .env")

    sb.open(URL)

    # adicionar cookies
    print("Adicionando cookies...")
    expires = int(time.time()) + 86400 * 30

    for c in COOK.split("; "):
        if "=" in c:
            name, val = c.split("=", 1)
            sb.add_cookie({"name": name, "value": val, "expiry": expires, "path": "/"})

    sb.refresh()
    sb.sleep(4)

    # aguardar turnstile
    wait_turnstile(sb, timeout=40)

    # clicar
    click_humano(sb, "#process_claim_hourly_faucet")

    sb.sleep(5)

    sb.save_screenshot("screen.png")

    print("=== FIM ===")
