# Join Us Callout Design

## Goal

Make the existing recruitment message easier to notice while preserving the restrained visual style of Guo Lu's academic homepage.

## Homepage changes

- Replace the current red, bold recruitment sentence in the Bio section with a compact callout card.
- Use a pale blue background, a solid blue left border, modest padding, and a small border radius. Do not add animation, icons, or warning-red styling.
- Add the heading `Join Us`.
- Use this exact recruitment copy:

  `We are looking for self-motivated Ph.D./M.S. students, research interns, and postdoctoral fellows. Prospective applicants are welcome to send a CV and transcript by email.`

- Place the existing Chinese homepage link inside the callout below the recruitment copy. Encode the source label as `&#20013;&#25991;&#20027;&#39029; &rarr;` so it renders as the four Chinese characters for "Chinese homepage" followed by a right arrow. Keep the unchanged target `https://icisee.sjtu.edu.cn/jiaoshiml/luguo.html`.
- Close the existing Bio paragraph after the honors text. Add the callout as a sibling block within the Bio text column at the current recruitment-message position; do not nest block content inside that paragraph.
- Use this semantic structure: `<aside class="join-us-callout" aria-labelledby="join-us-heading">`, `<h3 id="join-us-heading">Join Us</h3>`, a recruitment `<p>`, and the Chinese-homepage `<a>`.
- Define the callout appearance in `css/hugo-academic.css`; do not use inline presentation styles.

## Small corrections

- Preserve the already-correct Bio employment range using source `2020&ndash;2022`, rendered as `2020` followed by an en dash and `2022`.
- Remove the erroneous trailing slash from the Publications-section Google Scholar URL, yielding `https://scholar.google.com/citations?user=R9iwlJcAAAAJ&hl=en`.
- Do not change the valid profile Google Scholar link, publication entries, News, Services, navigation, analytics, or other homepage content.

## Accessibility and responsive behavior

- Use the semantic `aside`, labelled heading, paragraph, and link structure specified above.
- Keep sufficient foreground/background contrast and retain keyboard-accessible link behavior.
- Allow the card and text to wrap naturally on narrow screens; introduce no fixed width or height. CSS must use fluid block sizing and include a narrow-screen media rule for reduced padding.

## Verification

- Add regression tests before production edits and observe the expected RED failures.
- Assert the old red recruitment span and old wording are absent.
- Assert the exact semantic structure, heading, copy, decoded Chinese link label plus arrow, target, and callout style hooks occur once within the Bio section.
- Assert the source contains `2020&ndash;2022`, rendered text decodes to the correct employment range, and neither HTML nor CSS contains U+FFFD replacement characters.
- Assert both the profile and Publications Google Scholar links resolve to the exact corrected URL, with no trailing-slash variant.
- Assert the callout CSS contains no fixed width or height and includes a narrow-screen padding adjustment.
- Run the complete test suite, `git diff --check`, strict UTF-8 decoding, and a local responsive/source smoke test.
