import os
import re
import html
import urllib.parse
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

for bib_id in bibdata.entries:
    entry = bibdata.entries[bib_id]
    b = entry.fields
    
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
    
    md = f"---\n"
    md += f"title: \"{html_escape(clean_title)}\"\n"
    md += f"collection: publications\n"
    md += f"permalink: /publication/{html_filename}\n"
    md += f"date: {pub_date}\n"
    md += f"venue: '{html_escape(venue)}'\n"
    md += f"citation: '{html_escape(citation)}'\n"
    md += f"---\n"
    
    adsurl = b.get("adsurl", "")
    if adsurl:
        md += f"Use [ADS link]({adsurl}){{:target=\"_blank\"}} for full citation and access paper\n"
    else:
        md += f"Use [Google Scholar](https://scholar.google.com/scholar?q={urllib.parse.quote(clean_title)}){{:target=\"_blank\"}} for full citation\n"
        
    with open(os.path.join(out_dir, md_filename), "w") as f:
        f.write(md)

print("Successfully updated publications!")
