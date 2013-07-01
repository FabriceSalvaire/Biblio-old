####################################################################################################
# 
# Babel - A Bibliography Manager 
# Copyright (C) Salvaire Fabrice 2013 
# 
####################################################################################################

####################################################################################################

import unicodedata

import mupdf as cmupdf
from MuPDF import *

####################################################################################################

from .MupdfTools import *
from .TextStyle import TextStyles, TextStyleFrequencies
from Babel.Tools.Interval import IntervalInt2D

####################################################################################################

class TextPage():

    ##############################################

    def __init__(self, page, text_sheet, text_page):

        self._page = page
        self._text_sheet = text_sheet
        self._text_page = text_page
        
        self._page_number = self._page._page_number
        self._document = self._page._document
        self._context = self._document._context

        self._styles = None

    ##############################################

    def __del__(self):

        cmupdf.fz_free_text_sheet(self._context, self._text_sheet)
        cmupdf.fz_free_text_page(self._context, self._text_page)

    ##############################################

    @property
    def interval(self):

        mediabox = self._text_page.mediabox

        return IntervalInt2D((mediabox.x0, mediabox.x1),
                             (mediabox.y0, mediabox.y1))

    ##############################################

    def word_iterator(self):

        # Fixme: word iterator for block
        
        for block in TextBlockIterator(self._text_page):
            for line in TextLineIterator(block):
                word = u''
                for span in TextSpanIterator(line):
                    for char in TextCharIterator(span):
                        unicode_char = unichr(char.c)
                        category = unicodedata.category(unicode_char)
                        # Take only letters, and numbers when it is not the first character
                        if ((category in ('Ll', 'Lu')) or (category == 'Nd' and word)):
                            word += unicode_char.lower()
                        elif word:
                            yield word
                            word = u''
                if word: # Last char was a letter/number
                    yield word

    ##############################################
    
    def _get_styles(self):

        styles = TextStyles()
        style = self._text_sheet.style
        while style:
            styles.register_style(to_text_style(style))
            style = style.next
        styles.sort()
        
        return styles

    ##############################################

    @property
    def styles(self):

        if self._styles is None:
            self._styles = self._get_styles()
        return self._styles

    ##############################################
    
    def dump_text_style(self):

        template = 'span.s%u{font-family:"%s";font-size:%gpt'
        text = ''
        style = self._text_sheet.style
        while style:
            font = style.font
            text += template % (style.id, get_font_name(font), style.size)
            if cmupdf.font_is_italic(font):
                text += ';font-style:italic'
            if cmupdf.font_is_bold(font):
                text += ';font-weight:bold;'
            text += '}\n'
            style = style.next

        return text

    ##############################################

    def dump_text_page_xml(self, dump_char=True):

        text = u'<page page_number="%u">\n' % (self._page_number)
        for block in TextBlockIterator(self._text_page):
            text += u'<block bbox="' + format_bounding_box(block) + u'">\n'
            for line in TextLineIterator(block):
                text += u' '*2 + u'<line bbox="' + format_bounding_box(line) + u'">\n'
                for span in TextSpanIterator(line):
                    style = span.style
                    font_name = get_font_name(style.font)
                    text += u' '*4 + u'<span bbox="' + format_bounding_box(span) + \
                        u'" font="%s" size="%g">\n' % (font_name, style.size)
                    if dump_char:
                        for char in TextCharIterator(span):
                            text += u' '*6 + '<char bbox="' + format_bounding_box(char) + \
                                u'" c="%s"/>\n' % (unichr(char.c))
                    else:
                        text += u' '*4 + u'<p>' + span_to_string(span) + u'</p>\n'
                    text += u' '*4 + u'</span>\n'
                text += u' '*2 + u'</line>\n'
            text += u'</block>\n'
        text += u'</page>\n'

        return text

    ##############################################

    def to_blocks(self):

        # Fixme: @property ?

        styles = self.styles
        
        blocks = TextBlocks()
        for c_block in TextBlockIterator(self._text_page):
            text_block = TextBlock(self)
            for c_line in TextLineIterator(c_block):
                line_interval = to_interval(c_line)
                text_line = TextLine(line_interval)
                for c_span in TextSpanIterator(c_line):
                    text_span = TextSpan(span_to_string(c_span), styles[c_span.style.id])
                    text_line.append(text_span)
                # If the line is empty then start a new block
                if not bool(text_line) and bool(text_block):
                    blocks.append(text_block)
                    text_block = TextBlock(self)
                else:
                    text_block.append(text_line)
            if bool(text_block):
                blocks.append(text_block)

        blocks.sort()

        return blocks

####################################################################################################

class TextBlocks(object):

    ##############################################

    def __init__(self):

        self._blocks = []
        self._sorted_blocks = None

    ##############################################

    def __iter__(self):
        
        return iter(self._blocks)

    ##############################################

    def sorted_iter(self):
        
        return iter(self._sorted_blocks)

    ##############################################

    def __getitem__(self, index):

        return self._blocks[index]

    ##############################################

    def append(self, text_block):
        
        self._blocks.append(text_block)
        text_block.block_id = len(self._blocks) -1
        self._sorted_blocks = None

    ##############################################

    def sort(self):

        self._sorted_blocks = sorted(self._blocks)
        y_rank = 0
        y = None
        for text_block in self._sorted_blocks:
            if y is None:
                y = text_block.y_inf
            elif y < text_block.y_inf:
                y_rank += 1
            text_block.y_rank = y_rank

