# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import logging
import argparse
import subprocess

from mediagoblin import mg_globals as mgg
from mediagoblin.processing import (
    BadMediaFail, FilenameBuilder,
    MediaProcessor, ProcessingManager,
    request_from_args, get_process_filename,
    store_public, copy_original)


_log = logging.getLogger(__name__)

MEDIA_TYPE = 'mediagoblin_svg'
SUPPORTED_FILETYPES = ['svg', 'svgz']


def sniff_handler(media_file, **kw):
    _log.info('Sniffing {0}'.format(MEDIA_TYPE))
    if kw.get('media') is not None:  # That's a double negative!
        name, ext = os.path.splitext(kw['media'].filename)
        clean_ext = ext[1:].lower()  # Strip the . from ext and make lowercase

        if clean_ext in SUPPORTED_FILETYPES:
            _log.info('Found file extension in supported filetypes')
            return MEDIA_TYPE
        else:
            _log.debug('Media present, extension not found in {0}'.format(
                    SUPPORTED_FILETYPES))
    else:
        _log.warning('Need additional information (keyword argument \'media\')'
                     ' to be able to handle sniffing')

    return None


def render_pyrsvg(svg_filename, png_filename, max_size):
    """
    Render an SVG image, scaled to fit the specified max_size using pyrsvg
    """
    import rsvg, cairo

    svg = rsvg.Handle(svg_filename)
    svg_width, svg_height, _, _ = svg.get_dimension_data()

    ratio = min(float(max_size[0]) / svg_width, float(max_size[1]) / svg_height)
    png_width = int(round(svg_width * ratio))
    png_height = int(round(svg_height * ratio))

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, png_width, png_height)
    ctx = cairo.Context(surface)
    ctx.transform(cairo.Matrix(xx=ratio, yy=ratio))
    
    svg.render_cairo(ctx)
    surface.write_to_png(png_filename)
    #return (png_width, png_height)

def render_rsvg(svg_filename, png_filename, max_size):
    """
    Render an SVG image, scaled to fit the specified max_size using rsvg command
    """
    cmd = ['rsvg', '--keep-aspect-ratio', '-w', str(max_size[0]), '-h', str(max_size[1]),
           '-f', 'png', svg_filename, png_filename]
    subprocess.Popen(cmd).wait()

render_preview = render_rsvg


class CommonSvgProcessor(MediaProcessor):
    """
    Provides a base for various svg processing steps
    """
    acceptable_files = ['original']

    def common_setup(self):
        """
        Set up the workbench directory and pull down the original file
        """
        self.svg_config = mgg.global_config['plugins']['mediagoblin_svg']

        # Conversions subdirectory to avoid collisions
        self.conversions_subdir = os.path.join(
            self.workbench.dir, 'conversions')
        os.mkdir(self.conversions_subdir)

        # Pull down and set up the processing file
        self.process_filename = get_process_filename(
            self.entry, self.workbench, self.acceptable_files)
        self.name_builder = FilenameBuilder(self.process_filename)

    def generate_preview(self, size=None):
        if not size:
            size = (mgg.global_config['media:medium']['max_width'],
                    mgg.global_config['media:medium']['max_height'])

        preview_filename = os.path.join(self.workbench.dir,
            self.name_builder.fill('{basename}.preview.png'))

        render_preview(self.process_filename, preview_filename, size)
        store_public(self.entry, 'preview', preview_filename,
                     self.name_builder.fill('{basename}.preview.png'))

    def generate_thumb(self, size=None):
        if not size:
            size = (mgg.global_config['media:thumb']['max_width'],
                    mgg.global_config['media:thumb']['max_height'])

        thumb_filename = os.path.join(self.workbench.dir,
            self.name_builder.fill('{basename}.thumbnail.png'))
        
        render_preview(self.process_filename, thumb_filename, size)
        store_public(self.entry, 'thumb', thumb_filename,
                     self.name_builder.fill('{basename}.thumbnail.png'))

    def copy_original(self):
        copy_original(
            self.entry, self.process_filename,
            self.name_builder.fill('{basename}{ext}'))


class InitialProcessor(CommonSvgProcessor):
    """
    Initial processing step for new svg files
    """
    name = "initial"
    description = "Initial processing"

    @classmethod
    def media_is_eligible(cls, entry=None, state=None):
        """
        Determine if this media type is eligible for processing
        """
        if not state:
            state = entry.state
        return state in (
            "unprocessed", "failed")

    ###############################
    # Command line interface things
    ###############################

    @classmethod
    def generate_parser(cls):
        parser = argparse.ArgumentParser(
            description=cls.description,
            prog=cls.name)

        parser.add_argument(
            '--size',
            nargs=2,
            metavar=('max_width', 'max_height'),
            type=int)

        parser.add_argument(
            '--thumb-size',
            nargs=2,
            metavar=('max_width', 'max_height'),
            type=int)

        return parser

    @classmethod
    def args_to_request(cls, args):
        return request_from_args(
            args, ['size', 'thumb_size'])

    def process(self, size=None, thumb_size=None):
        self.common_setup()
        self.generate_preview(size=size)
        self.generate_thumb(size=thumb_size)
        self.copy_original()
        self.delete_queue_file()


class Resizer(CommonSvgProcessor):
    """
    Resizing processor for thumbnails and rendered images
    """
    name = 'resize'
    description = 'Resize thumbnail and preview image'
    thumb_size = 'size'

    @classmethod
    def media_is_eligible(cls, entry=None, state=None):
        """
        Determine if this media type is eligible for processing
        """
        if not state:
            state = entry.state
        return state in 'processed'

    ###############################
    # Command line interface things
    ###############################

    @classmethod
    def generate_parser(cls):
        parser = argparse.ArgumentParser(
            description=cls.description,
            prog=cls.name)

        parser.add_argument(
            '--size',
            nargs=2,
            metavar=('max_width', 'max_height'),
            type=int)

        parser.add_argument(
            '--thumb-size',
            nargs=2,
            metavar=('max_width', 'max_height'),
            type=int)

        parser.add_argument(
            'file',
            choices=['medium', 'thumb'])

        return parser

    @classmethod
    def args_to_request(cls, args):
        return request_from_args(
            args, ['size', 'file'])

    def process(self, file, size=None):
        print "process", "file:", file
        self.common_setup()
        if file == 'medium':
            self.generate_preview(size=size)
        elif file == 'thumb':
            self.generate_thumb(size=size)


class SvgProcessingManager(ProcessingManager):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.add_processor(InitialProcessor)
        self.add_processor(Resizer)
