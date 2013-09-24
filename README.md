mediagoblin_svg
===============

This plugin adds support for SVG images to MediaGoblin. For now, it simply
converts uploaded images to PNG and provides a link for downloading the
original image at the media display page. SVG rendering can be performed
either by using `python-rsvg` and `cairo` libraries or by the `rsvg` command-line
utility (default behaviour).

To display SVG images directly in the browser, specify the `serve_img` option
in the configuration file as follows:

    [[mediagoblin_svg]]
    serve_img=True

The SVG plugin is highly experimental at the moment and using it with your
MediaGoblin instance may break things, so please use with caution.
