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

    def serialize(self, xmlDocument, fout):
        self._expandEmptyTags(xmlDocument)
        xml = etree.tostring(xmlDocument, method="xml", encoding="utf-8", xml_declaration=True)
        if self.embedViewerFile is not None:
            # '<' in <script> must be escaped in XML, but must not be in HTML
            # Enclose in CDATA to make the XML valid.  CDATA is ignored by
            # HTML, so put CDATA tags in JS comments.
            # Our script contains ']]>', so escape with escaped character in
            # strings, and adjust to "]] >" out of strings.
            # This will break if ]]> appears within a string but is not a
            # complete string.
            with open(self.embedViewerFile, encoding="utf-8") as fin:
                script = fin.read()
                script = re.sub('([\x00-\x08\x0B\x0C\x0E-\x1F])', lambda m: "\\x%02x" % ord(m.group(1)), script)
                script = script.replace('"]]>"', '"\\x5D\\x5D\\x3E"').replace(']]>', ']] >')
                script = "// <![CDATA[\n" + script + "\n// ]]>\n"; 
            xml = xml.decode('utf-8').replace('IXBRL_VIEWER_SCRIPT_PLACEHOLDER', script).encode('utf-8')
        fout.write(xml)
        
