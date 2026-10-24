#!/usr/bin/env python3
"""Build a portable static site using only Python's standard library."""
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin
from datetime import datetime, timezone
from email.utils import format_datetime
import json, re, posixpath, shutil, hashlib

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs'
META = json.loads((ROOT / 'content/pages.json').read_text())
HOME = json.loads((ROOT / 'source/home.json').read_text())
ORIGIN = 'https://nathancheng.xyz'

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
def text(html):
    p = Text(); p.feed(html)
    return re.sub(r'\s+', ' ', ''.join(p.parts)).strip()
def relative(target, route):
    path = posixpath.relpath(target.strip('/') or '.', route.strip('/') or '.')
    return path + ('/' if target.endswith('/') and path != '.' else '')
def localize(html, route):
    return sanitize(html, lambda target: relative(target, route))
def write(route, html):
    dest = OUT / route.strip('/') / 'index.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
from presentation import shell, meta_line, listing, homepage, post_footer, category_listing
from sanitize_content import sanitize

# Only audited, rebuilt assets may enter the published directory.
audit_path = ROOT/'source/asset-audit.json'
if not audit_path.is_file():
    raise SystemExit('Prepare the four assets with prepare_assets.py before building this draft.')
asset_report = json.loads(audit_path.read_text())
for name in ['hero.png','avatar.png','portrait.jpg','nathan-serif.woff']:
    path = ROOT/'assets'/name
    assert path.is_file(), f'Missing sanitized asset: {name}'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == asset_report['assets'][name]['output_sha256'], f'Asset changed since audit: {name}'

OUT.mkdir(exist_ok=True)
asset_names = {'style.css','site.js','favicon.svg','FONT-LICENSE.txt','hero.png','avatar.png','portrait.jpg','nathan-serif.woff'}
assert {p.name for p in (ROOT/'assets').iterdir() if p.is_file()} == asset_names, 'Unexpected asset file'
(OUT/'assets').mkdir(exist_ok=True)
for name in asset_names:
    shutil.copy2(ROOT/'assets'/name, OUT/'assets'/name)
expected = {p['slug']:p['content']['rendered'] for kind in ['posts','pages'] for p in json.loads((ROOT/'source'/f'{kind}.json').read_text())}
report = []
search = []
for item in META:
    route = '/' + item['slug'] + '/'
    original = (ROOT/'content'/f'{item["slug"]}.html').read_text()
    rendered = localize(original, route)
    assert text(original) == text(rendered), f'Text changed: {route}'
    assert text(expected[item['slug']]) == text(rendered), f'Source text mismatch: {route}'
    toc = ''
    if item['slug'] in ('ride-along-compressing-a-biology-undergrad-into-1-year','who-is-the-most-handsome-asian-guy-in-toronto-nathan-cheng'):
        sections = []
        def heading(m):
            anchor = 'section-' + str(len(sections)+1)
            sections.append((anchor,text(m.group(1))))
            return '<h2 id="'+anchor+'">'+m.group(1)+'</h2>'
        rendered = re.sub(r'<h2>(.*?)</h2>',heading,rendered,flags=re.S)
        toc = '<nav class="table-of-contents" aria-label="Table of Contents"><h2>Table of Contents</h2><ol>'+''.join('<li><a href="#'+anchor+'">'+escape(title)+'</a></li>' for anchor,title in sections)+'</ol></nav>'
    title = unescape(item['title']['rendered'])
    body = f'<article class="article {item["type"]}"><header class="article-heading"><h1 class="article-title">{escape(title)}</h1>'
    if item['type'] == 'post':
        body += meta_line(item, route)
    body += f'</header>{toc}<div class="prose" data-original-content>{rendered}</div>'
    if item['type'] == 'post':
        body += post_footer(item, route)
    body += '</article>'
    write(route, shell(title, route, body, text(original)[:180]))
    report.append({'path':route,'text_matches_source':True,'text_sha256':hashlib.sha256(text(rendered).encode()).hexdigest(),'characters':len(text(rendered))})
    search.append({'title':title,'path':route,'text':text(original)})

featured = next(i for i in META if i['slug']=='about-me')
featured_html = (ROOT/'content/about-me.html').read_text()
assert text(HOME['content']) == text(featured_html), 'Homepage differs from the featured post'
home = homepage(featured, localize(featured_html,'/'))
write('/', shell('Nathan Cheng', '/', home))

