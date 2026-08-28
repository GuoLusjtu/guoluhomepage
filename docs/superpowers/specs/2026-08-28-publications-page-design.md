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

An accepted paper whose official page is not yet available may be included when its acceptance and bibliographic details are already confirmed. Its title may temporarily link to arXiv.

## Data Sources and Verification

Google Scholar is the discovery inventory, not the authority for author names. Each selected paper will be matched by title against the strongest available source in this order:

1. official publisher or proceedings page, including IEEE Xplore, ACM Digital Library, CVF Open Access, OpenReview, Springer, and AAAI Proceedings;
2. the official paper PDF;
3. arXiv, when the formal record is not yet available;
4. Google Scholar only as a fallback.

Author initials will never be expanded by guessing. If a full name cannot be verified reliably, the source abbreviation will remain until it can be corrected. Titles, author order, venue, year, and destination URL must agree with the selected authoritative source.

## Information Architecture

The page will use the existing site header, navigation conventions, typography, content width, footer, analytics snippet, and responsive behavior. It will introduce no new framework or runtime dependency.

The page begins with:

- the heading `Publications`;
- one short sentence explaining that the list is curated from peer-reviewed work;
- a link to Guo Lu's Google Scholar profile for citation statistics.

Publications appear in reverse chronological order from 2026 to the earliest retained year. A year will not consume a full-width heading row. On desktop, each year is a narrow left column aligned with the first publication in that group, while the group's publications occupy the wider right column. On narrow screens, the year becomes a compact label immediately above the first publication in the group.

## Publication Entry

Every paper uses a compact two-line presentation:

1. linked paper title;
2. authors followed by venue abbreviation and publication year.

Example:

> **DVC: An End-to-End Deep Video Compression Framework**  
> <u>Guo Lu</u>, Wanli Ouyang, Dong Xu, Xiaoyun Zhang, Chunlei Cai, Zhiyong Gao · *CVPR, 2019*

The title links to the official publication or DOI landing page. CVF Open Access and OpenReview are preferred where applicable because they provide stable paper-specific pages. If no reliable formal page exists, an accepted paper may link to arXiv. A paper with no verified destination remains unlinked rather than receiving a guessed URL.

The first version will not add separate PDF, Code, Project, Highlight, or Oral controls. These can be added later without changing the entry structure.

## Author Presentation

Authors remain in publication order. Verified full English names are preferred over initials. `Guo Lu` is always underlined and remains in its true author position.

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

The new page will have a descriptive document title, canonical URL, and existing site metadata conventions. The current homepage SEO title, body copy, layout, and recent-publications selection will not otherwise change.

## Data Maintenance

The publication list will be stored directly in the static page, following the repository's current architecture. New papers can be inserted into the current year group; a new year adds one year group and its entries. Citation counts will not be copied into the page, avoiding frequently stale data.

## Validation

Implementation verification will cover:

- the homepage **More Publications** link targets the new page;
- `/publication/` no longer redirects to the homepage;
- all retained entries have a title, authors, venue, and year;
- Guo Lu is underlined and appears once per author list;
- title URLs are syntactically valid and use HTTPS where available;
- excluded record types and duplicate titles are absent;
- year groups are in reverse chronological order;
- desktop and mobile layouts wrap without horizontal overflow;
- existing homepage content tests continue to pass;
- the Cloudflare analytics snippet remains present on the new page.

