#!/usr/bin/env python3
"""Build a portable static site using only Python's standard library."""
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit
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
    # Remove image markup only. Captions and every text node are retained.
    html = re.sub(r'<img\b[^>]*>', '', html, flags=re.I)
    def link(m):
        url = unescape(m.group(1)); u = urlsplit(url)
        if u.hostname in ('nathancheng.xyz', 'www.nathancheng.xyz'):
            return 'href="' + escape(relative(u.path, route) + ('?' + u.query if u.query else '') + ('#' + u.fragment if u.fragment else ''), quote=True) + '"'
        return m.group(0)
    html = re.sub(r'href="([^"]*)"', link, html)
    html = html.replace('<iframe ', '<iframe title="Longevity Marketcap newsletter" loading="lazy" ')
    return html
def write(route, html):
    dest = OUT / route.strip('/') / 'index.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
def shell(title, route, body, description=None):
    description = description or HOME['hero']['description']
    def href(target): return escape(relative(target, route), quote=True)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} - Nathan Cheng</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{ORIGIN}{route}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{ORIGIN}{route}">
<link rel="icon" href="{href('/assets/favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{href('/assets/style.css')}"><link rel="alternate" type="application/rss+xml" title="Nathan Cheng" href="{href('/feed.xml')}">
<script src="{href('/assets/search-data.js')}" defer></script><script src="{href('/assets/site.js')}" defer></script></head>
<body id="top"><a class="skip-link" href="#main">Skip to content</a><div class="site-shell">
<header class="site-header"><a class="brand" href="{href('/')}">Nathan Cheng<span>Adventures in Longevity.</span></a><nav aria-label="Main navigation"><a href="{href('/about/')}">About</a><a href="{href('/category/learning/')}">Learning</a><a href="https://twitter.com/realnathancheng">Twitter <span aria-hidden="true">↗</span></a></nav></header>
<main id="main">{body}</main>
<section class="site-search" aria-label="Search the site"><form action="{href('/')}" role="search"><label for="search">Search for:</label><div class="search-row"><input id="search" name="s" type="search" placeholder="Input your search keywords" autocomplete="off"><button type="submit">Search <span aria-hidden="true">↗</span></button></div></form><div id="search-results" aria-live="polite" hidden></div></section>
<footer><div><strong>Nathan Cheng</strong><p>{escape(HOME['author'].strip())}</p></div><div class="footer-links"><a href="{href('/feed.xml')}">RSS</a><a href="#top">Back to top ↑</a><span>All rights reserved. 2021</span></div></footer>
</div></body></html>'''
def meta_line(item):
    date = datetime.fromisoformat(item['date'])
    return f'<p class="article-meta"><a href="/author/nathan/">Nathan Cheng</a><span>·</span><time datetime="{item["date"][:10]}">{date.strftime("%B")} {date.day}, {date.year}</time></p>'
def listing(items, route):
    return '<div class="article-list">' + ''.join(f'<a class="article-row" href="{relative("/"+i["slug"]+"/",route)}"><span>{escape(unescape(i["title"]["rendered"]))}</span><span aria-hidden="true">↗</span></a>' for i in items) + '</div>'

OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True)
expected = {p['slug']:p['content']['rendered'] for kind in ['posts','pages'] for p in json.loads((ROOT/'source'/f'{kind}.json').read_text())}
report = []
search = []
for item in META:
    route = '/' + item['slug'] + '/'
    original = (ROOT/'content'/f'{item["slug"]}.html').read_text()
    rendered = localize(original, route)
    assert text(original) == text(rendered), f'Text changed: {route}'
    assert text(expected[item['slug']]) == text(rendered), f'Source text mismatch: {route}'
    title = unescape(item['title']['rendered'])
    body = f'<article class="article"><header class="article-heading"><h1>{escape(title)}</h1>'
    if item['type'] == 'post':
        body += meta_line(item).replace('href="/author/nathan/"',f'href="{relative("/author/nathan/",route)}"')
    body += f'</header><div class="prose" data-original-content>{rendered}</div></article>'
    write(route, shell(title, route, body, text(original)[:180]))
    report.append({'path':route,'text_matches_source':True,'text_sha256':hashlib.sha256(text(rendered).encode()).hexdigest(),'characters':len(text(rendered))})
    search.append({'title':title,'path':route,'text':text(original)})

featured = next(i for i in META if i['slug']=='about-me')
featured_html = (ROOT/'content/about-me.html').read_text()
assert text(HOME['content']) == text(featured_html), 'Homepage differs from the featured post'
home = f'''<section class="hero"><p class="eyebrow">Adventures in Longevity.</p><h1>{escape(HOME['hero']['title'])}</h1><p class="hero-description">{escape(HOME['hero']['description'])}</p></section>
<section class="work"><div class="section-label"><h2>{escape(featured['title']['rendered'])}</h2><span aria-hidden="true">↓</span></div><div class="prose projects" data-original-content>{localize(featured_html,'/')}</div></section>
<section class="learning"><div class="section-label"><h2>Learning</h2></div>{listing([i for i in META if 11 in i.get('categories',[])],'/')}</section>'''
write('/', shell('Nathan Cheng', '/', home))

archives = []
for kind, prefix, key in [('categories','category','categories'),('tags','tag','tags')]:
    for term in json.loads((ROOT/'source'/f'{kind}.json').read_text()):
        route = f'/{prefix}/{term["slug"]}/'
        body = f'<section class="archive"><p class="eyebrow">{escape(prefix.title())}</p><h1>{escape(term["name"])}</h1>{listing([i for i in META if term["id"] in i.get(key,[])],route)}</section>'
        write(route,shell(term['name'],route,body)); archives.append(route)
route = '/author/nathan/'
write(route,shell('Nathan Cheng',route,f'<section class="archive"><p class="eyebrow">Author</p><h1>Nathan Cheng</h1><p class="lede">{escape(HOME["author"].strip())}</p>{listing([i for i in META if i["type"]=="post"],route)}</section>')); archives.append(route)
route = '/author/admin/'
write(route,shell('Admin',route,'<section class="archive"><p class="eyebrow">Author</p><h1>Admin</h1><p>0 posts</p><p>It seems we cannot find what you are looking for. Perhaps searching can help.</p></section>')); archives.append(route)

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
    content = (ROOT/'content'/f'{item["slug"]}.html').read_text()
    rss += f'<item><title>{escape(unescape(item["title"]["rendered"]))}</title><link>{url}</link><guid>{url}</guid><pubDate>{date}</pubDate><description>{escape(content)}</description></item>'
(OUT/'feed.xml').write_text(rss+'</channel></rss>\n')
write('/feed/', '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Nathan Cheng RSS</title><meta http-equiv="refresh" content="0;url=../feed.xml"></head><body><a href="../feed.xml">Nathan Cheng RSS feed</a></body></html>')
(OUT/'404.html').write_text(shell('Page not found','/', '<section class="archive"><p class="eyebrow">404</p><h1>Page not found.</h1><p><a href="https://nathancheng.xyz/">Return to Nathan Cheng</a></p></section>'))
(ROOT/'verification.json').write_text(json.dumps({'captured':'2026-10-24','source':ORIGIN,'pages':report,'homepage_matches_source':True,'published_comments':0,'images_omitted':True,'routes':routes},indent=2)+'\n')
print(f'Built {len(routes)} pages. All 6 content bodies and the homepage match the WordPress source text.')
