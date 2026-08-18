# Join Us Callout Design

## Goal

Make the existing recruitment message easier to notice while preserving the restrained visual style of Guo Lu's academic homepage.

## Homepage changes

- Replace the current red, bold recruitment sentence in the Bio section with a compact callout card.
- Use a pale blue background, a solid blue left border, modest padding, and a small border radius. Do not add animation, icons, or warning-red styling.
- Add the heading `Join Us`.
- Use this exact recruitment copy:

  `We are looking for self-motivated Ph.D./M.S. students, research interns, and postdoctoral fellows. Prospective applicants are welcome to send a CV and transcript by email.`

- Place the existing Chinese homepage link inside the callout below the recruitment copy, with visible text `中文主页 →` and the unchanged target `https://icisee.sjtu.edu.cn/jiaoshiml/luguo.html`.
- Keep the callout inside the Bio text column at the current recruitment-message position.

## Small corrections

- Repair the Bio employment range so its source and rendered text are exactly `2020–2022`.
- Remove the erroneous trailing slash from the Publications-section Google Scholar URL, yielding `https://scholar.google.com/citations?user=R9iwlJcAAAAJ&hl=en`.
- Do not change the valid profile Google Scholar link, publication entries, News, Services, navigation, analytics, or other homepage content.

## Accessibility and responsive behavior

- Use semantic text and a real heading element within the callout.
- Keep sufficient foreground/background contrast and retain keyboard-accessible link behavior.
- Allow the card and text to wrap naturally on narrow screens; introduce no fixed width or height.

## Verification

- Add regression tests before production edits and observe the expected RED failures.
- Assert the old red recruitment span and old wording are absent.
- Assert the exact heading, copy, Chinese link text/target, and callout style hooks occur once within the Bio section.
- Assert `2020–2022` is present and the mojibake form is absent.
- Assert both the profile and Publications Google Scholar links resolve to the exact corrected URL, with no trailing-slash variant.
- Run the complete test suite, `git diff --check`, strict UTF-8 decoding, and a local responsive/source smoke test.
