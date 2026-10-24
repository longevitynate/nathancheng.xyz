#!/usr/bin/env python3
"""Compare the deployed personal GitHub Pages files with this verified build."""
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor
import hashlib, time
ROOT=Path(__file__).resolve().parent
BASE='https://longevitynate.github.io/nathancheng.xyz/'
class Redirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        u=urlsplit(newurl)
        if u.scheme!='https' or u.hostname!='longevitynate.github.io':
            raise ValueError('Unexpected deployment redirect')
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def check(path):
    expected=path.read_bytes()
    rel=path.relative_to(ROOT/'docs').as_posix()
    route=rel[:-10] if rel.endswith('index.html') else rel
    digest=hashlib.sha256(expected).hexdigest()
    url=BASE+route+'?migration='+digest[:12]
    for attempt in range(3):
        try:
            req=Request(url,headers={'Cache-Control':'no-cache','User-Agent':'NathanPersonalSiteVerification/1.0'})
            with build_opener(Redirect()).open(req,timeout=20) as response:
                actual=response.read(len(expected)+1)
                assert response.status==200, 'Unexpected HTTP status'
                assert hashlib.sha256(actual).hexdigest()==digest, 'Published bytes differ'
            return rel
        except Exception:
            if attempt==2: raise
            time.sleep(5)
paths=[p for p in sorted((ROOT/'docs').rglob('*')) if p.is_file() and not p.name.startswith('.')]
with ThreadPoolExecutor(max_workers=5) as pool:
    checked=list(pool.map(check,paths))
print('LIVE_HTTP_PASS: '+str(len(checked))+' published pages/assets match the verified build byte-for-byte.')
print('Verified '+BASE)
