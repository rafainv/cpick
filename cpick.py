import os
import time
from seleniumbase import SB
from selenium.webdriver.common.action_chains import ActionChains

# ==========================
#  ENV
# ==========================
URL = os.getenv("URL")
COOK = os.getenv("COOKIES")

if not URL:
    raise SystemExit("❌ ERRO: variável URL não encontrada.")
if not COOK:
    raise SystemExit("❌ ERRO: variável COOKIES não encontrada.")


# ==========================================================
#  FUNÇÃO PARA BYPASS CLOUDLFLARE TURNSTILE Avançado
# ==========================================================
def solve_turnstile(sb, timeout=25):
    print("Aguardando Turnstile...")

    end = time.time() + timeout

    while time.time() < end:
        try:
            # 1 — localizar iframe do Turnstile
            iframe = sb.driver.find_element("css selector", "iframe[src*='challenge']")
            sb.driver.switch_to.frame(iframe)

            # 2 — tenta clicar no checkbox (turnstile normal)
            try:
                chk = sb.driver.find_element("css selector", "input[type='checkbox']")
                chk.click()
                sb.driver.switch_to.default_content()
                print("Turnstile OK (checkbox).")
                return True
            except:
                pass

            # 3 — tenta clicar via JS (shadow DOM)
            try:
                sb.driver.execute_script("""
                    try {
                        let t = document.querySelector("input[type='checkbox']");
                        if(t){ t.click(); }
                    } catch(e){}
                """)
                sb.driver.switch_to.default_content()
                print("Turnstile OK (shadow dom).")
                return True
            except:
                pass

            sb.driver.switch_to.default_content()

        except:
            pass

        time.sleep(1)

    print("⚠ Turnstile não resolveu a tempo.")
    return False


# ==========================================================
#  FUNÇÃO PARA CLICK HUMANO REAL
# ==========================================================
def human_click(sb, element):
    sb.scroll_to(element)
    time.sleep(1)

    box = element.rect
    x = int(box["x"] + box["width"] / 2)
    y = int(box["y"] + box["height"] / 2)

    print("Coordenadas do botão:", x, y)

    # Reset cursor
    actions = ActionChains(sb.driver)
    actions.move_by_offset(-9999, -9999).perform()

    # Move até o botão e clica
    actions = ActionChains(sb.driver)
    actions.move_by_offset(x, y).pause(0.25).click().perform()

    print("CLICK HUMANO REAL EXECUTADO")


# ==========================================================
#  SCRIPT PRINCIPAL
# ==========================================================
with SB(uc=True, test=True, headed=False) as sb:
    sb.open(URL)

    print("Aplicando cookies...")

    # adicionar cookies
    expire = int(time.time()) + (30 * 24 * 60 * 60)
    for c in COOK.split("; "):
        if "=" not in c:
            continue
        name, value = c.split("=", 1)
        sb.add_cookie({
            "name": name,
            "value": value,
            "path": "/",
            "expiry": expire,
            "sameSite": "Lax",
        })

    sb.refresh()
    sb.sleep(5)

    # resolver Turnstile
    solve_turnstile(sb, timeout=25)

    sb.sleep(3)

    # localizar botão Claim
    print("Localizando botão Claim...")
    btn = sb.find_element("#process_claim_hourly_faucet", timeout=20)

    # click humano real (funciona sempre)
    human_click(sb, btn)

    sb.sleep(10)

    sb.save_screenshot("screen.png")

    print("=== FIM ===")
