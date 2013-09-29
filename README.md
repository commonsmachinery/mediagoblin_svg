mediagoblin_svg
===============

This plugin adds support for SVG images to MediaGoblin. For now, it simply
converts uploaded images to PNG and provides a link for downloading the
original image at the media display page. SVG rendering can be performed
either by using `python-rsvg` and `cairo` libraries or by the `rsvg` command-line
utility (default behaviour).

Installation
------------

Download and install mediagoblin_svg:

    pip install https://github.com/commonsmachinery/mediagoblin_svg/tarball/master

Add the plugin to your mediagoblin_local.ini:

    [[mediagoblin_svg]]

Run dbupdate to initialize the SVG data tables:

    ./bin/gmg dbupdate

And restart the server.

Configuration
-------------

Displaying SVG images directly in the browser is controlled by two options called
`svg_thumbnails` and `svg_previews`. Specify them in your mediagoblin_local.ini
as follows:

    [[mediagoblin_svg]]
    svg_previews=True
    svg_thumbnails=False

It's recommended to run a reprocessing command after changing either of these
options:

    ./bin/gmg reprocess bulk_run mediagoblin_svg resize preview
    ./bin/gmg reprocess bulk_run mediagoblin_svg resize thumb

Disclaimer
----------

The SVG plugin is highly experimental at the moment and using it with your
MediaGoblin instance may break things, so please use with caution.
