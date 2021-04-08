# Copyright 2019 Workiva Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lxml import etree
import re

class XHTMLSerializer:

    # From https://www.w3.org/TR/html401/index/elements.html
    selfClosableElements = (
        'area', 'base', 'basefont', 'br', 'col', 'frame', 'hr', 'img', 
        'input', 'isindex', 'link', 'meta', 'param'
    )

    def __init__(self, embedViewerFile = None):
        self.embedViewerFile = embedViewerFile

    def _expandEmptyTags(self, xml):
        """
        Expand self-closing tags

        Self-closing tags cause problems for XHTML documents when treated as
        HTML.  Tags that are required to be empty (e.g. <br>) are left as
        self-closing.
        """
        for e in xml.iter('*'):
            m = re.match(r'\{http://www\.w3\.org/1999/xhtml\}(.*)', e.tag)
            if m is not None and m.group(1) not in XHTMLSerializer.selfClosableElements and e.text is None:
                e.text = ''

    #
    # Parse JavaScript and replace occurrences of ]]> with an appropriate
    # altenative:
    #
    #   String literal: "]]>" => "\x5D\x5D\x3E"
    #   Regex literal: /]]>/ => "]]\x3E"
    #   Division or comment: ]]> => ]] >
    #
    def escapeCDATAEndMarkerInJavascript(self, js):
        i = 0
        s = len(js)
        out = ''
        while i < s:
            m = re.match(r'(?s)^(.*?)(/|"|\'|`)', js[i:])
            if m is None:
                out += js[i:].replace(']]>', ']] >')
                break
            i += len(m.group(0))
            out += m.group(0).replace(']]>', ']] >')
            if m.group(2) == "/":
                if js[i] == '/':
                    # line comment
                    m = re.match(r'^/[^\n\r]*', js[i:])
                    out += m.group(0).replace(']]>', ']] >')
                    i += len(m.group(0))
                elif js[i] == '*':
                    # normal comment
                    m = re.match(r'(?s)^\*(.*?)\*/', js[i:])
                    i += len(m.group(0))
                    out += m.group(0).replace(']]>', ']] >')
                else:
                    # Avoid doing a regex search against the end of a long
                    # string
                    # Find the first non-whitespace character before the /
                    x = len(out) - 2
                    while x > 0 and out[x] in " \t\r\n":
                        x -= 1
                    # Any of the following implies a regex literal rather than division
                    if out[x] in "[{(,=:?!&|;" or re.search(r'\breturn$', out[x-6 if x >= 6 else 0:x+1]) is not None:
                        # regex literal
                        m = re.match(r'^(\\.|[^[\\/]|\[\^?.[^]]*\])*/', js[i:])
                        m.group(0)
                        i += len(m.group(0))
                        out += m.group(0).replace(']]>', ']]\\x3E')

            elif m.group(2) in ("'",'"','`'):
                m = re.match(r'(?s)^((?:\\.|[^' + m.group(2) + r'\\])*)' + m.group(2), js[i:])
                if m is None:
                    return out
                i += len(m.group(0))
                string = m.group(0).replace(']]>', '\\x5D\\x5D\\x3E')

                # Also escape any characters which are not valid in CDATA
                out += re.sub('([\x00-\x08\x0B\x0C\x0E-\x1F])', lambda m: "\\x%02x" % ord(m.group(1)), string) 

        return out


    def serialize(self, xmlDocument, fout):
        self._expandEmptyTags(xmlDocument)
        xml = etree.tostring(xmlDocument, method="xml", encoding="utf-8", xml_declaration=True)
        if self.embedViewerFile is not None:
            # '<' in <script> must be escaped in XML, but must not be in HTML
            # Enclose in CDATA to make the XML valid.  CDATA is ignored by
            # HTML, so put CDATA tags in JS comments.
            #
            # Any ']]>' in the JS needs escaping, but how it's escaped depends on context.
            with open(self.embedViewerFile, encoding="utf-8") as fin:
                script = "// <![CDATA[\n" + self.escapeCDATAEndMarkerInJavascript(fin.read()) + "\n// ]]>\n"; 
            xml = xml.decode('utf-8').replace('IXBRL_VIEWER_SCRIPT_PLACEHOLDER', script).encode('utf-8')
        fout.write(xml)
        
