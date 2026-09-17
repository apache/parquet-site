# Hugo shortcodes

Shortcodes are Hugo templates called from Markdown content;
see the [Hugo shortcode documentation] for details.

This site uses shortcodes to dynamically generate content from data stored in
the `data/` directory.

For example the [format-versions.html] shortcode is used in the [versions.md]
page to generate the format version tables. The page calls it with Hugo's
shortcode syntax and passes a `table` parameter such as `forward_incompatible`.

[format-versions.html]: format-versions.html
[versions.md]: ../../content/en/docs/File%20Format/versions.md
[Hugo shortcode documentation]: https://gohugo.io/content-management/shortcodes/#custom
