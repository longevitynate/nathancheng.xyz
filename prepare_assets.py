#!/usr/bin/env python3
"""Validate and reconstruct explicitly selected assets. Never fetches URLs.

Run once with local paths to the four selected downloads:
  python3 prepare_assets.py --hero PATH --avatar PATH --portrait PATH --font PATH

Requires Pillow and fonttools for preparation only. The static build remains
standard-library-only. Originals remain outside assets/ and docs/.
"""
from pathlib import Path
from io import BytesIO
import argparse, hashlib, json, warnings
from PIL import Image, ImageOps
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = Path(__file__).resolve().parent
Image.MAX_IMAGE_PIXELS = 20_000_000
warnings.simplefilter('error', Image.DecompressionBombWarning)
SOURCES = {
 'hero.png':'https://nathancheng.xyz/wp-content/uploads/2021/05/Nathan-padded-avatar-3.png',
 'avatar.png':'https://secure.gravatar.com/avatar/8b6933b086bd3597583b9f6673bf12e6?s=160&d=mm&r=g',
 'portrait.jpg':'https://nathancheng.xyz/wp-content/uploads/2019/02/IMG_3867-768x1024.jpg',
 'lora.woff':'https://nathancheng.xyz/wp-content/uploads/2025/09/0QI6MX1D_JOuGQbT0gvTJPa787weuyJF.woff'
}

def digest(data): return hashlib.sha256(data).hexdigest()

def bounded_read(path, limit):
    p = Path(path).resolve(strict=True)
    if not p.is_file() or p.stat().st_size > limit:
        raise ValueError('Invalid input size: '+str(path))
    data = p.read_bytes()
    if not data or len(data) > limit:
        raise ValueError('Invalid input size')
    return data

def rebuild_image(path, name, expected):
    data = bounded_read(path, 10_000_000)
    if not (data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xff\xd8\xff')):
        raise ValueError('Expected PNG or JPEG signature')
    with Image.open(BytesIO(data)) as source:
        if source.format not in ('PNG','JPEG') or getattr(source,'n_frames',1) != 1:
            raise ValueError('Unsupported image format')
        if source.size != expected:
            raise ValueError(f'Unexpected {name} dimensions: {source.size}')
        source.verify()
    with Image.open(BytesIO(data)) as source:
        pixels = ImageOps.exif_transpose(source)
        mode = 'RGB' if name.endswith('.jpg') else 'RGBA'
        pixels = pixels.convert(mode)
        # A fresh image stores only decoded pixels, never source metadata.
        clean = Image.frombytes(mode, pixels.size, pixels.tobytes())
        result = BytesIO()
        if mode == 'RGB':
            clean.save(result,format='JPEG',quality=95,optimize=True)
        else:
            clean.save(result,format='PNG',optimize=True)
    rebuilt = result.getvalue()
    with Image.open(BytesIO(rebuilt)) as verified:
        verified.verify()
    return rebuilt, {'source_url':SOURCES[name], 'input_sha256':digest(data),
                     'output_sha256':digest(rebuilt),'bytes':len(rebuilt),
                     'width':expected[0],'height':expected[1],
                     'method':'Decode pixels and encode fresh image without source metadata'}

def rebuild_font(path):
    data = bounded_read(path, 1_000_000)
    if not data.startswith(b'wOFF'):
        raise ValueError('Expected WOFF signature')
    font = TTFont(BytesIO(data),lazy=False,checkChecksums=2)
    if font.sfntVersion != '\x00\x01\x00\x00' or 'glyf' not in font:
        raise ValueError('Expected a TrueType outline font')
    allowed = {'GlyphOrder','head','hhea','maxp','OS/2','hmtx','cmap','loca','glyf',
               'name','post','GDEF','GPOS','GSUB','kern'}
    # Remove executable TrueType hint programs, unknown/opaque tables, and
    # embedded SVG/bitmap data before rebuilding.
    for tag in list(font.keys()):
        if tag not in allowed:
            del font[tag]
    font.ensureDecompiled()
    if 'Lora' not in (font['name'].getDebugName(1) or ''):
        raise ValueError('Unexpected font family')
    if len(font.getGlyphOrder()) > 10000:
        raise ValueError('Unexpected glyph count')
    options = subset.Options()
    options.hinting = False
    options.name_IDs = ['*']
    options.name_languages = ['*']
    options.recalc_bounds = True
    sanitizer = subset.Subsetter(options=options)
    sanitizer.populate(glyphs=font.getGlyphOrder())
    sanitizer.subset(font)
    font.flavor = 'woff'
    font.flavorData = None
    out = BytesIO()
    font.save(out,reorderTables=True)
    rebuilt = out.getvalue()
    check = TTFont(BytesIO(rebuilt),lazy=False,checkChecksums=2)
    check.ensureDecompiled()
    assert not {'fpgm','prep','cvt ','SVG ','DSIG','meta'} & set(check.keys())
    for glyph in check['glyf'].glyphs.values():
        if hasattr(glyph,'program'):
            assert len(glyph.program.getBytecode()) == 0
    return rebuilt, {'source_url':SOURCES['lora.woff'],'input_sha256':digest(data),
                     'output_sha256':digest(rebuilt),'bytes':len(rebuilt),
                     'method':'Rebuild recognized TrueType tables; remove hint programs and opaque metadata'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('hero','avatar','portrait','font'):
        parser.add_argument('--'+key,required=True)
    args = parser.parse_args()
    outputs = {}
    for key,name,size in [('hero','hero.png',(700,600)),('avatar','avatar.png',(160,160)),
                          ('portrait','portrait.jpg',(768,1024))]:
        outputs[name] = rebuild_image(getattr(args,key),name,size)
    outputs['lora.woff'] = rebuild_font(args.font)
    # Write only after every input passes, so failure leaves the site unchanged.
    for name,(data,record) in outputs.items():
        (ROOT/'assets'/name).write_bytes(data)
    report = {'assets':{name:record for name,(_,record) in outputs.items()},
              'notes':'Structural validation and reconstruction reduce risk; not a malware-free guarantee.'}
    (ROOT/'source/asset-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Rebuilt 3 raster images and 1 font. Hashes saved in source/asset-audit.json.')

if __name__ == '__main__':
    main()