archives = []
for kind, prefix, key in [('categories','category','categories'),('tags','tag','tags')]:
    for term in json.loads((ROOT/'source'/f'{kind}.json').read_text()):
        route = f'/{prefix}/{term["slug"]}/'
        body = f'<section class="archive"><header class="archive-heading"><p class="widget-label">{escape(prefix.title())}</p><h1>{escape(term["name"])}</h1></header>{listing([i for i in META if term["id"] in i.get(key,[])],route)}</section>'
        if kind == 'categories':
            body = category_listing([i for i in META if term['id'] in i.get(key,[])], term['name'], route)
        write(route,shell(term['name'],route,body)); archives.append(route)
route = '/author/nathan/'
write(route,shell('Nathan Cheng',route,f'<section class="archive"><header class="archive-heading"><p class="widget-label">Author</p><h1>Nathan Cheng</h1><p>{escape(HOME["author"].strip())}</p></header>{listing([i for i in META if i["type"]=="post"],route)}</section>')); archives.append(route)
route = '/author/admin/'
write(route,shell('Admin',route,'<section class="archive"><header class="archive-heading"><p class="widget-label">Author</p><h1>Admin</h1><p>0 posts</p></header><p class="empty-archive">It seems we cannot find what you are looking for. Perhaps searching can help.</p></section>')); archives.append(route)

# The browser search works without a server, network API, or dependencies.
(OUT/'assets/search-data.js').write_text('window.SITE_SEARCH = '+json.dumps(search,ensure_ascii=False).replace('</','<\\/')+';\n')
(OUT/'.nojekyll').write_text('')
routes = ['/'] + ['/'+i['slug']+'/' for i in META] + archives
def sitemap(paths): return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+ORIGIN+p+'</loc></url>' for p in paths)+'</urlset>\n'
(OUT/'sitemap.xml').write_text(sitemap(routes))
for kind, filename in [('post','post-sitemap.xml'),('page','page-sitemap.xml')]:
    (OUT/filename).write_text(sitemap(['/']+['/'+i['slug']+'/' for i in META if i['type']==kind]))
for prefix, filename in [('category','category-sitemap.xml'),('tag','post_tag-sitemap.xml'),('author','author-sitemap.xml')]:
    (OUT/filename).write_text(sitemap([p for p in archives if p.startswith('/'+prefix+'/')]))
sitemap_files = ['post-sitemap.xml','page-sitemap.xml','category-sitemap.xml','post_tag-sitemap.xml','author-sitemap.xml']
(OUT/'sitemap_index.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<sitemap><loc>'+ORIGIN+'/'+name+'</loc></sitemap>' for name in sitemap_files)+'</sitemapindex>\n')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap_index.xml\n')
rss = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Nathan Cheng</title><link>'+ORIGIN+'</link><description>Adventures in Longevity.</description>'
for item in META:
    if item['type']!='post': continue
    url = ORIGIN+'/'+item['slug']+'/'
    date = format_datetime(datetime.fromisoformat(item['date']).replace(tzinfo=timezone.utc))
    content = localize((ROOT/'content'/f'{item["slug"]}.html').read_text(),'/'+item['slug']+'/')
    content = re.sub(r'(href|src)="([^"]*)"', lambda m: m.group(1)+'="'+escape(urljoin(url,unescape(m.group(2))),quote=True)+'"',content)
    rss += f'<item><title>{escape(unescape(item["title"]["rendered"]))}</title><link>{url}</link><guid>{url}</guid><pubDate>{date}</pubDate><description>{escape(content)}</description></item>'
(OUT/'feed.xml').write_text(rss+'</channel></rss>\n')
write('/feed/', '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Nathan Cheng RSS</title><meta http-equiv="refresh" content="0;url=../feed.xml"></head><body><a href="../feed.xml">Nathan Cheng RSS feed</a></body></html>')
(OUT/'404.html').write_text(shell('Page not found','/', '<section class="archive site-shell"><header class="archive-heading"><p class="widget-label">404</p><h1>Page not found.</h1><p><a href="https://nathancheng.xyz/">Return to Nathan Cheng</a></p></header></section>'))
(ROOT/'verification.json').write_text(json.dumps({'captured':'2026-10-24','source':ORIGIN,'pages':report,'homepage_matches_source':True,'published_comments':0,'images_omitted':False,'assets_sanitized':True,'routes':routes},indent=2)+'\n')
print(f'Built {len(routes)} pages. All 6 content bodies and the homepage match the WordPress source text.')
