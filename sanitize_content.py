"""Allowlisted rendering of the six WordPress content bodies."""
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit
import re

TAGS = {'p','a','ul','ol','li','h1','h2','h3','h4','h5','h6','div','strong','em',
        'br','figure','img','span','figcaption','blockquote','cite','iframe'}
CLASSES = {'pk-alert','pk-alert-info','has-text-align-center','wp-block-image',
           'is-resized','wp-image-808','aligncenter','wp-block-pullquote'}
PORTRAIT = 'https://nathancheng.xyz/wp-content/uploads/2019/02/IMG_3867-768x1024.jpg'
NEWSLETTER = 'https://sub.longevitymarketcap.com/embed'

class Content(HTMLParser):
    def __init__(self, relative):
        super().__init__(convert_charrefs=True)
        self.relative = relative
        self.output = []
    def handle_starttag(self, tag, attrs):
        if tag not in TAGS:
            raise ValueError('Unexpected content tag: ' + tag)
        raw = dict(attrs)
        if any(name.lower().startswith('on') for name in raw):
            raise ValueError('Event handler in original content')
        a = {}
        if 'class' in raw:
            values = raw['class'].split()
            if not set(values) <= CLASSES:
                raise ValueError('Unknown content class')
            a['class'] = ' '.join(values)
        if tag == 'a':
            value = raw.get('href', '')
            u = urlsplit(value)
            if u.scheme.lower() not in ('https','http','mailto','') or (u.netloc and not u.scheme):
                raise ValueError('Unsafe link scheme')
            if any(ord(c) < 32 for c in value):
                raise ValueError('Control character in URL')
            if u.hostname in ('nathancheng.xyz','www.nathancheng.xyz'):
                value = self.relative(u.path) + ('?' + u.query if u.query else '') + ('#' + u.fragment if u.fragment else '')
            a['href'] = value
            a['rel'] = 'noopener noreferrer'
        if tag == 'img':
            if raw.get('src') != PORTRAIT:
                raise ValueError('Unexpected content image')
            a.update(src=self.relative('/assets/portrait.jpg'), alt=raw.get('alt',''),
                     loading='lazy', decoding='async')
            for name in ('width','height'):
                if not re.fullmatch(r'\d{1,4}',raw.get(name,'')):
                    raise ValueError('Invalid image dimensions')
                a[name] = raw[name]
        if tag == 'iframe':
            if raw.get('src') != NEWSLETTER:
                raise ValueError('Unexpected frame source')
            a.update(src=NEWSLETTER,title='Longevity Marketcap newsletter',loading='lazy',
                     width='100%',height='320',referrerpolicy='strict-origin-when-cross-origin',
                     sandbox='allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox')
        if 'style' in raw and tag != 'iframe':
            if raw['style'].strip() != 'text-decoration: underline;':
                raise ValueError('Unexpected inline content style')
            a['class'] = (a.get('class','') + ' text-underline').strip()
        if raw.get('role') == 'alert':
            a['role'] = 'note'
        self.output.append('<' + tag + ''.join(' ' + k + '="' + escape(v,quote=True) + '"' for k,v in a.items()) + '>')
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in ('img','br'):
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        if tag not in TAGS:
            raise ValueError('Unexpected closing tag')
        if tag not in ('img','br'):
            self.output.append('</' + tag + '>')
    def handle_data(self, data):
        self.output.append(escape(data))
    def handle_comment(self, data):
        pass

def sanitize(html, relative):
    parser = Content(relative)
    parser.feed(html)
    parser.close()
    return ''.join(parser.output)
