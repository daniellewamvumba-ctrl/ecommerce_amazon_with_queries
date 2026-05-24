import asyncio
import csv
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import random
import os
import sys


csv_file="amazon_multipage.csv"
headers=["Title","Price","Reviews","Ratings"]
pages_before_IP_reset=5
max_pages_per_query=10
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
]
queries=["smartphones","smartphones under 500","best smartphones 2024","latest smartphones","top rated smartphones"]
#scrolling function
async def scroll_to_bottom(page):
    for i in range(8):
        scroll_amount=random.randint(700,900)
        await page.mouse.wheel(0,scroll_amount)
        await asyncio.sleep(random.uniform(4,6))
        await human_error_simulation(page)
        await random_delay("short")
        await human_hover(page)
        await mouse_moves(page)

#human hover function
async def human_hover(page):
    """Finds a random product and hovers over it to mimic interest"""
    try:
        products = await page.locator("div[data-component-type='s-search-result']").all()
        if products:
            target = random.choice(products)
            await target.hover()
            await asyncio.sleep(random.uniform(0.5, 2.0))
    except:
        pass

    

#Mouse moves function
async def mouse_moves(page):
    viewport=page.viewport_size
    if viewport:
        height=viewport["height"]
        width=viewport["width"]
        x=random.randint(0,width)
        y=random.randint(0,height)
        await page.mouse.move(x,y,steps=random.randint(15,30))

#Save to csv function
async def save_to_csv(data):
    file_exist=os.path.isfile(csv_file)
    with open(csv_file,mode="a",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=headers)
        if not file_exist:
            writer.writeheader()
        writer.writerow(data)

#Typing like a human function
async def typing_function(element,text):
    for char in text:
        await element.type(char,delay=random.randint(50,200))
        if random.random()<0.05:
            await asyncio.sleep(random.uniform(0.1,0.3))

#Scrape details of products
async def scrape_details(products):
    for index,product in enumerate(products):
        try:
            title_element=product.locator("h2").first
            title=await title_element.inner_text() if await title_element.count()>0 else "N/A"
        except Exception as e:
            print(f"Could not extract title for item {index}: due to {e}")
            title="N/A"
        try:
            price_element=product.locator(".a-price-whole").first
            price=await price_element.inner_text() if await price_element.count()>0 else "N/A"
        except Exception as e:
            print(f"Could not extract price for item {index}: due to {e}")
            price="N/A"
        try:
            reviews_element=product.locator(".a-size-small .a-link-normal").first
            reviews=await reviews_element.inner_text() if await reviews_element.count()>0 else "N/A"
        except Exception as e:
            print(f"Could not extract reviews for item {index}: due to {e}")
            reviews="N/A"
        try:
            rating_element=product.locator(".a-icon-alt").first
            rating=await rating_element.inner_text() if await rating_element.count()>0 else "N/A"
        except Exception as e:
            print(f"Could not extract rating for item {index}: due to {e}")
            rating="N/A"
        data={"Title":title,"Price":price,"Reviews":reviews,"Ratings":rating}
        await save_to_csv(data)
        if index%5==0:
            await mouse_moves(product.page)
            await human_hover(product.page)
            await asyncio.sleep(random.uniform(2,4))
            print(f"Scraped item {index+1}: {title}")

#The delay function to mimic human behavior
async def human_error_simulation(page):
    """Occasionally clicks a random link and immediately goes back"""
    if random.random() < 0.03: # 3% chance
        try:
            links = await page.locator("a").all()
            random_link = random.choice(links)
            if await random_link.is_visible():
                await random_link.click()
                await asyncio.sleep(random.uniform(1, 3))
                await page.go_back()
                print("Simulated a 'misclick' and went back.")
        except:
            pass

#Distraction function to mimic user getting distracted
async def random_distraction():
    """Simulates the user being distracted for a while"""
    if random.random() < 0.05: # 5% chance
        long_pause = random.uniform(30, 90)
        print(f"Simulating distraction: Pausing for {int(long_pause)}s...")
        await asyncio.sleep(long_pause)

#Rndom delay function to mimic human behavior
async def random_delay(type="short"):
    if type == "short":
        # Quick actions like clicking a button
        await asyncio.sleep(random.uniform(1.2, 3.5))
    elif type == "medium":
        # Reading a product title/price
        await asyncio.sleep(random.uniform(4.0, 8.0))
    elif type == "long":
        # Mimicking "reading" the page or a context switch
        await asyncio.sleep(random.uniform(10.0, 25.0))

async def wait_for_ip_reset(current_page):
    """Pauses the script so you can toggle Airplane Mode on your phone"""
    print(f"\n{'!'*30}")
    print(f"IP ROTATION REQUIRED at Page {current_page}")
    print("1. Toggle Airplane Mode ON/OFF on your phone.")
    print("2. Ensure your computer re-connects to the Hotspot.")
    print("3. Press ENTER to resume scraping...")
    print(f"{'!'*30}\n")
    # This waits for user input in the terminal
    await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)


#The main function to run the scraper applying all the above functions
async def scrape_amazon():
    stealth_engine = Stealth()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        for query in queries:
            current_page = 1
            context = None
            
            while current_page <= max_pages_per_query:
                # 1. Identity & IP Management
                if context is None or (current_page - 1) % pages_before_IP_reset == 0:
                    if context:
                        await context.close()
                        # The "Mobile Hotspot" Pause
                        print(f"\n[ACTION REQUIRED] Resetting IP for {query} at Page {current_page}")
                        await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                    context = await browser.new_context(
                        user_agent=random.choice(USER_AGENTS),
                        viewport={'width': 1920 + random.randint(-50, 50), 'height': 1080 + random.randint(-50, 50)}
                    )
                    await stealth_engine.apply_stealth_async(context)
                    page = await context.new_page()
                    
                    # Navigation: Home -> Type (Page 1) OR Direct Jump (Page 6, 11, etc)
                    if current_page == 1:
                        await page.goto("https://www.amazon.com", wait_until="domcontentloaded")
                    
                        search_box = page.locator("#twotabsearchtextbox")
                        await typing_function(search_box, query)
                        await page.keyboard.press("Enter")
                        await random_delay("medium")
                        await human_hover(page)
                        await mouse_moves(page)
                    else:
                        await page.goto(f"https://www.amazon.com/s?k={query}&page={current_page}")

                # 2. Random Distractions (The Human Touch)
                if random.random() < 0.1: # 10% chance to just sit there for 45s
                    print("Simulating 'coffee break'...")
                    await random_distraction()
                    

                # 3. Scraping & Scrolling
                await page.wait_for_selector("div[data-component-type='s-search-result']")
                await scroll_to_bottom(page)
                await random_delay("medium")
                
                products = await page.locator("div[data-component-type='s-search-result']").all()
                await scrape_details(products)
                
                # 4. Pagination
                if current_page % pages_before_IP_reset != 0:
                    next_btn = page.locator("a.s-pagination-next")
                    if await next_btn.is_visible():
                        await next_btn.click()
                        current_page += 1
                        await random_delay("long")
                    else: break
                else:
                    current_page += 1
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_amazon())



    

