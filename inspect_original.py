"""Read original markup and styling as inert text for design comparison."""
from html.parser import HTMLParser
from urllib.request import urlopen
import json,re
class Outline(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[];self.nodes=[];self.heading=None;self.headings=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);classes=a.get('class','')
        label=tag+('#'+a['id'] if a.get('id') else '')+('.'+classes.replace(' ','.') if classes else '')
        if tag=='body': self.nodes.append({'body':classes})
        if any(x in classes for x in ('site-content','content-area','site-main','entry-header','entry-content','entry-container','entry-footer','entry-title','page-header','post-share','pk-coming','archive-header','cs-main-content')):
            self.nodes.append({'node':label,'parents':self.stack[-5:]})
        if tag in ('h1','h2','h3','h4','h5','h6'):
            self.heading={'tag':tag,'class':classes,'text':''}
        if tag not in ('meta','link','img','br','hr','input','source','wbr','area','base','embed','param'):
            self.stack.append(label)
    def handle_endtag(self,tag):
        if self.heading and tag==self.heading['tag']:
            self.headings.append(self.heading);self.heading=None
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i].split('.')[0].split('#')[0]==tag:
                del self.stack[i:];break
    def handle_data(self,data):
        if self.heading:self.heading['text']+=data
def read(path):
    with urlopen('https://nathancheng.xyz'+path,timeout=25) as r:
        data=r.read(1_000_001)
        assert len(data)<=1_000_000
        return data.decode('utf-8')
for path in ['/about-me/','/who-is-the-most-handsome-asian-guy-in-toronto-nathan-cheng/','/category/learning/','/coming-soon/']:
    try:
        p=Outline();p.feed(read(path))
        print('NATHAN_ORIGINAL '+json.dumps({'path':path,'structure':p.nodes[:45],'headings':p.headings[:20]}),flush=True)
    except Exception as e:print('NATHAN_ORIGINAL_ERROR',path,type(e).__name__,str(e),flush=True)
css=read('/wp-content/themes/expertly/style.css?ver=1.0.0')
wanted=[]
for m in re.finditer(r'([^{}]+)\{([^{}]*)\}',css):
    selector=m[1].strip()
    if any(x in selector for x in ('.entry-single-header','.cs-category-post','.entry-share','.entry-header','.entry-content-wrap','.entry-container','.post-share','.single-post .entry','.page .entry','.entry-footer','.archive-header','.site-main','.content-area','.cs-category-posts','.cs-category-post ','.section-category-posts','.cs-overlay-content','.headings-large','.page-title')):
        wanted.append({'selector':selector,'rules':m[2].strip()})
print('NATHAN_ORIGINAL_CSS '+json.dumps(wanted[:120]),flush=True)
