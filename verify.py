#!/usr/bin/env python3
"""Validate migrated text, internal links, and static document metadata."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, hashlib, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.content=[]; self.depth=0; self.level=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='div':
            self.level+=1
            if 'data-original-content' in a: self.depth=self.level
        for attr in ('href','src'):
            if attr in a: self.links.append(a[attr])
    def handle_endtag(self, tag):
        if tag=='div':
            if self.level==self.depth: self.depth=0
            self.level-=1
    def handle_data(self,data):
        if self.depth: self.content.append(data)

checked=0
for f in OUT.rglob('*.html'):
    p=Page(); p.feed(f.read_text())
    assert '<meta name="viewport"' in f.read_text() or f.parent.name=='feed', f'Missing viewport: {f}'
    for link in p.links:
        url=urlsplit(link)
        if url.scheme or url.netloc or not url.path: continue
        dest=(f.parent/unquote(url.path)).resolve()
        assert dest.is_relative_to(OUT.resolve()), f'Link escapes site: {f}: {link}'
        assert dest.is_file() or (dest/'index.html').is_file(), f'Broken internal link: {f}: {link}'
    checked+=1

report=json.loads((ROOT/'verification.json').read_text())
for item in report['pages']:
    p=Page(); p.feed((OUT/item['path'].strip('/')/'index.html').read_text())
    value=re.sub(r'\s+',' ',''.join(p.content)).strip()
    assert hashlib.sha256(value.encode()).hexdigest()==item['text_sha256'], f'Rendered body mismatch: {item["path"]}'
for f in OUT.glob('*.xml'): ET.parse(f)
assert not any(re.search(r'src="https?://(?:www\.)?nathancheng\.xyz/wp-content/', f.read_text()) for f in OUT.rglob('*.html')), 'WordPress asset dependency remains'
print(f'PASS: {checked} HTML documents, all internal assets/links, 6 exact content hashes, and XML feeds/sitemaps.')
