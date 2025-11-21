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

    print("Aguardando Cloudflare...")
    sb.sleep(10)  # Cloudflare Managed Challenge (fixo)

    # === garantir que o botão existe no DOM ===
    selector = "#process_claim_hourly_faucet"

    # ====== SCROLL ATÉ O BOTÃO ======
    try:
        sb.scroll_to(selector)
        sb.sleep(1)
    except:
        pass

    # ====== TENTAR CLICK NORMAL ======
    try:
        sb.click(selector, timeout=10)
        print("CLICK NORMAL OK")
    except:
        print("Click normal falhou, tentando agressivo...")

    # ====== CLICK JAVASCRIPT DIRETO ======
    try:
        sb.execute_script("document.querySelector(arguments[0]).click();", selector)
        print("CLICK JS OK")
    except:
        print("JS click falhou.")

    # ====== CLICK VIA DISPATCH EVENT ======
    try:
        sb.execute_script("""
        const btn = document.querySelector(arguments[0]);
        if (btn) {
            btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
        }
        """, selector)
        print("CLICK EVENT OK")
    except:
        print("dispatchEvent falhou")

    # ====== CLICK DENTRO DE IFRAMES (SCAN) ======
    try:
        frames = sb.driver.find_elements("tag name", "iframe")
        print("iframes encontrados:", len(frames))
        for index, frame in enumerate(frames):
            try:
                sb.switch_to_frame(frame)
                try:
                    sb.click(selector, timeout=3)
                    print(f"CLICK EM IFRAME {index} OK")
                except:
                    pass
            except:
                pass
            finally:
                sb.switch_to_default_content()
    except:
        pass

    # ====== CLICK VIA JS GLOBAL (tenta todos os botões possíveis) ======
    sb.execute_script("""
        let b = [...document.querySelectorAll('button, input, div')].filter(x => 
            x.id == 'process_claim_hourly_faucet' ||
            x.textContent.toLowerCase().includes('claim')
        );
        b.forEach(x => x.click());
    """)

    sb.sleep(10)
    sb.save_screenshot("screen.png")
