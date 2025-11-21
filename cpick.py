#!/usr/bin/env python3
import os
import time
from seleniumbase import SB
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

load_dotenv()

URL  = os.getenv("URL")
COOK = os.getenv("COOKIES")


def solve_turnstile(sb, timeout=30):
    print("Aguardando Turnstile...")

    # tenta achar iframe dentro do shadow DOM
    t0 = time.time()
    iframe = None

    while time.time() - t0 < timeout:
        try:
            iframe = sb.driver.execute_script("""
            try {
                const host = document.querySelector('#cf_turnstile');
                if (!host) return null;
                const root = host.shadowRoot;
                if (!root) return null;
                const iframe = root.querySelector('iframe');
                return iframe || null;
            } catch(e){ return null; }
            """)
            if iframe:
                break
        except:
            pass
        time.sleep(0.5)

    if not iframe:
        print("⚠ Turnstile não encontrado dentro do shadowRoot.")
        return False

    try:
        sb.switch_to_frame(iframe)

        print("Iframe do Turnstile localizado!")

        # tenta clicar o checkbox (varredura)
        clicked = False
        selectors = [
            "input[type='checkbox']",
            "div[role='button']",
            ".ctp-checkbox",
            ".label",
        ]

        for sel in selectors:
            try:
                sb.click(sel, timeout=3)
                clicked = True
                print("Clicou no Turnstile:", sel)
                break
            except:
                pass

        sb.switch_to_default_content()

        if not clicked:
            print("⚠ Nenhum seletor clicável encontrado dentro do Turnstile.")
            return False

        # aguardando resposta
        for _ in range(20):
            value = sb.get_attribute("#cf-chl-widget-b4m8z_response", "value")
            if value and len(value) > 10:
                print("Turnstile resolvido!")
                return True
            time.sleep(1)

        print("⚠ Turnstile não resolveu a tempo.")
        return False

    except Exception as e:
        print("Erro resolvendo Turnstile:", e)
        return False


def click_humano(sb, selector):
    try:
        btn = sb.find_element(selector)
        sb.scroll_to(btn)
        sb.sleep(1)

        actions = ActionChains(sb.driver)
        actions.move_to_element(btn).pause(0.2).click().perform()

        print("CLICK HUMANO OK")
        return True
    except Exception as e:
        print("Erro no click humano:", e)
        return False


def click_absoluto(sb, selector):
    try:
        btn = sb.find_element(selector)
        box = btn.rect
        x = int(box["x"] + box["width"] / 2)
        y = int(box["y"] + box["height"] / 2)

        print("Coordenadas:", x, y)

        # reset cursor
        actions = ActionChains(sb.driver)
        actions.move_by_offset(-9999, -9999).perform()

        # click no ponto real
        actions = ActionChains(sb.driver)
        actions.move_by_offset(x, y).pause(0.25).click().perform()

        print("CLICK ABSOLUTO OK")
        return True

    except Exception as e:
        print("Erro click absoluto:", e)
        return False


# ----------------------------------------------------
#               MAIN CODE
# ----------------------------------------------------

with SB(uc=True, test=True, headed=False) as sb:

    sb.open(URL)

    # Aplicar cookies
    exp = int(time.time()) + 86400*30
    for c in COOK.split("; "):
        name, value = c.split("=", 1)
        sb.add_cookie({"name":name, "value":value, "path":"/", "expiry":exp})

    sb.refresh()
    sb.sleep(4)

    # Resolver Cloudflare Turnstile
    solve_turnstile(sb, timeout=30)

    sb.sleep(2)

    # Clicar Claim (3 métodos)
    sel = "#process_claim_hourly_faucet"

    if not click_humano(sb, sel):
        click_absoluto(sb, sel)

    sb.sleep(8)

    sb.save_screenshot("screen.png")

print("=== FIM ===")
