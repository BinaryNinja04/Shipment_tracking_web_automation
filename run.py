import asyncio
from playwright.async_api import async_playwright
import spacy
import re
import json
import os

CACHE_FILE = "cache.json"

nlp = spacy.load("en_core_web_sm")

def extract_container_number(prompt):
    doc = nlp(prompt)
    for token in doc:
        match = re.match(r"(SINI|HMMU|MAEU|MSKU|TEMU|TGHU|OOLU)\d{7,8}", token.text)
        if match:
            return match.group()
    return None

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache_data, f, indent=2)

NO_DATA_PATTERNS = [
    "no information", "no records", "not found", "no tracking data",
    "no result", "invalid container", "please enter", "nothing found"
]

def is_tracking_info_missing(text):
    lowered = text.lower()
    return any(phrase in lowered for phrase in NO_DATA_PATTERNS) or len(text.strip()) < 50

async def handle_hmm_tracking(page, container_number):
    print(" Searching for popup...")
    try:
        close_button = await page.wait_for_selector("button:has-text('Close')", timeout=5000)
        await close_button.click()
        print("❌ Closed popup.")
    except:
        print("ℹ️ No popup detected.")

    iframe = await page.query_selector("iframe")
    if iframe:
        print(" Found iframe. Switching context to iframe.")
        page = await iframe.content_frame()
    else:
        print("ℹ️ No iframe found. Continuing on main page.")

    print(" Locating 'Track & Trace' section...")
    track_trace_section = page.locator("text=Track & Trace").locator("..").locator("..")

    print(" Selecting 'Container No.' from dropdown...")
    await track_trace_section.locator("select").nth(0).select_option(label="Container No.")

    print(f" Entering container number: {container_number}")
    await track_trace_section.locator("input").fill(container_number)

    print(" Clicking 'Retrieve' button...")
    await track_trace_section.locator("button:has-text('Retrieve')").click()

    await page.wait_for_timeout(10000)
    result_html = await page.content()
    print("\n---- HMM TRACKING PAGE HTML ----\n")
    print(result_html[:1000])
    print("\n---- END ----\n")

    return result_html

async def main():
    user_input = input("\n  Enter your request (e.g., 'Get tracking info for HMM booking ID SINI25432400'): ")
    print("\n Using spaCy to extract the container number...")

    cache = load_cache()

    if user_input in cache:
        print(f"Retrieved from cache for container: {cache[user_input]['container_number']}")
        print("\n---- CACHED RESULT ----\n")
        print(cache[user_input]["result"])
        print("\n---- END ----\n")
        return
    
    container_number = extract_container_number(user_input)

    if not container_number:
        print("⚠️ Could not find a valid container number in the input.")
        return

    print(f" Container number extracted: {container_number}\n")

    print(" Launching browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print(" Opening SeaCargoTracking website...")
        await page.goto("http://www.seacargotracking.net")

        print(" Finding input fields...")
        inputs = await page.query_selector_all("input")
        print(f"Found {len(inputs)} input fields")

        print(" Filling container number...")
        await inputs[0].fill(container_number)

        print(" Clicking Search button...")
        await inputs[1].click()

        print(" Waiting 6 seconds for any redirection to start...")
        await asyncio.sleep(6)

        all_pages = context.pages
        if len(all_pages) > 1:
            redirected_page = all_pages[-1]
            print(" Detected new page after delay.")
        else:
            redirected_page = page
            print("⚠️ No new tab detected; using the same page.")

        print(" Waiting for redirected tab to load...")
        await redirected_page.wait_for_load_state()

        print(" Waiting for intermediate redirection page...")
        body_text = await redirected_page.inner_text("body")
        print("\n---- TRACKING INFO ----\n")
        print(body_text)
        print("\n---- END ----\n")

        if "CLICK HERE" in body_text:
            print(" Clicking 'CLICK HERE' link to go to carrier site...")
            click_link = await redirected_page.wait_for_selector("a:has-text('CLICK HERE')")
            async with context.expect_page() as carrier_page_info:
                await click_link.click()
            carrier_page = await carrier_page_info.value
        else:
            print("⚠️ 'CLICK HERE' link not found, staying on same page.")
            carrier_page = redirected_page

        await carrier_page.wait_for_load_state("load")
        current_url = carrier_page.url
        print(f" Current URL after redirection: {current_url}")

        result_text = ""
        if "hmm21" in current_url:
            print(" Detected HMM site. Proceeding with HMM tracking flow...")
            result_text = await handle_hmm_tracking(carrier_page, container_number)
        else:
            print(" Trying to read iframe if available...")
            iframe = await carrier_page.query_selector("iframe")
            if iframe:
                frame = await iframe.content_frame()
                await frame.wait_for_load_state()
                result_text = await frame.inner_text("body")
            else:
                print("⚠️ Iframe not found.")
                result_text = await carrier_page.content()

        cache[user_input] = {
            "container_number": container_number,
            "result": result_text.strip()
        }
        save_cache(cache)

        log = {
            "query": user_input,
            "action": "hmm_flow" if "hmm21" in current_url else "iframe_flow",
            "container_found": container_number
        }
        with open("ai_decision_log.json", "a") as f:
            f.write(json.dumps(log) + "\n")

        if is_tracking_info_missing(result_text):
            print("⚠️ No tracking info found or unrecognized format.")
        else:
            print("✅ Tracking information retrieved successfully.")

        await browser.close()

# Run the script
asyncio.run(main())