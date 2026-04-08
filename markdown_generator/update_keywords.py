import os
import re
import urllib.parse
import urllib.request
import json
import time

TOKEN = "csWmjqPU7bcKJ8GLoO6GW0aQqeBi9tG2oOQX8vMV"
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}

def fetch_keywords_from_ads(bibcode):
    search_url = f"https://api.adsabs.harvard.edu/v1/search/query?q=bibcode:{urllib.parse.quote(bibcode)}&fl=keyword"
    req = urllib.request.Request(search_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            if docs:
                keywords = docs[0].get('keyword', [])
                if keywords:
                    return ", ".join(keywords)
    except Exception as e:
        print(f"Error fetching keywords for {bibcode}: {e}")
    return ""

def process_bib_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = re.compile(r'@([a-zA-Z]+)\s*\{\s*([^,]+),')
    matches = list(pattern.finditer(content))
    
    new_content = ""
    last_idx = 0
    for i, match in enumerate(matches):
        entry_start = match.start()
        entry_key = match.group(2).strip()
        
        next_idx = matches[i+1].start() if i+1 < len(matches) else len(content)
        entry_text = content[entry_start:next_idx]
        
        # Check for keywords that might actually be our custom types
        kw_match = re.search(r'keywords\s*=\s*\{([^\}]+)\}', entry_text, re.IGNORECASE)
        custom_tags = ["firstauthor", "select", "contributing", "own"]
        
        if kw_match:
            kw_val = kw_match.group(1).strip()
            # If the keyword is just one of our custom tags, rename it to own_type
            if kw_val.lower() in custom_tags:
                entry_text = entry_text[:kw_match.start()] + f"own_type = {{{kw_val}}}" + entry_text[kw_match.end():]
                # Re-check kw_match since we removed it
                kw_match = re.search(r'keywords\s*=\s*\{([^\}]+)\}', entry_text, re.IGNORECASE)
        
        # If the entry already has real keywords, we skip fetching
        if kw_match:
            new_content += content[last_idx:entry_start] + entry_text
            last_idx = next_idx
            continue
            
        # Check if there's an adsurl to extract bibcode
        adsurl_match = re.search(r'adsurl\s*=\s*[\{"]https?://ui\.adsabs\.harvard\.edu/abs/([^/\}"]+)[\}"]', entry_text)
        if adsurl_match:
            bibcode = adsurl_match.group(1)
        else:
            bibcode = entry_key
            
        print(f"Processing {entry_key} (bibcode: {bibcode}) for missing keywords...")
        
        # Fetch keywords if it looks like a bibcode
        new_keywords = ""
        if len(bibcode) >= 19 and bibcode[:4].isdigit():
            new_keywords = fetch_keywords_from_ads(bibcode)
            time.sleep(0.2) # rate limit
            
        if new_keywords:
            print(f"  Found keywords: {new_keywords[:50]}...")
            safe_kw = new_keywords.replace('{', '').replace('}', '')
            insert_str = f',\n    keywords = {{{safe_kw}}}'
            
            own_type_match = re.search(r'own_type\s*=\s*\{[^\}]+\}', entry_text)
            if own_type_match:
                end_pos = own_type_match.end()
                entry_text = entry_text[:end_pos] + insert_str + entry_text[end_pos:]
            else:
                last_brace = entry_text.rfind('}')
                if last_brace != -1:
                    entry_text = entry_text[:last_brace] + insert_str + '\n' + entry_text[last_brace:]

        new_content += content[last_idx:entry_start] + entry_text
        last_idx = next_idx
        
    new_content += content[last_idx:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    process_bib_file(os.path.join(os.path.dirname(__file__), "own-bib.bib"))
    print("Done updating keywords.")
