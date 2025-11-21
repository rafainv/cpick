import os
import time
from seleniumbase import SB
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

load_dotenv()

URL  = os.getenv("URL")
COOK = os.getenv("COOKIES")

if not COOK:
    raise Exception("❌ Variável COOKIES não encontrada no .env")

def add_cookies(sb, cookie_str):
    expires = int(time.time()) + (30 * 24 * 60 * 60)
    for c in cookie_str.split("; "):
        if "=" in c:
            name, value = c.split("=", 1)
            sb.add_cookie({
                "name": name,
                "value": value,
                "path": "/",
                "sameSite": "Lax",
                "expiry": expires,
            })

def click_humano(sb, selector):
    try:
        el = sb.find_element(selector)
        sb.scroll_to(el)
        sb.sleep(1)

        actions = ActionChains(sb.driver)
        actions.move_to_element(el).pause(0.25).click().perform()

        print("✔ CLICK HUMANO OK")
        return True
    except Exception as e:
        print("✖ Falhou no click humano:", e)
        return False

def click_js(sb, selector):
    try:
        sb.execute_script("document.querySelector(arguments[0]).click();", selector)
        print("✔ CLICK JS OK")
        return True
    except:
        return False


with SB(uc=True, test=True, headed=False) as sb:

    print("🔵 Abrindo página...")
    sb.open(URL)
    sb.sleep(3)

    print("🔵 Inserindo cookies...")
    add_cookies(sb, COOK)

    sb.refresh()
    sb.sleep(4)

    print("🔵 Aguardando Cloudflare liberar...")
    sb.sleep(11)     # Cloudflare Managed Challenge geralmente 5–10s

    selector = "#process_claim_hourly_faucet"

    print("🔵 Tentando clique humano...")
    if not click_humano(sb, selector):

        print("🔵 Tentando clique via JavaScript...")
        if not click_js(sb, selector):

            print("⚠ Nenhum método conseguiu clicar, tentando varredura global...")
            sb.execute_script("""
                [...document.querySelectorAll('*')].forEach(e=>{
                    if(e.id=='process_claim_hourly_faucet' || e.textContent.includes('Claim')){
                        try{ e.click(); }catch{}
                    }
                })
            """)

    sb.sleep(8)

    print("📸 Salvando screenshot...")
    sb.save_screenshot("screen.png")

print("✅ FINALIZADO")
