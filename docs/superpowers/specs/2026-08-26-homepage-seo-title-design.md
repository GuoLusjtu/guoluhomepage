# Homepage SEO Title and LinkedIn Design

## Goal

Update the homepage document title for search-result clarity and add the approved LinkedIn profile entry to the existing social-icon list, while preserving all other metadata, content, styling, scripts, and behavior.

## Change

- Modify only the existing `<title>` element in root `index.html`.
- Replace `<title>GUO LU&#39;s Homepage</title>` with:

  `<title>Guo Lu (鲁国) | SJTU | Video Coding &amp; Generative AI</title>`

- The decoded browser/search-engine title must be exactly `Guo Lu (` followed by the two Chinese characters for the name, then `) | SJTU | Video Coding & Generative AI`.
- Keep the Chinese name as the approved literal UTF-8 characters and escape only the ampersand as `&amp;`, yielding valid HTML while rendering the requested title exactly.

## Metadata boundary

- The current homepage has no `og:title` or `twitter:title`; do not add either field.
- Preserve the existing meta description, canonical URL, all other head markup, schema-related markup, CSS, JavaScript, layout, and visible body content except for the approved LinkedIn icon entry.
- Do not reformat `index.html` or touch any production file other than root `index.html`. A regression test file may change solely to verify this production constraint.

## LinkedIn entry

- Add exactly one LinkedIn `<li>` immediately after the existing GitHub item in the profile `<ul class="social-icon">`.
- Use the exact URL `https://www.linkedin.com/in/guo-lu-118a6592/`.
- Add `aria-label="LinkedIn"` to the anchor.
- Use the existing bundled Font Awesome icon with `<i class="fa fa-linkedin big-icon" aria-hidden="true"></i>`.
- Follow the current social-link behavior: do not add `target`, `rel`, new CSS, JavaScript, visible text, or a duplicate Contact-section link.
- Preserve the existing Contact, Google Scholar, and GitHub entries and their order; the final order is Contact, Google Scholar, GitHub, LinkedIn.

## Verification

- Add a regression test before changing production and observe the expected RED failure.
- Assert exactly one `<title>` exists and its decoded text equals the requested title.
- Assert no `og:title` or `twitter:title` field exists.
- Assert exactly one LinkedIn URL, accessible anchor, and icon occur in the profile list immediately after GitHub, with no Contact-section duplicate.
- Protect the remainder of `index.html` by canonicalizing only the old/new title element and the absent/present LinkedIn `<li>` before a fixed byte-level hash comparison.
- Run the complete test suite, strict UTF-8 decoding, and `git diff --check`.
- Report the changed file, changed field, and the exact before/after diff. Do not push unless separately requested.
