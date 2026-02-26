import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from google import genai
import os

# --- UNIVERSAL CONFIG ---
API_KEY = "AIzaSyDTpPp1e9JYhgR9mAZ5cg7POAXJoKof3PU"
MODEL_ID = "gemini-3-flash-preview"  # 1.5-Flash is the stable version for 2026 free tier

# 1. CHANGE THIS TO ANY URL
TARGET_URL = "http://books.toscrape.com/" 

# 2. CHANGE THIS TO WHATEVER DATA YOU WANT
EXTRACTION_GOAL = "Extract all book titles and their prices."

client = genai.Client(api_key=API_KEY)

async def ai_extract_data(html_text, goal):
    print("🤖 AI is reading the page...")
    # Gemini 1.5 Flash has a huge window, but we keep it clean for speed
    clean_text = html_text[:5000] 
    
    prompt = (
        f"Goal: {goal} "
        "Format the output as a clean list with a pipe separator like this: Data1 | Data2. "
        "Do not include headers or conversation. "
        "Text to analyze: " + clean_text
    )

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text.strip().split('\n')
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return []

async def main():
    all_results = []
    
    async with async_playwright() as p:
        print(f"🌐 Opening Browser to: {TARGET_URL}")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(TARGET_URL, wait_until="networkidle")

        # Let's scrape 2 pages as a test
        for i in range(1, 3): 
            print(f"📄 Processing Page {i}...")
            
            # This grabs only the visible text so we don't waste AI tokens on code
            page_content = await page.evaluate("() => document.body.innerText")
            
            # Send to AI
            data_lines = await ai_extract_data(page_content, EXTRACTION_GOAL)
            
            for line in data_lines:
                if "|" in line:
                    all_results.append(line.split("|"))

            # Logic to find a "Next" button automatically
            next_button = page.get_by_text("next", exact=False).first
            if await next_button.is_visible():
                await next_button.click()
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2) 
            else:
                break

        await browser.close()

    # Save to CSV
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv("universal_scraped_data.csv", index=False)
        print(f"✅ SUCCESS! Saved to 'universal_scraped_data.csv'")
        print(df.head()) # Show a preview in terminal
    else:
        print("⚠️ No data found.")

if __name__ == "__main__":
    asyncio.run(main())