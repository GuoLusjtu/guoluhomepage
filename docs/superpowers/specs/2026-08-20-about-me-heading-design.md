# About Me Heading Design

## Goal

Give the Bio text column a clear visual entry point so the introductory paragraph no longer begins flush at the top, while keeping the homepage restrained and consistent with the existing Join Us callout.

## Markup

- Add exactly one semantic `<h3 id="about-me-heading" class="about-me-heading">About Me</h3>` inside the Bio description column.
- Place the heading immediately before the existing introductory `<p>` and after no other visible content in that column.
- Keep the existing Bio paragraph left-aligned with no first-line indentation.
- Preserve the complete Bio paragraph, Join Us callout, portrait, links, Publications, and all other homepage content unchanged.

## Styling

- Add `.about-me-heading` styling to `css/hugo-academic.css` rather than using inline styles.
- Use `margin: 0 0 16px` so the heading begins cleanly at the top of the right column and creates visible separation before the first paragraph.
- Use `font-weight: 600` for clear but restrained emphasis.
- Do not add a border, background, icon, fixed dimension, or first-line indentation.
- Allow the existing heading typography to determine font family, color, and responsive size, keeping it visually related to the Join Us heading without making it a second callout.

## Verification

- Add a regression test before production changes and observe the expected RED failure.
- Assert the heading occurs exactly once, uses the exact semantic element/id/class/text, and immediately precedes the Bio paragraph.
- Assert the CSS declarations are exact and contain no border, background, fixed dimensions, or text indentation.
- Preserve existing byte/content guards except for the approved heading insertion and stylesheet addition.
- Run the complete test suite, strict UTF-8 decoding, `git diff --check`, and a local HTTP source/layout smoke test before pushing.
