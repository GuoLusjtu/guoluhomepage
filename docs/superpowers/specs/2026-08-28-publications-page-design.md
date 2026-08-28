# Curated Publications Page Design

## Goal

Replace the current `/publication/` redirect with a curated publications page that is easier to scan than Google Scholar while retaining a link to the Scholar profile for citation statistics and the complete source record.

The homepage will continue to show a short recent-publications selection. Its existing **More Publications** link will open the new `/publication/` page.

## Scope

The independent page will include peer-reviewed journal articles and full papers published at conference main tracks. It will include field-specific venues such as PCS, VCIP, ICME, ISCAS, ICASSP, and EUSIPCO; the page will not classify venues by CCF rank or label any venue as minor.

The first version will exclude:

- workshop papers;
- duplicate arXiv records when a peer-reviewed version exists;
- standalone preprints without a confirmed acceptance;
- patents;
- tutorials, challenge descriptions, and similar non-paper records;
- supplementary-material entries and obvious duplicate or malformed Scholar entries.

A conference item qualifies as a main-track full paper only when the official proceedings table of contents, official conference program, or paper PDF identifies it as a regular/main-conference paper. Items identified as workshop, companion, demo, challenge, tutorial, poster abstract, or short-paper track are excluded. When public metadata does not resolve the category, the item is marked `needs-review` in the inventory and is not rendered until Guo Lu confirms it.

An accepted paper whose official page is not yet available may be included only when supported by a publisher early-access record, an official venue program/accepted-paper list, or acceptance information explicitly supplied by Guo Lu. Its title may temporarily link to arXiv. A Scholar-only claim is not sufficient evidence of acceptance.

## Curated Inventory Gate

Before page markup is generated, implementation will create a reviewable inventory covering every Scholar record and every accepted paper supplied directly by Guo Lu. Each record has these fields:

- exact title;
- ordered display authors;
- venue display name and abbreviation;
- display year;
- title destination URL, nullable when no reliable public destination exists;
- authority URL used to verify the metadata, nullable only for a record explicitly confirmed by Guo Lu;
- provenance (`official-page`, `publisher`, `official-pdf`, `arxiv`, or `user-confirmed`) and a short note when provenance is `user-confirmed`;
- record type (`journal`, `conference-main`, or `excluded`);
- inclusion status (`include`, `exclude`, or `needs-review`);
- exclusion reason, when applicable.

The inventory is a committed, review-stage artifact at `docs/publications-inventory.md`. It is the deterministic source during initial page generation and initial duplicate/exclusion tests. Items marked `needs-review` are presented to Guo Lu as a short exception list and remain off the page until resolved. After Guo Lu approves the inventory and the page is generated, the rendered static HTML becomes the long-term publication source of truth; the inventory remains as an audit record and is not loaded at runtime. Future publications are added directly to the static page under the applicable year.

Duplicate matching uses a normalized title key formed by Unicode normalization, lowercasing, removing punctuation, collapsing whitespace, and removing suffixes such as `supplementary material`. A formal publication and its arXiv version share one display entry. Potential matches that remain ambiguous are marked `needs-review` rather than merged automatically.

## Data Sources and Verification

Google Scholar is the discovery inventory, not the authority for author names. Each selected paper will be matched by title against the strongest available source in this order:

1. the paper-specific official proceedings page when it exposes the paper directly, including CVF Open Access and OpenReview;
2. the publisher or DOI landing page, including IEEE Xplore, ACM Digital Library, Springer, and AAAI Proceedings;
3. the official paper PDF;
4. arXiv, when the formal record is not yet available;
5. Google Scholar only as a discovery fallback, not as authority for expanding names or confirming acceptance.

Author initials will never be expanded by guessing. If a full name cannot be verified reliably, the source abbreviation will remain until it can be corrected. Titles, author order, venue, year, and destination URL must agree with the selected authoritative source.

For a conference paper, the display year is the official conference edition year. For a journal paper, the display year is the year of the final volume/issue record; an early-access paper without a volume/issue uses the publisher's early-access year until the final record is available. The inventory records the chosen year authority. A preprint year never overrides the formal venue year.

## Information Architecture

The page will use the existing site header, navigation conventions, typography, content width, footer, analytics snippet, and responsive behavior. It will introduce no new framework or runtime dependency.

The page begins with:

