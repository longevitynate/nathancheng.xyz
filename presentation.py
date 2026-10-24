"""Static templates based on the original Expertly theme's measured layout."""
from pathlib import Path
from html import escape, unescape
from datetime import datetime
import json, posixpath

ROOT = Path(__file__).resolve().parent
HOME = json.loads((ROOT/'source/home.json').read_text())
POSTS = json.loads((ROOT/'source/posts.json').read_text())
ORIGIN = 'https://nathancheng.xyz'
TWITTER = 'https://twitter.com/realnathancheng'

def relative(target, route):
    path = posixpath.relpath(target.strip('/') or '.', route.strip('/') or '.')
    return path + ('/' if target.endswith('/') and path != '.' else '')

def icon(name):
    paths = {
        'search':'<circle cx="10.5" cy="10.5" r="7.5"/><path d="m16 16 5 5"/>',
        'chevron':'<path d="m6 9 6 6 6-6"/>',
        'up':'<path d="m6 14 6-6 6 6"/>',
        'menu':'<path d="M3 6h18M3 12h18M3 18h18"/>',
        'rss':'<path d="M4 11a9 9 0 0 1 9 9M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1" fill="currentColor"/>',
        'globe':'<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
        'clock':'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
        'comment':'<path d="M4 4h16v13H9l-5 4Z"/>',
        'twitter':'<path fill="currentColor" stroke="none" d="M22 5.9a8.2 8.2 0 0 1-2.4.7 4.2 4.2 0 0 0 1.8-2.3 8.4 8.4 0 0 1-2.6 1 4.2 4.2 0 0 0-7.2 3.8A11.9 11.9 0 0 1 3 4.7a4.2 4.2 0 0 0 1.3 5.6 4.2 4.2 0 0 1-1.9-.5v.1a4.2 4.2 0 0 0 3.4 4.1 4.2 4.2 0 0 1-1.9.1 4.2 4.2 0 0 0 3.9 2.9A8.4 8.4 0 0 1 2 18.7a11.8 11.8 0 0 0 6.4 1.9c7.7 0 11.9-6.4 11.9-11.9v-.5A8.5 8.5 0 0 0 22 5.9Z"/>'
    }
    return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'+paths[name]+'</svg>'

def date_label(item):
    d = datetime.fromisoformat(item['date'])
    return f'{d.strftime("%B")} {d.day}, {d.year}'

def search_form(route, name):
    return f'''<section class="site-search" aria-label="Search the site">
<form action="{relative('/',route)}" role="search"><label class="sr-only" for="search-{name}">Search for:</label>
<div class="search-row">{icon('search')}<input id="search-{name}" name="s" type="search" placeholder="Input your search keywords" autocomplete="off"><button type="submit">Search</button></div></form>
<div class="search-results" aria-live="polite" hidden></div></section>'''

def socials(route, counts=False):
    if counts:
        return f'<a class="twitter" href="{TWITTER}" aria-label="Twitter">{icon("twitter")} <span>10K</span></a><a class="rss" href="{relative("/feed.xml",route)}" aria-label="RSS feed">{icon("rss")}</a>'
    return f'<a href="{relative("/",route)}" aria-label="Website">{icon("globe")}</a><a href="{TWITTER}" aria-label="Twitter">{icon("twitter")}</a>'

def sidebar(route):
    items = POSTS[:1] if route == '/' else POSTS
    featured = ''.join(f'<li><h4><a href="{relative("/"+i["slug"]+"/",route)}">{escape(unescape(i["title"]["rendered"]))}</a></h4><time datetime="{i["date"][:10]}">{date_label(i)}</time></li>' for i in items)
    return f'''<aside class="sidebar" aria-label="Sidebar"><section class="author-card">
<h2 class="widget-label">Author</h2><h3><a href="{relative('/author/nathan/',route)}">Nathan Cheng</a></h3>
<a href="{relative('/author/nathan/',route)}"><img src="{relative('/assets/avatar.png',route)}" alt="Nathan Cheng" width="80" height="80" loading="lazy" decoding="async"></a>
<p>{escape(HOME['author'].strip())}</p><div class="social-links">{socials(route)}</div></section>
{search_form(route,'sidebar')}<section class="widget"><h2 class="widget-label">Featured Posts</h2><ul class="featured-list">{featured}</ul></section>
<section class="widget"><h2 class="widget-label">Twitter</h2></section></aside>'''

