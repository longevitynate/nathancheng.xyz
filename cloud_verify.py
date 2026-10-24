#!/usr/bin/env python3
"""Bounded migration preparation and verification on an isolated GitHub runner."""
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
import base64, json, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parent
ALLOWED_HOSTS = {'nathancheng.xyz','secure.gravatar.com'}
class RestrictedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        u=urlsplit(newurl)
        if u.scheme!='https' or u.hostname not in ALLOWED_HOSTS:
            raise ValueError('Unexpected redirect destination')
        return super().redirect_request(req,fp,code,msg,headers,newurl)
opener=build_opener(RestrictedRedirect())

def download(url,path,kind,max_bytes):
    req=Request(url,headers={'User-Agent':'NathanChengPersonalSiteMigration/1.0'})
    with opener.open(req,timeout=30) as response:
        actual=urlsplit(response.url)
        if actual.scheme!='https' or actual.hostname not in ALLOWED_HOSTS:
            raise ValueError('Unexpected response origin')
        content_type=response.headers.get_content_type()
        allowed={'png':{'image/png'},'jpg':{'image/jpeg'},'woff':{'application/font-woff','font/woff','application/octet-stream'}}
        if content_type not in allowed[kind]:
            raise ValueError('Unexpected content type '+content_type)
        data=response.read(max_bytes+1)
        if not data or len(data)>max_bytes:
            raise ValueError('Invalid download size')
        signatures={'png':b'\x89PNG\r\n\x1a\n','jpg':b'\xff\xd8\xff','woff':b'wOFF'}
        if not data.startswith(signatures[kind]):
            raise ValueError('Invalid file signature')
        path.write_bytes(data)
        print('Verified download signature and limit:',path.name,len(data),'bytes',flush=True)

def run(*args):
    subprocess.run([sys.executable,*args],cwd=ROOT,check=True,timeout=120)

subprocess.run(['node','--check','assets/site.js'],cwd=ROOT,check=True,timeout=30)
run('-m','py_compile','build.py','presentation.py','sanitize_content.py','prepare_assets.py','verify.py')
if not (ROOT/'source/asset-audit.json').exists():
    with tempfile.TemporaryDirectory(prefix='nathan-selected-assets-') as folder:
        folder=Path(folder)
        selections=[
            ('hero','hero.png','https://nathancheng.xyz/wp-content/uploads/2021/05/Nathan-padded-avatar-3.png','png',1_000_000),
            ('avatar','avatar.png','https://secure.gravatar.com/avatar/8b6933b086bd3597583b9f6673bf12e6?s=160&d=mm&r=g','png',500_000),
            ('portrait','portrait.jpg','https://nathancheng.xyz/wp-content/uploads/2019/02/IMG_3867-768x1024.jpg','jpg',3_000_000),
            ('font','nathan-serif.woff','https://nathancheng.xyz/wp-content/uploads/2025/09/0QI6MX1D_JOuGQbT0gvTJPa787weuyJF.woff','woff',1_000_000),
        ]
        args=['prepare_assets.py']
        for flag,name,url,kind,limit in selections:
            download(url,folder/name,kind,limit)
            args.extend(['--'+flag,str(folder/name)])
        run(*args)
run('inspect_original.py')
run('build.py')
run('verify.py')

# Export only rebuilt assets and verified public-site files. This does not
# give the build job write permission to the repository.
files=[ROOT/'assets'/n for n in ('hero.png','avatar.png','portrait.jpg','nathan-serif.woff')]
files.extend([ROOT/'source/asset-audit.json',ROOT/'verification.json'])
files.extend(p for p in sorted((ROOT/'docs').rglob('*')) if p.is_file())
for path in files:
    value=base64.b64encode(path.read_bytes()).decode('ascii')
    name=path.relative_to(ROOT).as_posix()
    chunks=[value[i:i+12000] for i in range(0,len(value),12000)] or ['']
    for index,chunk in enumerate(chunks):
        print('NATHAN_EXPORT '+json.dumps({'path':name,'index':index,'total':len(chunks),'data':chunk}),flush=True)
print('NATHAN_BUILD_VERIFIED',flush=True)
