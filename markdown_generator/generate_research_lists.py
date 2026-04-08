import os
import re

PUB_DIR = os.path.join(os.path.dirname(__file__), '../_publications')
PAGES_DIR = os.path.join(os.path.dirname(__file__), '../_pages')

bao_keywords = ['desi', 'bao', 'baryon acoustic', 'lyman alpha', 'lyensuremathalpha', 'ly$\\alpha$']
weak_lensing_keywords = ['weak gravitational lensing', 'weak lensing', 'unions', 'shear', 'lensing', '2dfis']
galaxy_evolution_keywords = ['active galactic nuclei', 'supermassive black holes', 'active galaxies', 'agn', 'black hole', 'halo mass-observable', 'radio agn', 'quiescence']

def load_publications():
    papers = []
    for f in os.listdir(PUB_DIR):
        if not f.endswith('.md'):
            continue
        
        content = open(os.path.join(PUB_DIR, f), 'r', encoding='utf-8').read()
        
        # Parse frontmatter
        title_match = re.search(r'^title:\s*\"([^\"]+)\"', content, re.MULTILINE)
        permalink_match = re.search(r'^permalink:\s*([^\n]+)', content, re.MULTILINE)
        date_match = re.search(r'^date:\s*([^\n]+)', content, re.MULTILINE)
        pub_type_match = re.search(r'^pub_type:\s*\'([^\']+)\'', content, re.MULTILINE)
        citation_match = re.search(r'^citation:\s*\'([^\']+)\'', content, re.MULTILINE)
        keywords_match = re.search(r'^keywords:\s*\"([^\"]+)\"', content, re.MULTILINE)
        
        if not title_match:
            continue
            
        title = title_match.group(1)
        permalink = permalink_match.group(1).strip() if permalink_match else ''
        date = date_match.group(1).strip() if date_match else '1900-01-01'
        pub_type = pub_type_match.group(1).strip() if pub_type_match else '3_other'
        citation = citation_match.group(1).strip() if citation_match else ''
        keywords = keywords_match.group(1).strip() if keywords_match else ''
        
        # Extract first author
        clean_citation = re.sub(r'<[^>]+>', '', citation).strip()
        first_author = clean_citation.split(',')[0].strip() if clean_citation else ''
        year = date.split('-')[0]
        
        # Combine title and keywords for topic matching
        search_text = (title + " " + keywords).lower()
        
        is_bao = any(k in search_text for k in bao_keywords)
        is_wl = any(k in search_text for k in weak_lensing_keywords)
        is_gal_evo = any(k in search_text for k in galaxy_evolution_keywords)
        
        sort_key = (0 if pub_type in ['1_first_author', '2_selected'] else 1, date)
        
        papers.append({
            'title': title,
            'permalink': permalink,
            'first_author': first_author,
            'year': year,
            'sort_key': sort_key,
            'is_bao': is_bao,
            'is_wl': is_wl,
            'is_gal_evo': is_gal_evo,
        })
        
    return papers

def format_list(papers, key):
    filtered = [p for p in papers if p[key]]
    
    # Sort by priority, then by date descending
    filtered.sort(key=lambda x: x['sort_key'][1], reverse=True)
    filtered.sort(key=lambda x: x['sort_key'][0])
    
    lines = []
    for p in filtered:
        link_text = f"{p['title']} - {p['first_author']} et al. ({p['year']})"
        lines.append(f"* [{link_text}]({p['permalink']})")
    
    return "\n".join(lines)

def update_page(page_file, new_list):
    page_path = os.path.join(PAGES_DIR, page_file)
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace everything between '## Relevant Publications' and '[**&larr; Back to Research Overview**](/research/)'
    pattern = re.compile(r'(## Relevant Publications\n)(.*?)(?=\n\[\*\*&larr; Back to Research Overview\*\*\]\(/research/\))', re.DOTALL)
    
    new_content = pattern.sub(r'\1' + new_list + '\n', content)
    
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Updated {page_file} successfully.")

if __name__ == "__main__":
    papers = load_publications()
    
    bao_list = format_list(papers, 'is_bao')
    wl_list = format_list(papers, 'is_wl')
    gal_evo_list = format_list(papers, 'is_gal_evo')
    
    update_page('research-bao.md', bao_list)
    update_page('research-weak-lensing.md', wl_list)
    update_page('research-galaxy-evolution.md', gal_evo_list)
