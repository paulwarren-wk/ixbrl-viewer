import lxml
import sys
import unittest
from unittest.mock import Mock
import io
from .mock_arelle import mock_arelle

mock_arelle()

from iXBRLViewerPlugin.xhtmlserialize import XHTMLSerializer

class TestXHTMLSerializer(unittest.TestCase):

    def _html(self, s):
        return '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>%s</body></html>' % s

    def _checkTagExpansion(self, html_in, html_out):
        writer = XHTMLSerializer()
        doc = lxml.etree.fromstring(self._html(html_in))
        writer._expandEmptyTags(doc)
        self.assertEqual(lxml.etree.tostring(doc, encoding="unicode"), self._html(html_out))

    def test_expandEmptyTags(self):
        self._checkTagExpansion('<div/>', '<div></div>')
        self._checkTagExpansion('<div><span class="fish" /></div>', '<div><span class="fish"></span></div>')

        # Non-expanding tags
        self._checkTagExpansion('<br/>', '<br/>')
        self._checkTagExpansion('<br />', '<br/>')
        self._checkTagExpansion('<hr/>', '<hr/>')
        self._checkTagExpansion('<img />', '<img/>')

        # Mixed content
        self._checkTagExpansion('<div>foo<p /><p>bar</p></div>', '<div>foo<p></p><p>bar</p></div>')

        # Expanded tags that should be empty will be collapsed
        self._checkTagExpansion('<br></br>', '<br/>')

        # Only expand tags in the XHTML namespace
        self._checkTagExpansion('<div xmlns="other" />', '<div xmlns="other"/>')

    def test_serialize(self):
        htmlsrc = self._html("<p>hello</p>")
        doc = lxml.etree.fromstring(htmlsrc)
        f = io.BytesIO()

        writer = XHTMLSerializer()
        writer.serialize(doc, f)

        # XML declaration should be added.
        self.assertEqual(f.getvalue().decode('utf-8'), "<?xml version='1.0' encoding='utf-8'?>\n" + htmlsrc)

    def test_cdata_escape(self):

        writer = XHTMLSerializer()

        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript(r'a=/[]]>/;'), r'a=/[]]\x3E/;')
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript(r'a=/[]]>/;b="]]>";'), r'a=/[]]\x3E/;b="\x5D\x5D\x3E";')
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript(r'a=b/c[[3]]>1/1;'), r'a=b/c[[3]] >1/1;')
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript(r'return /[]]>/;'), r'return /[]]\x3E/;')
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript(r'return/[]]>/;'), r'return/[]]\x3E/;')
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript(r'"\"" == a[b[0]]>5'), r'"\"" == a[b[0]] >5')
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript("/* ]]> */"), "/* ]] > */")
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript("/* ']]>' */"), "/* ']] >' */")
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript('"test ]]> test ";'), '"test \\x5D\\x5D\\x3E test ";')
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript(' a[b[0]]>5; // line comment\n "]]> test ";'), ' a[b[0]] >5; // line comment\n "\\x5D\\x5D\\x3E test ";')
        self.assertEqual(writer.escapeCDATAEndMarkerInJavascript('x = ` "]]>" `;'), 'x = ` "\\x5D\\x5D\\x3E" `;')
