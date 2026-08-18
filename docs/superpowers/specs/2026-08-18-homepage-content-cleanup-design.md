# Homepage Content Cleanup Design

## Scope

Update the generated static homepage without rebuilding the legacy Hugo project.

## Confirmed changes

1. Change the metadata description from `PhD-SJTU` to `Associate Professor at Shanghai Jiao Tong University | Video Coding, Multimedia Processing, and Efficient Multimodal LLMs`.
2. Correct `Gradudate Course` to `Graduate Course` and update its heading ID accordingly.
3. Replace the incorrect AAAI'25 publication venue with `Proceedings of the AAAI Conference on Artificial Intelligence, 39(10), 10725–10733, 2025.`
4. Keep `(Highlight)` for the CVPR'25 Image Quality Assessment paper and remove the conflicting `(Oral)` label from that entry only. Preserve valid `(Oral)` labels on other publications.
5. Remove the invalid `mailto:sdluguo AT gmail.com` link. Make the header email icon link to `#contact`, and display `luguo2014 AT sjtu.edu.cn` as plain text in the Contact section.
6. Wrap the complete News navigation `<li>` in an HTML comment in every HTML file that currently contains that item (19 files). Preserve the existing `news/` files unchanged and directly accessible for later content updates.
7. On the homepage only, rename the Awards section anchor from `#project` to `#awards` and update its Awards navigation link to `#awards`. Preserve unrelated `#projects` links elsewhere.
8. On the homepage only, change the footer from `© 2020 Guo Lu` to `© 2020–2026 Guo Lu`.

## Compatibility and boundaries

- Do not delete the News archive or any publication assets.
- Do not change the separate `/project/` archive.
- Keep the site as static HTML/CSS/JavaScript.
- Do not redesign layout, typography, colors, or publication ordering.

## Verification

A repository-local check will verify that:

- the metadata description, AAAI citation, `Graduate Course` text, and `id="graduate-courses"` are correct;
- the Image Quality Assessment entry contains `(Highlight)` but not `(Oral)`, while other publication labels remain unchanged;
- the header email icon resolves to `#contact`, Contact visibly contains the plain text `luguo2014 AT sjtu.edu.cn`, and the invalid `mailto:sdluguo AT gmail.com` is absent;
- all 19 existing News navigation items are commented out as complete `<li>` elements, while `/news/index.html` remains present and unchanged;
- the homepage Awards navigation resolves to the homepage `id="awards"`, with exact checks that do not match or alter unrelated `#projects` links;
- the homepage footer shows `© 2020–2026 Guo Lu` without modifying legacy attribution on other pages.

The homepage and the preserved News archive will also be served locally for HTTP smoke tests before committing the implementation.
