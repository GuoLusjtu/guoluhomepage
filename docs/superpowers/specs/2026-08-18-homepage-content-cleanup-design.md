# Homepage Content Cleanup Design

## Scope

Update the generated static homepage without rebuilding the legacy Hugo project.

## Confirmed changes

1. Change the metadata description from `PhD-SJTU` to `Associate Professor at Shanghai Jiao Tong University | Video Coding, Multimedia Processing, and Efficient Multimodal LLMs`.
2. Correct `Gradudate Course` to `Graduate Course` and update its heading ID accordingly.
3. Replace the incorrect AAAI'25 publication venue with `Proceedings of the AAAI Conference on Artificial Intelligence, 39(10), 10725–10733, 2025.`
4. Keep `(Highlight)` for the CVPR'25 Image Quality Assessment paper and remove the conflicting `(Oral)` label.
5. Remove the invalid `mailto:sdluguo AT gmail.com` link. Make the header email icon link to `#contact`, and display `luguo2014 AT sjtu.edu.cn` as plain text in the Contact section.
6. Comment out the News navigation item on every generated HTML page. Preserve the existing `news/` files for later content updates.
7. Rename the Awards section anchor from `#project` to `#awards` and update the Awards navigation link on every generated HTML page.
8. Change the footer from `© 2020 Guo Lu` to `© 2020–2026 Guo Lu`.

## Compatibility and boundaries

- Do not delete the News archive or any publication assets.
- Do not change the separate `/project/` archive.
- Keep the site as static HTML/CSS/JavaScript.
- Do not redesign layout, typography, colors, or publication ordering.

## Verification

A repository-local check will assert that the corrected strings and anchors exist, the known bad strings are absent from active markup, News navigation is commented out, and all local HTML pages use the new Awards anchor. The homepage will also be served locally for an HTTP smoke test before committing the implementation.
