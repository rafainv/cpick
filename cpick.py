import os
import time
from seleniumbase import SB
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL")
COOK = os.getenv("COOKIES")   # cookies no formato "a=1; b=2; c=3"

if not URL:
    raise Exception("ERRO: Variável URL não definida no .env")

if not COOK:
    raise Exception("ERRO: Variável COOKIES não definida no .env")

# ---------------------------------------------------------
# Função: esperar Turnstile Cloudflare desaparecer
# ---------------------------------------------------------
def wait_turnstile(sb, timeout=40):
    print("Aguardando Turnstile...")

    for i in range(timeout):
        try:
            exist = sb.is_element_visible('iframe[src*="turnstile"]')
            if not exist:
                print("✔ Turnstile liberado!")
                return True
        except:
            pass
        time.sleep(1)

    print("⚠ Turnstile não resolveu a tempo.")
    return False

# ---------------------------------------------------------
# Função: clicar humanamente no botão Claim
# ---------------------------------------------------------
def click_claim(sb):
    selector = "#process_claim_hourly_faucet"

    btn = sb.find_element(selector)
    sb.scroll_to(btn)
    sb.sleep(1)

    # ActionChains (simula usuário real)
    actions = ActionChains(sb.driver)
    actions.move_to_element(btn).pause(0.3).click().perform()

    print("✔ Click humano executado!")


# ---------------------------------------------------------
# SCRIPT PRINCIPAL
# ---------------------------------------------------------
with SB(uc=True, locale_code="pt-BR", headed=False, test=True) as sb:
    print("Abrindo página...")
    sb.open(URL)

    # ---- Aplicar cookies ----
    expires = int(time.time()) + 3600 * 24 * 30

    for c in COOK.split("; "):
        if "=" not in c:
            continue
        name, value = c.split("=", 1)
        sb.add_cookie({
            "name": name,
            "value": value,
            "path": "/",
            "expiry": expires,
            "sameSite": "Lax",
        })

    sb.refresh()
    sb.sleep(3)

    # ---- Aguardar Cloudflare / Turnstile ----
    wait_turnstile(sb, timeout=40)
    sb.sleep(2)

    # ---- Tentar Solve Automático (SeleniumBase AI) ----
    try:
        sb.solve_captcha()
        print("Captcha resolvido pelo SeleniumBase.")
    except Exception:
        print("solve_captcha não resolveu, continuando manual.")

    sb.sleep(3)

    # ---- Clicar no botão CLAIM ----
    try:
        click_claim(sb)
    except Exception as e:
        print("Erro ao clicar no claim:", e)

    sb.sleep(6)

    sb.save_screenshot("resultado.png")
    print("🖼 Screenshot salvo: resultado.png")

print("=== FIM ===")
