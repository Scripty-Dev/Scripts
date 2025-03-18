import requests
import logging
import time
import json
import sys
import asyncio
import http.client

logging.basicConfig(level=logging.INFO)

async def search_with_serper(query):
    """
    Uses the Serper API to get Google search results in a clean JSON format.
    """
    try:
        # Connect to the Serper API
        conn = http.client.HTTPSConnection("google.serper.dev")
        
        # Prepare the payload with the query
        payload = json.dumps({
            "q": query
        })
        
        # Set headers including the API key
        headers = {
            'X-API-KEY': '0cde2022efed535909470fc4df4fb8e23985f9a9',
            'Content-Type': 'application/json'
        }
        
        # Make the request
        conn.request("POST", "/search", payload, headers)
        
        # Get the response
        response = conn.getresponse()
        data = response.read()
        
        # Parse the JSON response
        result = json.loads(data.decode("utf-8"))
        
        search_results = []
        
        # Extract knowledge graph information if available
        if "knowledgeGraph" in result:
            kg = result["knowledgeGraph"]
            search_results.append({
                'type': 'knowledge_graph',
                'title': kg.get('title', ''),
                'description': kg.get('description', ''),
                'source': 'Google Knowledge Graph',
                'url': kg.get('url', '')
            })
        
        # Extract answer box information if available
        if "answerBox" in result:
            answer_box = result["answerBox"]
            search_results.append({
                'type': 'answer_box',
                'title': answer_box.get('title', ''),
                'answer': answer_box.get('answer', ''),
                'snippet': answer_box.get('snippet', ''),
                'source': answer_box.get('source', 'Google'),
                'url': answer_box.get('link', '')
            })
        
        # Extract top organic results
        if "organic" in result:
            for index, item in enumerate(result["organic"][:3]):  # Get top 3 organic results
                search_results.append({
                    'type': 'organic',
                    'position': index + 1,
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'source': item.get('source', ''),
                    'url': item.get('link', '')
                })
        
        return search_results
    
    except Exception as e:
        return f"Error: {str(e)}"

async def func(args):
    try:
        search_query = args.get('query')
        if not search_query:
            return json.dumps({"error": "No search query provided"})

        results = {
            "message": f"Search results for: {search_query}",
            "results": []
        }

        search_results = await search_with_serper(search_query)
        if isinstance(search_results, list):
            results["results"] = search_results
        else:
            results["error"] = search_results

        return json.dumps(results)

    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "web_search",
    "description": "Search the web for information using Google via the Serper API. Returns relevant search results and extracts from answer boxes.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up"
            }
        },
        "required": ["query"]
    }
}
