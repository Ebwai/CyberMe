from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Inject stealth
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        def handle_response(response):
            if 'json' in response.headers.get('content-type', ''):
                print(f"JSON Response: {response.url}")
        
        page.on("response", handle_response)
        
        print("Navigating to Home...")
        page.goto("https://www.douyin.com/", wait_until="domcontentloaded")
        time.sleep(2)
        
        print("Navigating to Favorites...")
        page.goto("https://www.douyin.com/user/self?showTab=favorite_collection", wait_until="domcontentloaded")
        
        print("Scrolling...")
        page.evaluate("window.scrollTo(0, 1000)")
        time.sleep(5)
        
        browser.close()

if __name__ == "__main__":
    run()
