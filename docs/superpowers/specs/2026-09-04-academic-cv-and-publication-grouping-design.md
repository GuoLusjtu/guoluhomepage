# Academic CV and Publication Grouping Design

## Goals

Create a concise English academic CV for Guo Lu and make it downloadable from the homepage. Reorganize the standalone Publications page so readers can distinguish journal articles from conference papers without changing the curated inventory.

## Sources and factual constraints

- Use the current English homepage for title, affiliation, biography, awards, teaching, services, and contact information.
- Use the official Shanghai Jiao Tong University faculty profile for verified research projects and roles.
- Use `docs/publications-inventory.md` and `publication/index.html` for publication metadata.
- Use the old indexed CV only for stable historical education facts that agree with current sources.
- Do not invent grant numbers, funding amounts, student names, dates, metrics, or corresponding-author status.

## CV deliverables and layout

- Produce `files/Guo-Lu-CV.docx` as the editable source and `files/Guo-Lu-CV.pdf` as the public download.
- Target approximately five pages, allowing four to six pages if clean page breaks require it.
- Use a restrained single-column academic layout with black body text and a dark-blue heading accent. Do not use a portrait, decorative graphics, or dense multi-column body text.
- Add page numbers and a compact contact line containing the public obfuscated email, homepage, Google Scholar, GitHub, and LinkedIn.

## CV contents

1. Name, current appointment, affiliation, contact, and research interests.
2. Academic appointments and education.
3. Honors and awards from the current homepage.
4. Selected research projects verified by the official faculty profile; show funder, role, topic, and verified dates when available.
5. Approximately 20 selected publications. Favor recent representative work while retaining landmark publications such as DVC and FVC. Separate journal articles and conference papers within each year. Underline or bold Guo Lu consistently; do not add corresponding-author symbols.
6. Professional services, teaching, tutorials, workshops, and challenge organization from the current homepage.

## Homepage integration

- Add a visible `CV` link in the existing profile/social-links area pointing to `/guoluhomepage/files/Guo-Lu-CV.pdf`.
- Preserve the current page layout, biography, Join Us callout, and all existing links.

## Publications page grouping

- Preserve years in reverse chronological order.
- Within every year, render a `Journal Articles` subgroup first and a `Conference Papers` subgroup second.
- Omit an empty subgroup rather than displaying an empty heading.
- Preserve every included publication's title, authors, venue, year, destination, and current within-type relative order.
- Keep the current responsive year layout and accessible heading hierarchy. Year remains `h2`; subgroup labels use `h3`; publication titles move to `h4` so heading levels remain valid.

## Verification

- Render the DOCX to PNG and PDF and inspect every page for clipping, bad page breaks, font substitution, and broken links.
- Verify that the PDF and DOCX contain no placeholder text or unsupported claims.
- Add focused tests for the CV link and publication subgroup structure, then run the existing site test suite.
- Confirm the homepage and Publications page load locally before pushing.
