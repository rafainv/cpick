const { connect } = require("puppeteer-real-browser");
const fs = require("fs");
require("dotenv").config({ quiet: true });

const url = process.env.URL;
const login = process.env.LOGIN;
const senha = process.env.SENHA;

const COOKIES_PATH = "cookies.json";

const cpick = async () => {
  const { page, browser } = await connect({
    args: ["--start-maximized"],
    turnstile: true,
    headless: false,
    // disableXvfb: true,
    customConfig: {},
    connectOption: {
      defaultViewport: null,
    },
    plugins: [],
  });

  try {
    if (fs.existsSync(COOKIES_PATH)) {
      const cookies = JSON.parse(fs.readFileSync(COOKIES_PATH));
      await page.setCookie(...cookies);
    }

    await page.goto(url, { waitUntil: "networkidle2" });

    await new Promise((r) => setTimeout(r, 5000));

    await page.evaluate(() => {
      document.body.style.zoom = "45%";
      window.scrollTo(0, document.body.scrollHeight);
    });

    // await new Promise((r) => setTimeout(r, 200000)); //minutos?

    // const cookies = await page.cookies();
    // fs.writeFileSync(COOKIES_PATH, JSON.stringify(cookies, null, 2));
    // console.log("Cookies salvos!");
    //rafaeekw
    // let token = null;
    // let startDate = Date.now();
    // while (!token && Date.now() - startDate < 30000) {
    //   await page.click("#freeplay_form_cf_turnstile");
    //   token = await page.evaluate(() => {
    //     try {
    //       let item = document.querySelector(
    //         '[name="cf-turnstile-response"]'
    //       ).value;
    //       return item && item.length > 20 ? item : null;
    //     } catch (e) {
    //       return null;
    //     }
    //   });
    //   await new Promise((r) => setTimeout(r, 1000));
    // }

    // await new Promise((r) => setTimeout(r, 5000));

    // try {
    //   await page.waitForFunction(() => {
    //     const el = document.querySelector("#free_play_form_button");
    //     if (!el) return null;
    //     return el.style.display !== "none";
    //   });
    //   await new Promise((r) => setTimeout(r, 5000));
    //   await page.waitForSelector("#free_play_form_button", { visible: true });
    //   await page.click("#free_play_form_button", { visible: true });
    // } catch (e) {
    //   console.log("Botão ainda não está visível.");
    // }
    await new Promise((r) => setTimeout(r, 5000));
    await page.screenshot({ path: "screen.png" });
  } catch (error) {
    await page.screenshot({ path: "screen.png" });
    console.error(`Erro interno do servidor: ${error.message}`);
    await new Promise((r) => setTimeout(r, 5000));
    await cpick();
  } finally {
    await browser.close();
  }
};

cpick();
