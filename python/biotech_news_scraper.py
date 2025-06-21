import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import csv
from urllib.parse import urljoin, quote

class BiotechNewsCollector:
    def __init__(self):
        self.base_url = "https://news.google.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.biotech_keywords = [
            'biotech', 'biotechnology', 'biopharma', 'biopharmaceutical',
            'pharmaceutical', 'drug development', 'clinical trial',
            'FDA approval', 'gene therapy', 'immunotherapy', 'vaccine',
            'CRISPR', 'stem cell', 'protein', 'antibody', 'biosimilar'
        ]
    
    def search_biotech_news(self, keyword, max_results=20):
        """Search for biotech news using Google News search"""
        search_url = f"{self.base_url}/search?q={quote(keyword)}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Find article containers (Google News structure may vary)
            article_elements = soup.find_all('article') or soup.find_all('div', class_='xrnccd')
            
            for i, element in enumerate(article_elements[:max_results]):
                if i >= max_results:
                    break
                    
                article_data = self.extract_article_data(element)
                if article_data:
                    articles.append(article_data)
                    
            return articles
            
        except requests.RequestException as e:
            print(f"Error fetching news for keyword '{keyword}': {e}")
            return []
    
    def extract_article_data(self, element):
        """Extract article data from HTML element"""
        try:
            # Try to find title
            title_elem = (element.find('h3') or 
                         element.find('h4') or 
                         element.find('a', class_='DY5T1d'))
            title = title_elem.get_text(strip=True) if title_elem else "No title"
            
            # Try to find link
            link_elem = element.find('a')
            link = link_elem.get('href') if link_elem else None
            if link and link.startswith('./'):
                link = urljoin(self.base_url, link)
            
            # Try to find source
            source_elem = element.find('div', class_='vr1PYe') or element.find('span', class_='vr1PYe')
            source = source_elem.get_text(strip=True) if source_elem else "Unknown source"
            
            # Try to find timestamp
            time_elem = element.find('time') or element.find('div', class_='OSrXXb')
            timestamp = time_elem.get_text(strip=True) if time_elem else "Unknown time"
            
            # Try to find snippet/description
            snippet_elem = element.find('div', class_='GI74Re') or element.find('span', class_='xBjOHf')
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            return {
                'title': title,
                'link': link,
                'source': source,
                'timestamp': timestamp,
                'snippet': snippet,
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting article data: {e}")
            return None
    
    def collect_all_biotech_news(self, max_per_keyword=10):
        """Collect news for all biotech keywords"""
        all_articles = []
        
        for keyword in self.biotech_keywords:
            print(f"Searching for: {keyword}")
            articles = self.search_biotech_news(keyword, max_per_keyword)
            
            for article in articles:
                article['search_keyword'] = keyword
                all_articles.append(article)
            
            # Be respectful to the server
            time.sleep(1)
        
        # Remove duplicates based on title
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            if article['title'] not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(article['title'])
        
        return unique_articles
    
    def save_to_json(self, articles, filename='biotech_news.json'):
        """Save articles to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(articles)} articles to {filename}")
    
    def save_to_csv(self, articles, filename='biotech_news.csv'):
        """Save articles to CSV file"""
        if not articles:
            print("No articles to save")
            return
            
        fieldnames = ['title', 'link', 'source', 'timestamp', 'snippet', 'search_keyword', 'collected_at']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(articles)
        
        print(f"Saved {len(articles)} articles to {filename}")
    
    def print_articles(self, articles, limit=5):
        """Print articles to console"""
        for i, article in enumerate(articles[:limit]):
            print(f"\n--- Article {i+1} ---")
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Time: {article['timestamp']}")
            print(f"Keyword: {article.get('search_keyword', 'N/A')}")
            if article['snippet']:
                print(f"Snippet: {article['snippet'][:200]}...")
            if article['link']:
                print(f"Link: {article['link']}")

# Usage example
def main():
    collector = BiotechNewsCollector()
    
    print("Collecting biotech/biopharma news...")
    articles = collector.collect_all_biotech_news(max_per_keyword=5)
    
    print(f"\nCollected {len(articles)} unique articles")
    
    # Display first few articles
    collector.print_articles(articles, limit=3)
    
    # Save to files
    collector.save_to_json(articles)
    collector.save_to_csv(articles)
    
    return articles

if __name__ == "__main__":
    articles = main()
