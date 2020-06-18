// Copyright 2019 Workiva Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import lunr from 'lunr'
import $ from 'jquery'
import { setDefault } from './util.js';

export function ReportSearch (report) {
    this._report = report;
    this.buildSearchIndex();
}

ReportSearch.prototype.buildSearchIndex = function () {
    var docs = {};
    var dims = {};
    var facts = this._report.facts();
    this.periods = {};
    for (var i = 0; i < facts.length; i++) {
        var f = facts[i];
        var factDoc = { "id": "f" + f.id };
        factDoc.date = f.periodTo();
        factDoc.startDate = f.periodFrom();
        docs[ factDoc.id ] = factDoc;

        for (const [dname, dvalue] of Object.entries(f.dimensions())) {
            const key = 'd' + dname + '/' + dvalue
            if (!(key in docs)) {
                docs[key] = {
                    "id": key,
                    "label": this._report.getLabel(dvalue, "std")
                }
            }
        }

        var ckey = 'c' + f.conceptName();
        if (!(ckey in docs)) {
            var conceptDoc = {};
            conceptDoc.label = f.getLabel("std");
            conceptDoc.concept = f.conceptQName().localname;
            conceptDoc.doc = f.getLabel("doc");
            conceptDoc.ref = f.concept().referenceValuesAsString();
            conceptDoc.id = ckey;
            const wider = f.widerConcepts();
            if (wider.length > 0) {
                conceptDoc.widerConcept = this._report.qname(wider[0]).localname;
                conceptDoc.widerLabel = this._report.getLabel(wider[0],"std");
                conceptDoc.widerDoc = this._report.getLabel(wider[0],"doc");
            }
            docs[ckey] = conceptDoc;
        }

        var p = f.period();
        if (p) {
            this.periods[p.key()] = p.toString();
        }

    }
    this._searchIndex = lunr(function () {
      this.ref('id');
      this.field('label');
      this.field('concept');
      this.field('startDate');
      this.field('date');
      this.field('doc');
      this.field('ref');
      this.field('widerLabel');
      this.field('widerDoc');
      this.field('widerConcept');

      for (const doc of Object.values(docs)) { 
        this.add(doc);
      }
    })
}

ReportSearch.prototype.search = function (s) {
    var rr = this._searchIndex.search(s.searchString);
    var results = []
    var searchIndex = this;

    var resultMap = {};

    rr.forEach((r,i) => {
        var items;
        const resultType = r.ref[0];
        const resultName = r.ref.substring(1);
        if (resultType == 'f') {
            items = [ searchIndex._report.getItemById(resultName) ];
        }
        else if (resultType == 'c') {
            items = this._report.getFactsByConcept(resultName);
        }
        else if (resultType == 'd') {
            const [dname, dvalue] = resultName.split('/');
            items = this._report.getFactsByDimensionValue(dname, dvalue);
        }
        for (const item of items) {
            if (
                (item.isHidden() ? s.showHiddenFacts : s.showVisibleFacts) &&
                (s.periodFilter == '*' || item.period().key() == s.periodFilter) &&
                (s.conceptTypeFilter == '*' || s.conceptTypeFilter == (item.isNumeric() ? 'numeric' : 'text'))) {

                setDefault(resultMap, item.id, { "fact": item, "score": 0}).score += r.score;
            }
        }
    });
    return Object.values(resultMap).sort((a,b) => b.score - a.score);
}
