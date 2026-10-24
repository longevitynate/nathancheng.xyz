# Design migration validation

The design restoration includes all 13 sitemap routes, all six original content bodies, the homepage introduction, original portraits, author sidebar, category cards, navigation, tables of contents, and footer. The generated docs/ directory is portable and contains no PHP or WordPress runtime.

## Passed

- Python and JavaScript syntax checks.
- All six article/page bodies and the homepage match the original public WordPress snapshots after normalizing HTML whitespace only.
- All 13 live sitemap URLs and all five original child sitemap filenames are preserved.
- All internal page, script, image, and font references resolve.
- Three images were checked by signature, content type, size, dimensions, and decoder, then re-encoded from fresh pixels. Embedded color profiles are converted to sRGB before metadata removal.
- The local serif font was reconstructed from recognized TrueType tables, stripped of hint programs, renamed Nathan Serif, and distributed with the original license.
- Sanitized asset hashes match the build audit.
- Content tag/URL allowlists, script-source restrictions, iframe restrictions, Content Security Policy, and unsafe-content rejection cases pass.
- Stylesheet resources are checked to be local.

The remote verification runs are visible in this repository's Actions tab. source/asset-audit.json records source URLs and input/output hashes. These are structural and reconstruction checks, not a claim that arbitrary input files can be proven malware-free.

## Visual evidence and remaining check

The original homepage and About page were inspected in Chrome at a 1512px desktop viewport. The single-post, handsome-guy, category, and Coming Soon page structures were subsequently inspected as inert source HTML and CSS, without running their scripts. The sanitized portrait images were also visually inspected.

The completed site's desktop/mobile browser comparison and interactive click-through remain pending because the user's computer/browser disconnected. Automated validation does not substitute for that visual check.

## Design measurements retained

- White header: 60px high; content shell maximum 1340px.
- Brand: system sans, 20px bold. Tagline: 15px, faded gray.
- Background #f8f8f8; text #121416; links #d641b4.
- Homepage hero: two equal columns, padded portrait, 52px heading, 20px/30px description.
- Desktop content: 980px article panel, 60px gap, 300px sidebar at 1512px viewport.
- Article: 80px desktop padding, 40px title, 17px/29.75px serif body. Post body maximum 670px.
- About and handsome pages use the full article interior width. Original image display dimensions and captions are retained.
- Author card: 24px padding and an 80px circular portrait.
- Category landing pages preserve the original featured cards and their original "0 posts" empty-archive wording.
- Footer: white, 48px padding, original 2021 copyright text.

The old WordPress server and custom-domain DNS remain unchanged. Everything is hosted in Nathan's personal GitHub repository and uses no Less Death infrastructure.