def layout(body, route):
    return f'<div class="site-content site-shell"><div class="content-area">{body}</div>{sidebar(route)}</div>'

def meta_line(item, route=None):
    route = route or '/'+item['slug']+'/'
    minutes = {'about-me':2,'day-1-molecular-biology-of-the-cell-chapter-1-cells-and-genomes':5,'ride-along-compressing-a-biology-undergrad-into-1-year':4}.get(item['slug'],2)
    return f'''<div class="article-meta"><a href="{relative('/author/nathan/',route)}"><img class="author-avatar" src="{relative('/assets/avatar.png',route)}" alt="" width="60" height="60" loading="lazy" decoding="async"></a><div>
<div class="author-name"><a href="{relative('/author/nathan/',route)}">Nathan Cheng</a><span class="meta-social">{socials(route)}</span></div>
<div class="meta-details"><time datetime="{item['date'][:10]}">{date_label(item)}</time><span aria-hidden="true">·</span><span>{icon('clock')}{minutes} minute read</span><span aria-hidden="true">·</span><span>{icon('comment')}No comments</span></div></div></div>'''

def listing(items, route):
    result = []
    for item in items:
        original = next(p for p in POSTS if p['slug']==item['slug'])
        link = relative('/'+item['slug']+'/',route)
        excerpt = escape(unescape(original['excerpt']['rendered']).strip())
        result.append(f'<article class="article post"><header class="article-heading"><h2 class="article-title"><a href="{link}">{escape(unescape(item["title"]["rendered"]))}</a></h2>{meta_line(item,route)}</header><div class="article-excerpt"><p>{excerpt}</p><a class="read-more" href="{link}">Read more</a></div></article>')
    return '<div class="article-list">'+''.join(result)+'</div>'

def homepage(featured, content):
    hero = f'''<section class="hero"><img class="hero-portrait" src="assets/hero.png" alt="Nathan Cheng" width="700" height="600" fetchpriority="high" decoding="async"><div class="hero-copy">
<h1>{escape(HOME['hero']['title'])}</h1><p class="hero-description">{escape(HOME['hero']['description'])}</p>{search_form('/','hero')}</div></section>'''
    post = f'<article class="article post"><header class="article-heading"><h2 class="article-title"><a href="{featured["slug"]}/">{escape(unescape(featured["title"]["rendered"]))}</a></h2>{meta_line(featured,"/")}</header><div class="prose" data-original-content>{content}</div></article>'
    return hero + layout(post,'/')

def category_listing(items, name, route):
    cards = []
    for index,item in enumerate(items):
        link=relative('/'+item['slug']+'/',route)
        title=escape(unescape(item['title']['rendered']))
        minutes=5 if item['slug'].startswith('day-1-') else 4 if item['slug'].startswith('ride-along-') else 2
        if index==0:
            cards.append(f'<article class="category-lead"><h2><a href="{link}">{title}</a></h2><p><a href="{relative("/author/nathan/",route)}">Nathan Cheng</a> <span>·</span> {date_label(item)} <span>·</span> {minutes} minute read</p></article>')
        else:
            cards.append(f'<article class="category-card"><p class="reading-time">{minutes} minute read</p><h2><a href="{link}">{title}</a></h2><time datetime="{item["date"][:10]}">{date_label(item)}</time></article>')
    # The original category template moves every post into its featured block,
    # leaving a "0 posts" archive below. Preserve that visible wording.
    return '<section class="category-featured">'+''.join(cards)+'</section>'+f'<header class="archive-heading"><p class="widget-label">Browsing Category</p><h1>{escape(name)}</h1><p>0 posts</p></header><div class="archive-empty"><p>It seems we cannot find what you are looking for. Perhaps searching can help.</p>{search_form(route,"archive")}</div>'

