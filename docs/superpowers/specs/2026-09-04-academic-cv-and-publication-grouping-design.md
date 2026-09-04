# Academic CV and Publication Grouping Design

## Goals

Create a concise English academic CV for Guo Lu and make it downloadable from the homepage. Reorganize the standalone Publications page so readers can distinguish journal articles from conference papers without changing the curated inventory.

## Sources and factual constraints

- Use the current English homepage for title, affiliation, biography, awards, teaching, services, and contact information.
- Use the official Shanghai Jiao Tong University faculty profile at `https://icisee.sjtu.edu.cn/jiaoshiml/luguo.html` for verified research projects and roles. Copy only fields explicitly present there; omit any incomplete role, date, identifier, or amount rather than inferring it.
- Use `docs/publications-inventory.md` and `publication/index.html` for publication metadata.
- Use the old indexed CV only for stable historical education facts that agree with current sources.
- Do not invent grant numbers, funding amounts, student names, dates, metrics, or corresponding-author status.

## CV deliverables and layout

- Produce `files/Guo-Lu-CV.docx` as the editable source and `files/Guo-Lu-CV.pdf` as the public download.
- Publish an identical compatibility copy at `paper/GuoLu.pdf` so indexed legacy links deliver the new CV rather than the obsolete version.
- Target approximately five pages, allowing four to six pages if clean page breaks require it.
- Use a restrained single-column academic layout with black body text and a dark-blue heading accent. Do not use a portrait, decorative graphics, or dense multi-column body text.
- Add page numbers and a compact contact line containing the public obfuscated email, homepage, Google Scholar, GitHub, and LinkedIn.

## CV contents

1. Name, current appointment, affiliation, contact, and research interests.
2. Academic appointments and education.
3. Honors and awards from the current homepage.
4. Selected research projects verified by the official faculty profile; show funder, role, topic, and verified dates when available.
5. Use exactly 21 selected publications: the 19 entries currently shown in the homepage Recent Publications section, plus `FVC: A New Framework towards Deep Video Compression in Feature Space` (CVPR 2021) and `DVC: An End-To-End Deep Video Compression Framework` (CVPR 2019). Copy titles, authors, venues, years, and links from the verified publication inventory without rewriting metadata. Separate journal articles and conference papers within each year. Underline or bold Guo Lu consistently; do not add corresponding-author symbols.
6. Professional services, teaching, tutorials, workshops, and challenge organization from the current homepage.

## Homepage integration

- Add a visible `CV` link in the existing profile/social-links area pointing to `/guoluhomepage/files/Guo-Lu-CV.pdf`.
- Preserve the current page layout, biography, Join Us callout, and all existing links.

## Publications page grouping

- Preserve years in reverse chronological order.
- Within every year, render a `Journal Articles` subgroup first and a `Conference Papers` subgroup second.
- Use the approved `Type` field in `docs/publications-inventory.md` as the classification authority: `journal` maps to Journal Articles and `conference-main` maps to Conference Papers. Do not classify from venue-string guesses.
- Omit an empty subgroup rather than displaying an empty heading.
- Preserve every included publication's title, authors, venue, year, destination, and current within-type relative order.
- Keep the current responsive year layout and accessible heading hierarchy. Year remains `h2`; subgroup labels use `h3`; publication titles move to `h4` so heading levels remain valid.
- Use native DOCX Title and Heading styles, logical reading order, and real hyperlinks. Keep the PDF text selectable/searchable and hyperlinks clickable.

## Verification

- Render the DOCX to PNG and PDF and inspect every page for clipping, bad page breaks, font substitution, and broken links. Verify the result is four to six pages.
- Verify that the PDF and DOCX contain no placeholder text or unsupported claims.
- Verify `files/Guo-Lu-CV.pdf` and `paper/GuoLu.pdf` are byte-identical, the PDF has selectable text, and document hyperlinks are present.
- Add focused tests for the CV link and publication subgroup structure, then run the existing site test suite. Tests must prove that all 72 curated papers appear exactly once, classifications match the inventory, counts are unchanged, within-type relative order is preserved, empty subgroup headings are omitted, and Journal Articles precede Conference Papers whenever both exist in a year.
- Confirm the homepage and Publications page load locally before pushing.
