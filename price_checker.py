import sys
import json
import requests
from bs4 import BeautifulSoup
import asyncio
import logging
import time

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
                
            if link.startswith('/'):
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
            if link and link.startswith('/'):
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

async def func(args):
    """Main function to handle product searches"""
    try:
        if 'query' not in args:
            return json.dumps({
                "error": "Please provide a search query",
                "status": "error"
            })

        search_term = args['query']
        stores = args.get('stores', ['amazon', 'walmart'])
        results = {}

        if 'amazon' in stores:
            amazon_results = await get_amazon_products(search_term)
            results['amazon'] = amazon_results if isinstance(amazon_results, list) else []

        if 'walmart' in stores:
            walmart_results = await get_walmart_products(search_term)
            results['walmart'] = walmart_results if isinstance(walmart_results, list) else []

        # Find cheapest and most reviewed products
        cheapest_product = None
        most_reviewed = None
        min_price = float('inf')
        max_reviews = 0

        for store, products in results.items():
            for product in products:
                # Check for cheapest product
                try:
                    price_str = product['price']
                    if price_str != 'Price not available':
                        price = float(price_str.replace('

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })

# Object definition for the assistant framework
object = {
    "name": "priceCheck",
    "description": "Search for product prices across multiple stores. Format: {\"query\": string, \"stores\": [string]} where stores is optional and can include 'amazon' and/or 'walmart'",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Product search query"
            },
            "stores": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["amazon", "walmart"]
                },
                "description": "List of stores to search (default: all stores)"
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
                print(json.dumps({
                    "error": str(e),
                    "status": "error"
                }))
, '').replace(',', ''))
                        if price < min_price:
                            min_price = price
                            cheapest_product = {'store': store, **product}
                except:
                    continue

                # Check for most reviewed
                try:
                    rating = product['rating']
                    if 'out of' in rating.lower():
                        num_reviews = int(''.join(filter(str.isdigit, rating.split('out of')[0])))
                        if num_reviews > max_reviews:
                            max_reviews = num_reviews
                            most_reviewed = {'store': store, **product}
                except:
                    continue

        return json.dumps({
            "results": results,
            "cheapest_product": cheapest_product,
            "most_reviewed": most_reviewed,
            "status": "success"
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })

# Object definition for the assistant framework
object = {
    "name": "priceCheck",
    "description": "Search for product prices across multiple stores. Format: {\"query\": string, \"stores\": [string]} where stores is optional and can include 'amazon' and/or 'walmart'",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Product search query"
            },
            "stores": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["amazon", "walmart"]
                },
                "description": "List of stores to search (default: all stores)"
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
                print(json.dumps({
                    "error": str(e),
                    "status": "error"
                }))
