import os
import re
import html
import urllib.parse
import urllib.request
import json
from pybtex.database.input import bibtex

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
}

def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)

def clean_text(text):
    return text.replace("{", "").replace("}", "").replace("\\", "")

month_map = {
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
    'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
}

journal_map = {
    '\\prd': 'Physical Review D',
    '\\apj': 'Astrophysical Journal',
    '\\apjl': 'Astrophysical Journal Letters',
    '\\aap': 'Astronomy & Astrophysics',
    '\\aj': 'Astronomical Journal',
    'arXiv e-prints': 'arXiv e-prints',
    'Science China Physics, Mechanics, and Astronomy': 'Science China Physics, Mechanics, and Astronomy',
    'Astronomy \\& Astrophysics': 'Astronomy & Astrophysics'
}

TOKEN = "csWmjqPU7bcKJ8GLoO6GW0aQqeBi9tG2oOQX8vMV"
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}

def fetch_abstract_from_ads(bibcode):
    search_url = f"https://api.adsabs.harvard.edu/v1/search/query?q=bibcode:{urllib.parse.quote(bibcode)}&fl=abstract"
    req = urllib.request.Request(search_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            if docs:
                return docs[0].get('abstract', '')
    except Exception as e:
        print(f"Error fetching abstract for {bibcode}: {e}")
    return ""

# Resolve paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
bib_file = os.path.join(SCRIPT_DIR, "own-bib.bib")
out_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "_publications"))

parser = bibtex.Parser()
with open(bib_file, 'r', encoding='utf-8') as f:
    content = f.read()
clean_content = re.sub(r'(?m)^\s*%.*$', '', content)
bibdata = parser.parse_string(clean_content)

# Clear existing files
for f in os.listdir(out_dir):
    if f.endswith('.md'):
        os.remove(os.path.join(out_dir, f))

total_papers = 0
first_author_papers = 0
selected_papers = 0

for bib_id in bibdata.entries:
    entry = bibdata.entries[bib_id]
    b = entry.fields
    
    keywords = b.get("keywords", "").lower()
    total_papers += 1
    if "firstauthor" in keywords:
        first_author_papers += 1
    if "select" in keywords:
        selected_papers += 1
        
    pub_year = b.get("year", "1900")
    raw_month = b.get("month", "jan").lower()[:3]
    pub_month = month_map.get(raw_month, "01")
    pub_day = b.get("day", "01")
    if len(pub_day) == 1:
        pub_day = "0" + pub_day
        
    pub_date = f"{pub_year}-{pub_month}-{pub_day}"
    
    title = b.get("title", "")
    clean_title = clean_text(title)
    
    url_slug = re.sub(r"\[.*\]|[^a-zA-Z0-9_-]", "", clean_title.replace(" ", "-"))
    url_slug = re.sub(r"-+", "-", url_slug).strip("-")
    
    md_filename = f"{pub_date}-{url_slug}.md"
    html_filename = f"{pub_date}-{url_slug}"
    
    # Authors
    authors = entry.persons.get("author", [])
    author_str = ""
    for i, author in enumerate(authors):
        if i == 6:
            author_str += " et al."
            break
        first = clean_text(" ".join(author.first_names))
        last = clean_text(" ".join(author.last_names))
        author_str += f" {first} {last}, "
    if author_str.endswith(", "):
        author_str = author_str[:-2]
        
    # Venue
    raw_venue = b.get("journal", b.get("publisher", ""))
    clean_venue = clean_text(raw_venue)
    venue = journal_map.get(raw_venue, clean_venue)
    
    citation = f"{author_str} \"{clean_title}.\" {venue}, {pub_year}."
    
    # Extract Annotation and Abstract
    annotation = clean_text(b.get("annotation", ""))
    abstract = clean_text(b.get("abstract", ""))
    
    # Try fetching abstract from ADS if not found
    adsurl = b.get("adsurl", "")
    if not abstract and bib_id:
        abstract = fetch_abstract_from_ads(bib_id)
        
    if not abstract and adsurl:
        # Fallback to extract bibcode from adsurl
        m = re.search(r'abs/([^/]+)', adsurl)
        if m:
            extracted_bibcode = m.group(1)
            abstract = fetch_abstract_from_ads(extracted_bibcode)

    if abstract and isinstance(abstract, list):
        abstract = " ".join(abstract)

    md = f"---\n"
    md += f"title: \"{html_escape(clean_title)}\"\n"
    md += f"collection: publications\n"
    md += f"permalink: /publication/{html_filename}\n"
    md += f"date: {pub_date}\n"
    md += f"venue: '{html_escape(venue)}'\n"
    md += f"citation: '{html_escape(citation)}'\n"
    if annotation:
        md += f"annotation: '{html_escape(annotation)}'\n"
    md += f"---\n\n"
    
    if abstract:
        md += f"### Abstract\n{html_escape(abstract)}\n\n"
        
    if adsurl:
        md += f"[Access paper on ADS]({adsurl}){{:target=\"_blank\"}}\n"
    else:
        md += f"[Search on Google Scholar](https://scholar.google.com/scholar?q={urllib.parse.quote(clean_title)}){{:target=\"_blank\"}}\n"
        
    with open(os.path.join(out_dir, md_filename), "w") as f:
        f.write(md)

# Write stats
data_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "_data"))
os.makedirs(data_dir, exist_ok=True)
with open(os.path.join(data_dir, "pub_stats.yml"), "w") as f:
    f.write(f"total: {total_papers}\n")
    f.write(f"first_author: {first_author_papers}\n")
    f.write(f"selected: {selected_papers}\n")

print("Successfully updated publications with abstracts from ADS and generated stats!")
