import os
import yaml
import re

bao_papers = [
    "DESI DR2 results. I. Baryon acoustic oscillations from the Lyman alpha forest",
    "DESI DR2 results. II. Measurements of baryon acoustic oscillations and cosmological constraints",
    "Validation of the DESI DR2 measurements of baryon acoustic oscillations from galaxies and quasars",
    "Validation of the DESI DR2 Ly$\\alpha$ BAO analysis using synthetic datasets",
    "DESI DR2 reference mocks: clustering results from Uchuu-BGS and LRG",
    "Construction of the damped Ly$\\alpha$ absorber catalog for DESI DR2 Ly$\\alpha$ BAO",
    "Cosmological implications of DESI DR2 BAO measurements in light of the latest ACT DR6 CMB data",
    "Constraints on neutrino physics from DESI DR2 BAO and DR1 full shape",
    "Extended dark energy analysis using DESI DR2 BAO measurements",
    "The Compilation and Validation of the Spectroscopic Redshift Catalogs for the DESI-COSMOS and DESI-XMM-LSS Fields"
]

weak_lensing_papers = [
    "Point spread function errors for weak lensing - density cross-correlations: Application to UNIONS",
    "Testing Cotton gravity as dark matter substitute with weak lensing",
    "UNIONS: The Ultraviolet Near-infrared Optical Northern Survey",
    "CFHT MegaCam Two Deep Fields Imaging Survey (2DFIS) I: Overview",
    "Halo Mass-observable Proxy Scaling Relations and Their Dependencies on Galaxy and Group Properties",
    "Dark Matter Halos of Luminous Active Galactic Nuclei from Galaxy-Galaxy Lensing with the HSC Subaru Strategic Program"
]

galaxy_evolution_papers = [
    "Black Hole-Halo Mass Relation from UNIONS Weak Lensing",
    "Dark Matter Halos of Luminous Active Galactic Nuclei from Galaxy-Galaxy Lensing with the HSC Subaru Strategic Program",
    "Halo Mass-observable Proxy Scaling Relations and Their Dependencies on Galaxy and Group Properties",
    "Radio AGN feedback sustains quiescence only in a minority of massive galaxies"
]

def load_papers():
    papers = []
    pub_dir = '_publications'
    for filename in os.listdir(pub_dir):
        if not filename.endswith('.md'): continue
        filepath = os.path.join(pub_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter:
                        papers.append(frontmatter)
    return papers

papers = load_papers()

def normalize_title(title):
    return re.sub(r'[^a-zA-Z0-9]', '', title).lower()

paper_dict = {normalize_title(p['title']): p for p in papers}

def format_paper(title):
    norm_title = normalize_title(title)
    if norm_title in paper_dict:
        p = paper_dict[norm_title]
    else:
        # Fallback: exact match wasn't found due to special chars, try partial match
        p = next((x for x in papers if norm_title in normalize_title(x['title']) or normalize_title(x['title']) in norm_title), None)
        if not p:
            return None
            
    # Extract first author from citation
    citation = p.get('citation', '')
    first_author = ""
    if '<b>' in citation:
        first_author = citation.split('<b>')[1].split('</b>')[0].strip()
        if not first_author.startswith('Qinxun'):
            first_author = citation.split(',')[0].replace('<b>', '').replace('</b>', '').strip()
    else:
        first_author = citation.split(',')[0].strip()
    
    date = str(p.get('date', ''))
    year = date.split('-')[0] if date else ''
    
    pub_type = p.get('pub_type', '2_co_author')
    is_first_or_selected = (pub_type == '1_first_author') or ('Qinxun' in first_author)
    
    # Sort key: 0 if first author / selected, 1 if not. Then by date descending (negative timestamp trick or string reversed)
    sort_key = (0 if is_first_or_selected else 1, date)
    
    link_text = f"{p['title']} - {first_author} et al. ({year})"
    link = f"[{link_text}]({p['permalink']})"
    return {
        'sort_key': sort_key,
        'markdown': f"* {link}"
    }

def print_list(name, title_list):
    print(f"=== {name} ===")
    formatted = []
    for t in title_list:
        res = format_paper(t)
        if res:
            formatted.append(res)
    # Sort: group first (0 vs 1), then date descending
    formatted.sort(key=lambda x: (x['sort_key'][0], x['sort_key'][1]), reverse=True)
    # Actually we want sort_key[0] ascending (0 then 1), and sort_key[1] descending.
    formatted.sort(key=lambda x: (x['sort_key'][0], x['sort_key'][1]), reverse=True)
    # Wait, reverse=True makes sort_key[0] descending (1 then 0). We want 0 then 1.
    formatted.sort(key=lambda x: (x['sort_key'][0], "\xff"*(10-len(x['sort_key'][1])) + x['sort_key'][1] ), reverse=False)
    # Better: sort by date descending first, then stable sort by is_first ascending
    formatted.sort(key=lambda x: x['sort_key'][1], reverse=True)
    formatted.sort(key=lambda x: x['sort_key'][0])
    
    for f in formatted:
        print(f['markdown'])

print_list("BAO", bao_papers)
print_list("Weak Lensing", weak_lensing_papers)
print_list("Galaxy Evolution", galaxy_evolution_papers)
