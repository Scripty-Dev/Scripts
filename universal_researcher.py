import sys
import json
import aiohttp
import asyncio
import feedparser
import re
from typing import List, Dict
from urllib.parse import quote

class UniversalResearcher:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def research(self, query: str) -> Dict:
        """Main research function"""
        try:
            print("Starting research for:", query)  # Debug line
            
            # Gather data from all sources
            results = await self._gather_all_sources(query)
            
            if not results:
                return {
                    'summary': "No results found. Please try refining your search.",
                    'key_points': [],
                    'sources': []
                }

            # Process results
            summary = self._create_summary(results)
            key_points = self._extract_key_points(results)
            sources = self._format_sources(results)

            return {
                'summary': summary,
                'key_points': key_points,
                'sources': sources
            }

        except Exception as e:
            print(f"Detailed error: {type(e).__name__}: {str(e)}")  # Debug line
            return {
                'summary': "An error occurred during research.",
                'key_points': [],
                'sources': [],
                'error': str(e)
            }

    async def _gather_all_sources(self, query: str) -> List[Dict]:
        """Gather information from all sources"""
        print("Gathering sources...")  # Debug line
        
        results = []
        
        # ArXiv search
        arxiv_results = await self._search_arxiv(query)
        if arxiv_results:
            results.extend(arxiv_results)
            print(f"Found {len(arxiv_results)} ArXiv results")  # Debug line

        # Wikipedia search
        wiki_results = await self._search_wikipedia(query)
        if wiki_results:
            results.extend(wiki_results)
            print(f"Found {len(wiki_results)} Wikipedia results")  # Debug line

        return results

    async def _search_arxiv(self, query: str) -> List[Dict]:
        """Search ArXiv for academic papers"""
        base_url = 'http://export.arxiv.org/api/query'
        
        try:
            async with self.session.get(f"{base_url}?search_query=all:{quote(query)}&start=0&max_results=5") as response:
                if response.status == 200:
                    feed = feedparser.parse(await response.text())
                    return [{
                        'title': entry.title,
                        'summary': self._clean_text(entry.summary),
                        'url': entry.link,
                        'source': 'arxiv'
                    } for entry in feed.entries]
        except Exception as e:
            print(f"ArXiv error: {str(e)}")
        return []

    async def _search_wikipedia(self, query: str) -> List[Dict]:
        """Search Wikipedia articles"""
        base_url = 'https://en.wikipedia.org/w/api.php'
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'utf8': 1,
            'srlimit': 5
        }
        
        try:
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [{
                        'title': result['title'],
                        'summary': self._clean_text(result.get('snippet', '')),
                        'url': f"https://en.wikipedia.org/?curid={result['pageid']}",
                        'source': 'wikipedia'
                    } for result in data['query']['search']]
        except Exception as e:
            print(f"Wikipedia error: {str(e)}")
        return []

    def _clean_text(self, text: str) -> str:
        """Clean and format text content"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters except basic punctuation
        text = re.sub(r'[^\w\s.!?,;:-]', '', text)
        return text.strip()

    def _create_summary(self, results: List[Dict]) -> str:
        """Create a summary from the results"""
        if not results:
            return "No relevant information found."
            
        # Combine summaries from the top 3 results
        summaries = []
        for result in results[:3]:
            if 'summary' in result and result['summary']:
                summaries.append(result['summary'])
                
        if not summaries:
            return "No summary available."
            
        return " ".join(summaries)

    def _extract_key_points(self, results: List[Dict]) -> List[str]:
        """Extract key points from results"""
        if not results:
            return []
            
        key_points = set()
        for result in results:
            if 'summary' in result and result['summary']:
                sentences = re.split(r'[.!?]+', result['summary'])
                for sentence in sentences:
                    clean_sentence = sentence.strip()
                    if len(clean_sentence.split()) > 5:  # Avoid very short sentences
                        key_points.add(clean_sentence)
                        
        return list(key_points)[:5]  # Return top 5 key points

    def _format_sources(self, results: List[Dict]) -> List[Dict]:
        """Format sources consistently"""
        sources = []
        for result in results:
            if all(key in result for key in ['title', 'url', 'source']):
                sources.append({
                    'title': result['title'],
                    'url': result['url'],
                    'source': result['source']
                })
        return sources

    async def close(self):
        """Close the session"""
        if not self.session.closed:
            await self.session.close()

# Export the function that will be called by the script agent
async def func(args):
    try:
        researcher = UniversalResearcher()
        try:
            results = await researcher.research(args['query'])
            return json.dumps(results)
        finally:
            await researcher.close()
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'summary': "An error occurred during research.",
            'key_points': [],
            'sources': []
        })

# Export the object that describes the function
object = {
    'name': 'universal_researcher',
    'description': 'Research a topic using multiple sources including ArXiv and Wikipedia. Returns a summary, key points, and sources.',
    'parameters': {
        'type': 'object',
        'properties': {
            'query': {
                'type': 'string',
                'description': 'The research query or topic to investigate'
            }
        },
        'required': ['query']
    }
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--metadata':
            # Return the metadata when requested
            print(json.dumps({'object': object}))
        else:
            # Normal execution with arguments
            with open(sys.argv[1], 'r') as f:
                args = json.load(f)
            
            # Run the async function
            result = asyncio.run(func(args))
            print(result)
