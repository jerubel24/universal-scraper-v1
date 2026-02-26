import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from google import genai
from dotenv import load_dotenv
# --- 1. NEW SECURE CONFIG ---
load_dotenv() 
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: API Key not found in .env. Please check the file.")

client = genai.Client(api_key=API_KEY)

async def ai_extract_data(html_text):
    print("🤖 Processing with Gemini 2.0 Flash...")
    try:
        # Improved prompt for better CSV formatting
        prompt = (
            "Extract book titles and prices from this text. "
            "Return ONLY the data in this exact format: Title | Price. "
            "One book per line.\n\n"
            f"TEXT: {html_text[:5000]}"
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text.strip().split('\n')
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return []

async def main():
    all_books = []
    async with async_playwright() as p:
        print("🌐 Launching Browser...")
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()
        
        url = "http://books.toscrape.com/"
        print(f"🚀 Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page_content = await page.evaluate("() => document.body.innerText")
            data_lines = await ai_extract_data(page_content)
            
            for line in data_lines:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 2:
                        all_books.append(parts)
            print(f"✅ Found {len(all_books)} items.")
        except Exception as e:
            print(f"❌ Browser Error: {e}")
        await browser.close()

    if all_books:
        df = pd.DataFrame(all_books, columns=["Title", "Price"])
        df.to_csv("scraped_results.csv", index=False)
        print("📁 Saved to scraped_results.csv")

if __name__ == "__main__":
    asyncio.run(main())