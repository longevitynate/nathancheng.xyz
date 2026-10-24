# Nathan Cheng's personal website


Portable static replacement for https://nathancheng.xyz, hosted in Nathan's personal GitHub account. No Less Death hosting, billing, databases, or credentials are used.

## Edit and publish

The deployable website is the `docs/` directory. It is ordinary HTML, CSS, and a small JavaScript search function. It has no package manager, build service dependency, server process, PHP, or database.

1. Edit a page in `content/*.html` or the appearance in `assets/style.css`.
2. Run `python3 build.py` and `python3 verify.py`.
3. Commit the source and updated `docs/` files to `main`.

GitHub Pages publishes from `main`, `/docs`. The same `docs/` directory can be uploaded to any static web host. The only third-party embedded service is the existing Longevity Marketcap newsletter form.

`build.py` deliberately checks text against the migration baseline. When intentionally editing wording later, update the corresponding public snapshot in `source/posts.json` or `source/pages.json` to establish the new baseline. For homepage copy, update `source/home.json`. Do not silently relax the checks during migration.

## Preserved content

The public WordPress REST API was captured on October 24, 2026. All 3 published posts and 3 published pages are included, with their existing paths, titles, dates, paragraphs, lists, links, captions, punctuation, and spelling. The homepage introduction and featured post are preserved too. Original wording includes old dates, historical roles, scientific claims, typos, and a parody page; none have been edited.

Six author/category/tag archives, local full-text search, XML sitemaps, and a new RSS file are included. A live sitemap audit on October 24, 2026 found 13 unique URLs across all 5 child sitemaps, including the empty `/author/admin/` archive. All 13 are present, and the original sitemap index and child sitemap URLs are preserved. `source/sitemap-audit.json` records this inventory. `verification.json` records hashes of normalized text (only HTML whitespace is normalized). The original API responses are retained in `source/` for audit and backup; they contain only publicly returned data.

The original design is recreated with a white header, portrait hero, local serif article font, pink links, article panels, author sidebar, category cards, table-of-contents navigation, mobile menu, and footer. Portraits are included on the homepage, About page, and handsome-guy page. Captions and article wording remain unchanged. There were zero public comments. WordPress administration, comment submission, share counters, and theme scripts are not part of the static site. RSS is now at `/feed.xml`; `/feed/` contains a browser redirect, which some RSS readers will not follow. Existing RSS subscribers should use `/feed.xml`.

## Asset preparation and validation

The published files contain three reconstructed raster images and a rebuilt local font. Image formats, dimensions, and size limits were checked; any embedded color profile is converted to sRGB before pixels are re-encoded without the original metadata. The Lora-derived font is rebuilt without hint programs and renamed Nathan Serif under the included SIL Open Font License. Input and output SHA256 hashes are recorded in `source/asset-audit.json`.

The article renderer allows a limited set of tags and links, rejects script/event-handler markup, substitutes local images, and restricts the existing newsletter iframe. The site adds a Content Security Policy and uses only the two small, locally served JavaScript files. No WordPress theme/plugin executable code is imported.

The committed assets are ready to use. Only if replacing them from original downloads, run `prepare_assets.py` with explicit local paths. That one-time preparation needs Pillow and fonttools. The normal site build uses Python's standard library only. GitHub Actions checks the generated documents, original-text hashes, internal links, sitemap inventory, allowed scripts, local CSS resources, and audited asset hashes.

The original homepage and About page were visually inspected before implementation; the other page structures were checked from inert HTML/CSS. Final desktop/mobile browser comparison remains pending because the connected browser became unavailable. See `DESIGN-MIGRATION.md` for the validation record.

## Point nathancheng.xyz at this site

Do this after validating the GitHub Pages deployment. The old WordPress host remains untouched until the DNS switch is completed.

1. In this repository's Settings > Pages, set the custom domain to `nathancheng.xyz` before changing DNS. Preserve the resulting `docs/CNAME` file on future builds.
2. At the domain's DNS provider, replace the existing apex web-host records with these four A records:

   | Name | Type | Value |
   | --- | --- | --- |
   | @ | A | 185.199.108.153 |
   | @ | A | 185.199.109.153 |
   | @ | A | 185.199.110.153 |
   | @ | A | 185.199.111.153 |
   | www | CNAME | longevitynate.github.io |

3. Remove or replace old web-host AAAA records if present. Preserve unrelated email MX/TXT records.
4. Wait for GitHub's domain check and certificate, then enable Enforce HTTPS. DNS can take up to 24 hours to propagate.
5. Check the homepage, `/about/`, both biology posts, newsletter, and mobile layout on the custom domain. Keep the previous host until those checks pass. Retain a private WordPress database/files backup before retiring it; the public snapshots here do not include drafts or the database.

Official instructions: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
