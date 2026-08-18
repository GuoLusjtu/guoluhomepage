# 2026 Homepage Publications, Services, and News Refresh

## Goal

Refresh the homepage with two newly accepted papers and current professional service, and restore News using a hybrid presentation: six concise items on the homepage plus a chronological archive at `/news/` beginning in 2026. Keep the existing visual language and analytics, and avoid presenting the homepage publication list as exhaustive.

## Scope and constraints

- Edit the generated static HTML directly; do not redesign the site or introduce a new build system.
- Keep the existing About text, publication entries not named below, service entries not named below, and all other visible content unchanged. The pre-2026 News archive is intentionally retired from both HTML and XML.
- Preserve the exact Cloudflare Web Analytics beacon once on every one of the 19 body-bearing HTML pages, keep legacy Google Analytics absent, and leave the 12 meta-refresh redirect stubs byte-for-byte unchanged.
- The `Recent Publications` section remains a curated list. It may omit papers on which Guo Lu is not the corresponding author, even when a News item reports the full acceptance count.

## Publications

Add these two entries to the 2026 group in `Recent Publications`.

### TOMM'26

- Label and title: `[TOMM'26] Diff-VF: Training-free High-quality Long Video Generation via Diffusion Model`
- Link the title to:
  `https://scholar.google.com.au/citations?view_op=view_citation&hl=zh-CN&user=R9iwlJcAAAAJ&sortby=pubdate&citation_for_view=R9iwlJcAAAAJ:4fKUyHm3Qg0C`
- Authors, in this exact order: `Haoning Yang, Xinyuan Chen, Yaohui Wang, Guo Lu`
- Underline only `Guo Lu`, following the existing author-emphasis convention.
- Venue: `ACM Transactions on Multimedia Computing, Communications, and Applications (TOMM), 2026.`

### T-CSVT'26

- Label and title: `[T-CSVT'26] Large Language Model for Lossless Image Compression with Visual Prompts`
- Link the title to:
  `https://scholar.google.com.au/citations?view_op=view_citation&hl=zh-CN&user=R9iwlJcAAAAJ&cstart=20&pagesize=80&sortby=pubdate&citation_for_view=R9iwlJcAAAAJ:ZHo1McVdvXMC`
- Authors, in this exact order: `Junhao Du, Chuqin Zhou, Yunuo Chen, Guo Lu`
- Underline only `Guo Lu`.
- Venue: `IEEE Transactions on Circuits and Systems for Video Technology, 2026.`

The resulting 2026 order must be:

1. ECCV'26
2. ACMMM'26
3. TOMM'26 (new)
4. T-CSVT'26 (new)
5. Engineering'26
6. CVPR'26, `Unified...`
7. CVPR'26, `Adaptive...`
8. ICLR'26

Do not display acceptance months in publication entries. Do not add the second ACM MM 2026 paper to `Recent Publications`.

## Professional Services

Keep the existing Associate Editor entry first. Add or update the following entries without creating duplicates:

- `Guest Editor, IEEE Journal on Emerging and Selected Topics in Circuits and Systems (JETCAS) Special Issue on “When Large Models Meet Video Coding: Synergies, Systems, and Hardware Challenges,” 2026.`
- `Challenge Organizer, The Challenge on Ultra-Low Bitrate Image Compression @ ECCV 2026.`
- `Area Chair, International Conference on Learning Representations (ICLR), 2025, 2026.`
- `Area Chair, Annual Conference on Neural Information Processing Systems (NeurIPS), 2025, 2026.`
- `Senior PC, AAAI, 2021, 2026.`

Do not show the JETCAS submission deadline. Do not show a month for the challenge in Professional Services. Preserve all other service entries and their order as closely as the existing structure allows.

## News content

Use these six concise entries, in this exact newest-first order and without paper titles:

1. `August 2026 — Serving as an Area Chair for ICLR and as a Senior PC member for AAAI.`
2. `August 2026 — Two papers were accepted by ACM TOMM and IEEE T-CSVT.`
3. `July 2026 — Two papers were accepted by ACM MM 2026, and one paper was accepted by ECCV 2026.`
4. `June 2026 — Organizing the Challenge on Ultra-Low Bitrate Image Compression at ECCV 2026.`
5. `March 2026 — Serving as a Guest Editor for an IEEE JETCAS Special Issue.`
6. `February 2026 — Two papers were accepted by CVPR 2026.`

The ACM MM count intentionally reports two accepted papers even though the curated publication list shows only one. Do not add an ICLR 2026 paper-acceptance item or a NeurIPS invitation item.

## Hybrid News architecture

### Homepage

- Insert a compact `home-section` with `id="news"` between About and Recent Publications.
- Show exactly the six entries above.
- Add a `More News` link to `/news/` after the list.
- Reuse the site's current typography and list styling; add no public visitor counter and no elaborate card layout.

### Archive

- Replace the current `/news/` item list with the same six 2026 entries in the same order.
- Remove all 15 pre-2026 items: the 10 currently rendered in `/news/` and the five older items found only in `news/index.xml`.
- Replace the item list in `news/index.xml` with the same six 2026 announcements, so the feed and visible archive share the same time boundary. Do not invent individual detail-page URLs for these items.
- Remove the dead `/news/page/2/` pager; the archive is a single chronological page beginning in 2026.
- The six new concise entries do not receive individual detail pages.
- Future routine News may remain archive-only text; individual detail pages are optional for substantive announcements.

When a seventh newer item is added later, the homepage should still show only the newest six while `/news/` and `news/index.xml` retain the complete history from 2026 onward.

### Navigation

- Re-enable the currently commented News navigation `<li>` on all 19 body-bearing HTML pages.
- The navigation link continues to target the homepage News section (`/#news`, or the existing equivalent that resolves to the homepage section). The `More News` link is the route to the full archive.
- No commented News navigation item should remain after the change.

## Verification strategy

Add regression coverage before changing production HTML, then implement until the full suite passes.

Tests must verify:

- both new publication entries have the exact titles, Scholar URLs, four-author lists, underlined `Guo Lu`, venue text, and positions 3 and 4 within the 2026 group;
- the five specified service lines are exact, stale year variants are gone, no duplicate is introduced, and the deadline is absent;
- the homepage contains one `id="news"` section between About and Publications, exactly the six specified items in exact order, and one `More News` link to `/news/`;
- all 19 body-bearing pages contain an active News navigation item and no commented News navigation item;
- `/news/` contains exactly the same six 2026 items in the same order, with no pre-2026 entries or dead `/news/page/2/` pager;
- `news/index.xml` contains the same six 2026 announcements and no pre-2026 item or invented detail-page URL;
- no individual detail page is created for any of the six new entries;
- the Cloudflare beacon remains exact and single-instance on all 19 content pages, legacy Google Analytics remains absent, and the 12 redirect stubs remain byte-for-byte unchanged.

The existing News preservation test currently hashes the pre-2026 archive. Replace that assertion deliberately: verify the exact six-item HTML archive and matching six-item XML feed, and explicitly verify that the known pre-2026 titles, legacy detail URLs, and dead pager are absent. Continue to protect the News page shell, footer, and analytics through the existing general page invariants.

Run the full regression suite and a local HTTP smoke test for `/`, `/news/`, and one representative tag page. Confirm the new homepage/archive content, active News navigation, existing page markers, and analytics invariants. Deployment and production verification are a separate final step after the implementation is reviewed and the user authorizes pushing.
