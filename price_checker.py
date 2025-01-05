import requests
from bs4 import BeautifulSoup
import logging
import time
import json
import sys
import asyncio
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)

def wait_and_find(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except:
        return None

def wait_and_find_all(driver, by, value, timeout=10):
    try:
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
        return elements
    except:
        return []

logging.basicConfig(level=logging.INFO)

async def get_amazon_products(search_term):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    url = f'https://www.amazon.com/s?k={search_term.replace(" ", "+")}'
    
    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        time.sleep(1)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        for index in ['2', '3', '4']:
            item = soup.find('div', {'data-index': index})
            if not item:
                continue

            title_link = item.find('a', {'class': 's-line-clamp-2'})
            if not title_link:
                continue
                
            h2 = title_link.find('h2')
            if not h2:
                continue
                
            title = h2.get('aria-label')
            link = title_link.get('href')
            if not title or not link:
                continue
                
            if not link.startswith('http'):
                link = f"https://www.amazon.com{link}"

            reviews_block = item.find('div', {'data-cy': 'reviews-block'})
            rating_text = 'No rating'
            if reviews_block:
                rating = reviews_block.find('a', {'aria-label': True})
                if rating and rating.get('aria-label'):
                    rating_text = rating['aria-label'].split(',')[0]

            price_span = item.find('span', {'class': 'a-price'})
            if price_span:
                price = price_span.find('span', {'class': 'a-offscreen'}).text
            else:
                secondary_offer = item.find('div', {'data-cy': 'secondary-offer-recipe'})
                if secondary_offer:
                    price_text = secondary_offer.find('span', text=lambda t: t and '$' in t)
                    price = price_text.text.strip() if price_text else 'Price not available'
                else:
                    price = 'Price not available'

            products.append({
                'title': title,
                'price': price,
                'rating': rating_text,
                'url': link
            })

        return products

    except Exception as e:
        return f"Error: {str(e)}"

async def get_walmart_products(search_term):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    url = f'https://www.walmart.com/search?q={search_term.replace(" ", "+")}'
    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        time.sleep(1)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        items = soup.find_all('div', {'role': 'group'})[:3]
        
        for item in items:
            link_elem = item.find('a')
            if not link_elem:
                continue
                
            title_span = link_elem.find('span')
            if not title_span:
                continue
                
            title = title_span.text.strip()
            link = link_elem.get('href')
            if not link:
                continue
                
            if not link.startswith('http'):
                link = f"https://www.walmart.com{link}"
                
            price_div = item.find('div', {'data-automation-id': 'product-price'})
            if price_div and price_div.find('div'):
                price = price_div.find('div').text.strip()
                price = price.replace('Now ', '').replace('now ', '')
                if 'now' in price.lower():
                    price = ''.join(c for c in price if c.isdigit() or c == '$')
                if price.startswith('$') and '.' not in price:
                    dollars = price[1:-2]
                    cents = price[-2:]
                    price = f"${dollars}.{cents}"
            else:
                price = 'Price not available'

            reviews_span = item.find('span', {'data-testid': 'product-reviews'})
            rating = 'No rating'
            if reviews_span:
                stars_span = reviews_span.find_next_sibling('span')
                if stars_span:
                    rating = f"{stars_span.text}"
                    
            products.append({
                'title': title,
                'price': price,
                'rating': rating,
                'url': link
            })
            
        return products
        
    except Exception as e:
        return f"Error: {str(e)}"

async def get_costco_products(search_term):
    options = uc.ChromeOptions()
    options.headless = True
    
    options.add_argument('--disable-http2')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--disable-notifications')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--enable-javascript')
    
    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        url = f'https://www.costco.ca/s?langId=-24&keyword={search_term.replace(" ", "+")}'
        
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(1)  # Consistent with other functions' delay
            
            # Accept cookies if present
            cookie_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
            )
            if cookie_button:
                cookie_button.click()
            
            products = []
            product_tiles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid^="ProductTile_"]'))
            )
            
            for tile in product_tiles[:3]:  # Consistent with other functions' limit
                try:
                    link_elem = tile.find_element(By.CSS_SELECTOR, 'a[data-testid="Link"]')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get_attribute('href')
                    title_span = link_elem.find_element(By.TAG_NAME, 'span')
                    title = title_span.text if title_span else None
                    
                    price = 'Price not available'
                    price_elem = tile.find_element(By.CSS_SELECTOR, '[data-testid^="Text_Price_"]')
                    if price_elem:
                        price = price_elem.text
                    
                    rating = 'No rating'
                    rating_div = tile.find_element(By.CSS_SELECTOR, '[role="img"][aria-label*="rating"]')
                    if rating_div:
                        rating_text = rating_div.get_attribute('aria-label')
                        if 'out of 5 stars' in rating_text:
                            rating = rating_text.split('Average rating is ')[1].split(' stars')[0] + ' stars'

                    if title and url:
                        products.append({
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'url': url
                        })

                except Exception:
                    continue

            return products

        except Exception as e:
            return f"Error: {str(e)}"
            
    except Exception as e:
        return f"Error: {str(e)}"
        
    finally:
        driver.quit()
        
async def func(args):
    try:
        search_term = args.get('query')
        if not search_term:
            return json.dumps({"error": "No search query provided"})

        results = {
            "message": f"Search results for: {search_term}",
            "results": []
        }

        amazon_results = await get_amazon_products(search_term)
        if isinstance(amazon_results, list):
            for product in amazon_results:
                results["results"].append({
                    "store": "Amazon",
                    **product
                })

        walmart_results = await get_walmart_products(search_term)
        if isinstance(walmart_results, list):
            for product in walmart_results:
                results["results"].append({
                    "store": "Walmart",
                    **product
                })

        costco_results = await get_costco_products(search_term)
        if isinstance(costco_results, list):
            for product in costco_results:
                results["results"].append({
                    "store": "Costco",
                    **product
                })

        return json.dumps(results)

    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "price_checker",
    "description": "Search for product prices on Amazon and Walmart. Provide all the links to the user as well.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Product to search for"
            }
        },
        "required": ["query"]
    }
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-exports':
            print(json.dumps({"object": object}))
        else:
            try:
                args = json.loads(sys.argv[1])
                result = asyncio.run(func(args))
                print(result)
            except Exception as e:
                print(json.dumps({"error": str(e)}))
