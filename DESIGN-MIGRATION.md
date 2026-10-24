# Original design restoration: draft checkpoint

This branch contains prepared source changes, not a completed deployment. Do not merge or publish until the checks below pass. The production main branch and generated docs/ files were not changed.

## Completed

- Read the original homepage and About page in the browser at a 1512px desktop viewport.
- Measured the original Expertly theme rather than importing its PHP, JavaScript, plugins, or icon fonts.
- Prepared templates and CSS for the header, Categories menu, blue portrait hero, search, white article panels, author sidebar, pink links, archive cards, and footer.
- Kept the six original content files and source snapshots unchanged.
- Added a content-tag allowlist, local image substitution, restricted newsletter frame, and content security policy.
- Prepared a one-time asset reconstruction script. Build refuses to run without its asset audit and matching output hashes.
- JavaScript passed a syntax parse. CSS braces balance. Python build and browser tests have NOT been run on these changes.

## Assets and interrupted work

The browser exported these three selected files into its temporary asset directory:

- Hero: source PNG, 116429 bytes, 700 x 600, RGBA. Pillow format verification passed.
- Avatar: source PNG, 25975 bytes, 160 x 160, RGBA. Pillow format verification passed.
- Lora WOFF: exported but not yet parsed or rebuilt.

The connection dropped during export of the 768 x 1024 About/handsome portrait. Its completion is unknown.

None of these downloaded originals were committed or used in the generated website. No asset reconstruction has completed. Format verification alone is not a malware-free guarantee.

On the disconnected computer the first export directory was:
    /var/folders/nj/x6ykcmbd5f7f6r86sn_7l6640000gp/T/browser-use/assets/210fbc6c-7ad1-4509-81ce-0c27781974d2

Filenames: hero c5cdc7d6c6cc191e.png, avatar 4b00583f9f891bf8, font 1dd3adb430b0a644.woff.
The original local project is /Users/nathan/Documents/ai-playground/nathancheng-personal-site.
A pip installation of fonttools into /tmp/nathan-site-fonttools was started, but its outcome is unknown.

## Finish before publishing

1. Recover the selected downloads or obtain those same specific assets again. Inspect the actual images.
2. Run prepare_assets.py with explicit local paths. It limits file sizes and dimensions, reconstructs pixels without original metadata, rebuilds the Lora TrueType tables without hint programs, and records input/output SHA256 hashes. Inspect font licensing metadata and preserve applicable notices.
3. Run Python syntax checks, build.py, and verify.py. Review all six normalized content hashes against the original snapshots and all 13 sitemap routes.
4. Compare the original single-post, handsome, archive, and Coming Soon layouts. Their full visual layouts still need inspection. Adjust the draft templates as required; do not claim a complete design match based only on homepage/About evidence.
5. Test desktop and mobile navigation, search on nested URLs and the project-path deployment, local image/font loading, newsletter display, and browser console. Capture screenshots and refine spacing.
6. Regenerate docs/, inspect the complete diff, publish to the personal main branch, and verify GitHub Pages deployment.
7. Leave nathancheng.xyz DNS and the old WordPress host unchanged until the separate domain cutover.

## Measured desktop design

- Header: 60px high, white; shell max width 1340px.
- Brand: system sans, 20px bold. Tagline 15px, faded gray.
- Body background: #f8f8f8. Main text #121416, links #d641b4.
- Homepage hero: 50/50 columns. Padded portrait image expands to column width; image supplies its white spacing.
- Hero heading: 52px / 62.4px, bold system sans. Description 20px / 30px.
- Main content: top margin 48px; 980px article panel, 60px gap, 300px sidebar at 1512px viewport.
- Article panel: 80px padding. Heading 40px / 40px bold sans.
- Article body: Lora 17px / 29.75px; paragraphs bottom margin 32px. Post body max width 670px. About body uses the panel's 820px interior width.
- Author card: white, 24px padding, 80px circular avatar; body text 14px / 22px with 188px text width.
- Footer: white, 48px padding; original copyright text preserved.
