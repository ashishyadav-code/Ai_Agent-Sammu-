from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus
import time
import json
import threading
import sys
from ollama import chat

model = 'gpt-oss:120b-cloud'

class Loader:
    def __init__(self):
        self.running = False
        self.thread = None
        self.message = ""

    def _animate(self):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while self.running:
            sys.stdout.write(f"\r{frames[i % len(frames)]}  {self.message}   ")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def start(self, message):
        self.message = message
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop(self, final_msg=None):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r" + " " * 70 + "\r")
        sys.stdout.flush()
        if final_msg:
            print(final_msg)


class GoogleSession:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.loader = Loader()

    def _make_driver(self):
        """Driver banao - restart ke liye alag function"""
        options = Options()
        options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        service = Service(ChromeDriverManager(driver_version="146.0.7680.0").install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)  # ✅ Page load timeout - hang nahi karega
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        return driver

    def start(self):
        self.loader.start("🚀 Brave background mein start ho raha hai")
        self.driver = self._make_driver()
        self.wait = WebDriverWait(self.driver, 15)
        self.loader.stop("✅ Brave ready! Ab search karo\n")

    def _restart(self):
        """Browser crash hone pe restart karo"""
        print("🔄 Browser restart ho raha hai...")
        try:
            self.driver.quit()
        except:
            pass
        time.sleep(2)
        self.driver = self._make_driver()
        self.wait = WebDriverWait(self.driver, 15)
        print("✅ Browser restart ho gaya!\n")

    def search(self, query, retry=True):
        result = {
            "query": query,
            "ai_overview": None,
            "web_results": []
        }

        try:
            # ── SEARCH ──
            self.loader.start("🔍 Search ho raha hai")
            encoded_query = quote_plus(query)
            self.driver.get(f"https://www.google.com/search?q={encoded_query}&hl=en")
            self.wait.until(EC.presence_of_element_located((By.ID, "search")))
            time.sleep(3)
            self.loader.stop("✅ Search complete!")

            # ── AI OVERVIEW ──
            self.loader.start("🤖 AI Overview extract kar raha hai")
            ai_text = self.driver.execute_script("""
                var selectors = [
                    'div.IZ6rdc', 'div.wDYxhc', 'div.hgKElc',
                    'span.hgKElc', 'div.kno-rdesc span', 'div.yDYNvb',
                    'div.X5LH0c', 'div.LGOjhe', 'div.e24Myc',
                    "div[jsname='yEVEwb']", 'div.aixTof'
                ];
                for (var s of selectors) {
                    var el = document.querySelector(s);
                    if (el) {
                        var t = el.innerText.trim();
                        if (t.length > 80) return t;
                    }
                }
                return null;
            """)

            if ai_text:
                result["ai_overview"] = ai_text
                self.loader.stop("✅ AI Overview mil gaya!")
            else:
                self.loader.stop("⚠️  AI Overview nahi mila")

            # ── WEB RESULTS ──
            self.loader.start("🌐 Web results dhundh raha hai")
            for sel in ["div.tF2Cxc", "div.g"]:
                elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                count = 0
                for el in elements:
                    if count >= 2:
                        break
                    try:
                        title = el.find_element(By.CSS_SELECTOR, "h3").text.strip()
                        link = el.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                        if not title or not link or "google.com" in link:
                            continue

                        snippet = ""
                        for snip_sel in ["div.VwiC3b", "span.aCOpRe", "div.IsZvec"]:
                            try:
                                snippet = el.find_element(By.CSS_SELECTOR, snip_sel).text.strip()
                                if snippet:
                                    break
                            except:
                                continue

                        result["web_results"].append({
                            "title": title,
                            "link": link,
                            "snippet": snippet
                        })
                        count += 1
                    except:
                        continue
                if len(result["web_results"]) >= 2:
                    break

            self.loader.stop(f"✅ {len(result['web_results'])} web results mile!")

            # ── SAVE ──
            with open("result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.loader.stop(f"❌ Error: {str(e)[:100]}")

            # ✅ Auto restart - ek baar retry karo
            if retry:
                self._restart()
                return self.search(query, retry=False)  # Dobara try - sirf ek baar

        return result

    def stop(self):
        if self.driver:
            self.driver.quit()
            print("\n🔴 Browser band ho gaya. Bye!")


def print_result(data):
    print("\n" + "="*50)
    print(f"🔍 Query: {data['query']}")
    print("="*50)

    if data["ai_overview"]:
        print("\n🤖 AI Overview:")
        print(f"   {data['ai_overview'][:600]}")

    if data["web_results"]:
        print("\n📄 Snippets:")
        for i, r in enumerate(data["web_results"], 1):
            snippet = r["snippet"] if r["snippet"] else "Snippet nahi mila"
            print(f"\n  {i}. {snippet}")

    print("\n" + "─"*50)
    print("💾 result.json updated!")
    print("─"*50 + "\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("   🔎 Google Smart Search (Session Mode)")
    print("   💡 'exit' likho band karne ke liye")
    print("="*50 + "\n")

    session = GoogleSession()
    session.start()

    while True:
        query = input("📝 Query: ").strip()

        if not query:
            continue

        if query.lower() in ["exit", "quit", "band", "bye"]:
            session.stop()
            break

        data = session.search(query)
        print_result(data)

        message = [{
            "role": "system",
            "content": """You are an AI assistant that helps people find information.
You will be given a query and web search results.
Provide a concise summary in bullet points.
If there is no relevant information, say "No relevant information found"."""
        }]

        snippets = "\n".join([r["snippet"] for r in data["web_results"]])
        ai_context = data["ai_overview"] if data["ai_overview"] else ""

        message.append({"role": "user", "content": query})
        message.append({
            "role": "user",
            "content": f"AI Overview:\n{ai_context}\n\nWeb Results:\n{snippets}"
        })

        res = chat(model=model, messages=message)
        print(f"\n🔹 Summary: {res['message']['content']}")