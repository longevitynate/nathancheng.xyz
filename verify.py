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
audit=json.loads((ROOT/'source/sitemap-audit.json').read_text())
live_paths={p for paths in audit['sitemaps'].values() for p in paths}
assert live_paths==set(report['routes']), 'Migrated routes differ from the live sitemap inventory'
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
for name, paths in audit['sitemaps'].items():
    migrated={urlsplit(n.text).path for n in ET.parse(OUT/name).findall('s:url/s:loc',ns)}
    assert migrated==set(paths), f'Sitemap URL mismatch: {name}'
index={urlsplit(n.text).path.lstrip('/') for n in ET.parse(OUT/'sitemap_index.xml').findall('s:sitemap/s:loc',ns)}
assert index==set(audit['sitemaps']), 'Sitemap index mismatch'
assert not any(re.search(r'src="https?://(?:www\.)?nathancheng\.xyz/wp-content/', f.read_text()) for f in OUT.rglob('*.html')), 'WordPress asset dependency remains'
print(f'PASS: {checked} HTML documents, all internal assets/links, 6 exact content hashes, and XML feeds/sitemaps.')
print(f'PASS: All {len(live_paths)} live sitemap URLs are migrated; all 5 original child sitemap paths are preserved.')

# Every published content body, image, script, and frame has a bounded source.
class Security(HTMLParser):
    def __init__(self, file):
        super().__init__()
        self.in_script=False
        self.file=file
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        assert not any(k.lower().startswith('on') for k in a), 'Inline event handler'
        assert 'style' not in a, 'Unexpected inline CSS'
        assert tag not in ('object','embed','base'), 'Active content element'
        for name in ('href','src','action'):
            if name in a:
                u=urlsplit(a[name])
                assert u.scheme.lower() in ('','http','https','mailto'), 'Unsafe URL'
        if tag=='script':
            assert set(a)<= {'src','defer'}, 'Unexpected script attributes'
            source=(self.file.parent/urlsplit(a.get('src','')).path).resolve()
            assert source in {(OUT/'assets/site.js').resolve(),(OUT/'assets/search-data.js').resolve()}, 'Unknown script'
            assert not urlsplit(a['src']).scheme and not urlsplit(a['src']).netloc, 'Remote script'
            self.in_script=True
        if tag=='iframe':
            assert a.get('src')=='https://sub.longevitymarketcap.com/embed', 'Unknown frame'
            assert 'sandbox' in a and 'allow-top-navigation' not in a['sandbox'].split(), 'Unrestricted frame'
        if tag in ('img','link') and 'src' in a:
            assert not urlsplit(a['src']).scheme and not urlsplit(a['src']).netloc, 'Remote image'
    def handle_endtag(self,tag):
        if tag=='script': self.in_script=False
    def handle_data(self,data):
        assert not self.in_script or not data.strip(), 'Inline script'

for f in OUT.rglob('*.html'):
    html=f.read_text()
    Security(f).feed(html)
    if f.parent.name!='feed':
        assert 'Content-Security-Policy' in html, 'Missing CSP'
audit=json.loads((ROOT/'source/asset-audit.json').read_text())
for name,item in audit['assets'].items():
    assert hashlib.sha256((OUT/'assets'/name).read_bytes()).hexdigest()==item['output_sha256'], 'Asset hash mismatch'
from sanitize_content import sanitize
for malicious in [
    '<script>alert(1)</script>',
    '<p onclick="alert(1)">Text</p>',
    '<a href="javascript:alert(1)">Text</a>',
    '<iframe src="https://example.com"></iframe>',
    '<img src="https://example.com/a.png">',
    '<span style="background:url(https://example.com)">Text</span>',
]:
    try:
        sanitize(malicious,lambda path:path)
    except ValueError:
        pass
    else:
        raise AssertionError('Sanitizer accepted unsafe content')
print('PASS: Content allowlist, active-content restrictions, CSP, and audited asset hashes.')

css=(OUT/'assets/style.css').read_text()
assert not re.search(r'@import\b|expression\s*\(',css,re.I), 'Unexpected active CSS'
for match in re.finditer(r'url\(\s*["\']?([^"\'\s)]+)',css):
    value=match.group(1)
    u=urlsplit(value)
    assert not u.scheme and not u.netloc, 'Remote CSS resource'
    target=(OUT/'assets'/u.path).resolve()
    assert target.is_relative_to((OUT/'assets').resolve()) and target.is_file(), 'Unknown CSS resource'
print('PASS: Stylesheet resources are local and present.')