- the heading `Publications`;
- one short sentence explaining that the list is curated from peer-reviewed work;
- a link to Guo Lu's Google Scholar profile for citation statistics.

Publications appear in reverse chronological order from 2026 to the earliest retained year. A year will not consume a full-width heading row. On desktop, each year is a narrow left column aligned with the first publication in that group, while the group's publications occupy the wider right column. On narrow screens, the year becomes a compact label immediately above the first publication in the group.

## Publication Entry

Every paper uses a compact two-block presentation; either block may wrap naturally onto additional rendered lines:

1. paper title, linked when a verified destination exists;
2. authors followed by venue abbreviation and publication year.

Example:

> **DVC: An End-to-End Deep Video Compression Framework**  
> <u>Guo Lu</u>, Wanli Ouyang, Dong Xu, Xiaoyun Zhang, Chunlei Cai, Zhiyong Gao · *CVPR, 2019*

The title uses the same deterministic priority as metadata verification: paper-specific official proceedings page, then publisher/DOI landing page, then official paper PDF, then arXiv for a confirmed accepted paper whose formal page is unavailable. A paper with no verified destination remains unlinked rather than receiving a guessed URL.

The first version will not add separate PDF, Code, Project, Highlight, or Oral controls. These can be added later without changing the entry structure.

## Author Presentation

Authors remain in publication order. Verified full English names are preferred over initials. `Guo Lu` is always underlined and remains in its true author position.

Verified name variants that refer to the site owner, including `G. Lu`, `G Lu`, or `Lu Guo`, are normalized to the display form `Guo Lu` before the underline and single-occurrence checks. This normalization occurs only when the authoritative paper metadata or Guo Lu confirms the identity; initials are not assumed to identify Guo Lu merely because they match.

For publications with at most ten authors, all authors are shown. For publications with more than ten authors, the page retains the first four authors, Guo Lu, and the final two authors, inserting an ellipsis at every omitted span. If Guo Lu is already within the first four or final two, the name is not duplicated. The displayed sequence must preserve the original ordering.

## Responsive and Visual Behavior

The design stays visually consistent with the existing academic homepage:

- titles use the site's existing link color and a modest semibold weight;
- author and venue text is smaller and visually secondary;
- year labels use compact bold or blue-gray text;
- entries use restrained vertical spacing and no cards, tables, badges, or heavy borders;
- long titles and author lists wrap naturally;
- the mobile layout has no horizontal scrolling.

## Navigation and SEO

The homepage **More Publications** link will change from Google Scholar to `/guoluhomepage/publication/`. The Google Scholar icon and profile link elsewhere on the homepage remain unchanged.

The new page document title will be `Publications | Guo Lu (鲁国) | SJTU`, and its canonical URL will be `https://guolusjtu.github.io/guoluhomepage/publication/`. It will follow the site's existing metadata conventions without adding absent Open Graph or Twitter fields. The navigation retains the same destinations and social links as the homepage, with Publications visibly active on the new page. The current homepage SEO title, body copy, layout, and recent-publications selection will not otherwise change.

## Data Maintenance

After the initial inventory is approved and rendered, the publication list will be stored directly in the static page, following the repository's current architecture. The review inventory is retained only as an audit artifact, not as a second runtime data source. New papers can be inserted into the current year group; a new year adds one year group and its entries. Citation counts will not be copied into the page, avoiding frequently stale data.

## Validation

Implementation verification will cover:

- the homepage **More Publications** link targets the new page;
- `/publication/` no longer redirects to the homepage;
- all retained entries have a title, authors, venue, and year;
- Guo Lu is underlined and appears once per author list;
- when a title URL is present, it is absolute and uses `https://`;
- excluded record types and duplicate titles are absent;
- year groups are in reverse chronological order;
- desktop and mobile layouts wrap without horizontal overflow;
- existing homepage content tests continue to pass;
- the Cloudflare analytics snippet remains present on the new page.

Automated URL checks validate absolute `https://` syntax only and do not make external reachability a test requirement. Link availability is audited manually during inventory preparation because publisher availability and anti-bot behavior are unstable.

Responsive acceptance is checked at a 1280-pixel desktop viewport and a 375-pixel mobile viewport. At both widths, the document must have no horizontal overflow; at 1280 pixels the year occupies the narrow left column, and at 375 pixels the year appears as a compact label above the first entry in its group. The mobile transition uses the site's Bootstrap-compatible breakpoint at `max-width: 767px`.