def post_footer(item, route):
    tag_html = ''
    if item.get('tags'):
        tags = json.loads((ROOT/'source/tags.json').read_text())
        links = [f'<a href="{relative("/tag/"+t["slug"]+"/",route)}">{escape(t["name"])}</a>' for t in tags if t['id'] in item['tags']]
        tag_html = '<section class="related-tags"><h2>Related Tags</h2><p>'+', '.join(links)+'</p></section>'
    return f'''<div class="post-footer"><section class="post-author"><img src="{relative('/assets/avatar.png',route)}" width="80" height="80" alt="Nathan Cheng" loading="lazy"><div>
<h2><a href="{relative('/author/nathan/',route)}">Nathan Cheng</a></h2><p>{escape(HOME['author'].strip())}</p><div class="social-links">{socials(route)}</div></div></section>{tag_html}</div>'''

def category_menu(route):
    posts = ''.join(f'<a class="menu-post" href="{relative("/"+i["slug"]+"/",route)}"><strong>{escape(unescape(i["title"]["rendered"]))}</strong><time datetime="{i["date"][:10]}">{date_label(i)}</time></a>' for i in POSTS if 11 in i.get('categories',[]))
    return f'<div class="category-menu"><a class="menu-category" href="{relative("/category/learning/",route)}">Learning</a><div class="menu-posts">{posts}</div></div>'

def shell(title, route, body, description=None):
    description = description or HOME['hero']['description']
    def href(target): return escape(relative(target,route),quote=True)
    body = body if route=='/' else layout(body,route)
    page_title = 'Nathan Cheng - Adventures in Longevity.' if route=='/' else title+' - Nathan Cheng'
    current = ' class="current" aria-current="page"' if route=='/about/' else ''
    csp = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; frame-src https://sub.longevitymarketcap.com; connect-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self'"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}"><meta name="referrer" content="strict-origin-when-cross-origin">
<title>{escape(page_title)}</title><meta name="description" content="{escape(description,quote=True)}">
<link rel="canonical" href="{ORIGIN}{route}"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{ORIGIN}{route}">
<link rel="icon" href="{href('/assets/favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{href('/assets/style.css')}">
<link rel="alternate" type="application/rss+xml" title="Nathan Cheng" href="{href('/feed.xml')}">
<script src="{href('/assets/search-data.js')}" defer></script><script src="{href('/assets/site.js')}" defer></script></head>
<body id="top"><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner site-shell"><div class="brand-group"><a class="brand" href="{href('/')}">Nathan Cheng</a><span class="tagline">Adventures in Longevity.</span></div>
<button class="menu-button" type="button" aria-label="Toggle navigation" aria-expanded="false" aria-controls="main-nav">{icon('menu')}</button>
<nav class="main-nav" id="main-nav" aria-label="Main navigation"><details class="categories"><summary>Categories {icon('chevron')}</summary>{category_menu(route)}</details><a href="{href('/about/')}"{current}>About</a><div class="mobile-search">{search_form(route,'mobile')}</div></nav>
<div class="header-social">{socials(route,True)}<button class="header-search-button" type="button" aria-label="Search the site" aria-controls="header-search" aria-expanded="false">{icon('search')}</button></div></div>
<div id="header-search" class="header-search-panel" hidden><div class="site-shell">{search_form(route,'header')}</div></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="footer-inner site-shell"><div><h2 class="footer-title">Nathan Cheng</h2><p class="copyright">All rights reserved. 2021</p></div><div class="footer-social">{socials(route,True)}</div></div></footer>
<a class="back-to-top" href="#top" aria-label="Back to top">{icon('up')}</a></body></html>'''