####################################################################################################

class TextBase(object):

    ##############################################

    def __init__(self, text=''):

        self._text = text

    ##############################################

    def __len__(self):

        return len(self._text)

    ##############################################

    def __str__(self):

        return self._text

    ##############################################

    def __unicode__(self):

        return self._text

    ##############################################

    def __nonzero__(self):

        return bool(self._text)

    ##############################################

    def word_iterator(self):

        #if ((category in ('Ll', 'Lu')) or (category == 'Nd' and word)):
        #    word += unicode_char.lower()

        word = u''
        non_word = u''
        for char in self._text:
            category = unicodedata.category(char)
            if category in ('Ll', 'Lu', 'Nd'):
                word += char.lower()
            elif word:
                yield word
                word = u''
            else:
                non_word += char
        if word: # Last char was a letter/number
            yield word
        print u'<' + non_word + u'>'

####################################################################################################

class TextBlock(TextBase):

    # block id page/index X
    # text X
    # styles X
    # main_style X
    # length X
    # interval X
    # is centred
    # y rank
    # user tag

    ##############################################

    def __init__(self, text_page):

        # Fixme: parent text_page versus TextBlocks

        super(TextBlock, self).__init__()

        self._block_id = None
        self._y_rank = None
        self._text_page = text_page
        self._interval = None
        self._lines = []
        self._style_frequencies = None

    ##############################################

    @property
    def text_page(self):
        return self._text_page

    ##############################################

    @property
    def styles(self):
        return self._text_page.styles

    ##############################################

    @property
    def block_id(self):
        return self._block_id

    ##############################################

    @block_id.setter
    def block_id(self, block_id):
        self._block_id = block_id

    ##############################################

    @property
    def interval(self):
        return self._interval

    ##############################################

    @property
    def horizontal_margin(self):

        return (self._interval.x.inf - self.text_page.interval.x.inf,
                self.text_page.interval.x.sup - self._interval.x.sup)

    ##############################################

    @property
    def is_centred(self):

        left_margin, right_margin = self.horizontal_margin
        return abs(left_margin - right_margin)/float(min(left_margin, right_margin)) < .1

    ##############################################

    @property
    def is_left_justified(self):

        # value indicates column

        page_width = self.text_page.interval.x.length()
        left_margin, right_margin = self.horizontal_margin
        return left_margin/float(page_width) # < .1

    ##############################################

    @property
    def y_rank(self):
        return self._y_rank

    ##############################################

    @y_rank.setter
    def y_rank(self, y_rank):
        self._y_rank = y_rank

    ##############################################

    @property
    def is_right_justified(self):

        page_width = self.text_page.interval.x.length()
        left_margin, right_margin = self.horizontal_margin
        return right_margin/float(page_width) # < .1

    ##############################################

    @property
    def y_inf(self):
        return self._interval.y.inf

    ##############################################
        
    @property
    def number_of_styles(self):

        return sum([line.number_of_styles for line in self._lines])

    ##############################################

    def __cmp__(self, other):

        return cmp(self.y_inf, other.y_inf)

    ##############################################

    def line_iterator(self):

        return iter(self._lines)

    ##############################################

    def append(self, line):

        self._lines.append(line)
        if self._text:
            self._text += u' '
        self._text += unicode(line)
        if self._interval is not None:
            self._interval |= line.interval
        else:
            self._interval = line.interval

    ##############################################
 
    @property
    def style_frequencies(self):

        if self._style_frequencies is None:
            self._style_frequencies = TextStyleFrequencies()
            for line in self.line_iterator():
                self._style_frequencies += line.style_frequencies()

        return self._style_frequencies

    ##############################################
 
    @property
    def main_style(self):

        main_style_id = self.style_frequencies.max().style_id
        return self.styles[main_style_id]

####################################################################################################

class TextLine(TextBase):

    ##############################################

    def __init__(self, interval):

        super(TextLine, self).__init__()

        self._interval = interval
        self._spans = []

    ##############################################
        
    @property
    def interval(self):
        return self._interval

    ##############################################
        
    @property
    def number_of_styles(self):
        return len(self._spans)

    ##############################################
        
    def __iter__(self):
        
        return iter(self._spans)

    ##############################################

    def append(self, span):

        self._spans.append(span)
        self._text += unicode(span)

    ##############################################
        
    def style_frequencies(self):

        style_frequencies = TextStyleFrequencies()
        for span in self:
            style_id = span.style.id
            count = len(span)
            style_frequencies.fill(style_id, count)
        
        return style_frequencies

####################################################################################################

class TextSpan(TextBase):

    ##############################################

    def __init__(self, text, style):

        super(TextSpan, self).__init__(text)

        self.style = style

####################################################################################################
# 
# End
# 
####################################################################################################