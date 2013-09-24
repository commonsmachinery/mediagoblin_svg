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

To display SVG images directly in the browser, specify the `serve_img` option
in the configuration file as follows:

    [[mediagoblin_svg]]
    serve_img=True

The SVG plugin is highly experimental at the moment and using it with your
MediaGoblin instance may break things, so please use with caution.
