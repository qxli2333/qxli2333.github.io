import urllib.request
import json
import urllib.parse
import os

# Using the token identified in the workspace
TOKEN = "csWmjqPU7bcKJ8GLoO6GW0aQqeBi9tG2oOQX8vMV"
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
ORCID = "0000-0003-3616-6486"

def get_ads_data(orcid):
    query = f'orcid:{orcid}'
    params = {
        'q': query,
        'fl': 'bibcode,title,citation_count,year,pub,author',
        'rows': 200,
        'sort': 'date desc'
    }
    encoded_params = urllib.parse.urlencode(params)
    search_url = f"https://api.adsabs.harvard.edu/v1/search/query?{encoded_params}"
    
    req = urllib.request.Request(search_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('response', {}).get('docs', [])
    except Exception as e:
        print(f"Error fetching data from ADS: {e}")
        return []

def calculate_stats(docs):
    total_citations = sum(doc.get('citation_count', 0) for doc in docs)
    
    # Calculate First Author Citations
    # Note: ADS authors are usually "Last, First"
    first_author_citations = 0
    for doc in docs:
        authors = doc.get('author', [])
        if authors and ("Li, Q" in authors[0] or "Li, q" in authors[0]):
            first_author_citations += doc.get('citation_count', 0)
            
    # Calculate H-index
    counts = sorted([doc.get('citation_count', 0) for doc in docs], reverse=True)
    h_index = 0
    for i, count in enumerate(counts):
        if count >= i + 1:
            h_index = i + 1
        else:
            break
            
    return {
        'total_citations': total_citations,
        'first_author_citations': first_author_citations,
        'h_index': h_index,
        'count': len(docs)
    }

if __name__ == "__main__":
    docs = get_ads_data(ORCID)
    stats = calculate_stats(docs)
    
    print(f"Total Citations: {stats['total_citations']}")
    print(f"First Author Citations: {stats['first_author_citations']}")
    print(f"H-index: {stats['h_index']}")
    print(f"Publication Count: {stats['count']}")
    
    # Save stats to a JSON file for the website generator to use
    stats_file = os.path.join(os.path.dirname(__file__), '../_data/pub_stats.yml')
    # Preserve existing stats if possible
    existing_stats = {}
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            for line in f:
                if ':' in line:
                    key, val = line.split(':', 1)
                    existing_stats[key.strip()] = val.strip()

    with open(stats_file, 'w') as f:
        # Restore existing counts if they are not the ones we just calculated
        f.write(f"total: {existing_stats.get('total', stats['count'])}\n")
        f.write(f"first_author: {existing_stats.get('first_author', '1')}\n")
        f.write(f"selected: {existing_stats.get('selected', '2')}\n")
        
        # New citation stats
        f.write(f"total_citations: {stats['total_citations']}\n")
        f.write(f"first_author_citations: {stats['first_author_citations']}\n")
        f.write(f"h_index: {stats['h_index']}\n")
        f.write(f"count_ads: {stats['count']}\n")
