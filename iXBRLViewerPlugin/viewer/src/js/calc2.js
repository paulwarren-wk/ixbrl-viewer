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

import $ from 'jquery';
import { FactSet } from './factset.js';

export function Calc2(inspector, report) {
    this._report = report;
}

Calc2.prototype.dataPointForFact = function(fact) {
    var dps = this._report.calc2DataPoints();
    for (var dp of Object.keys(dps)) {
        for (var f of dps[dp].v) {
            if (f == fact.id) {
                return dp;
            }
        }
    }
    return null;
}

Calc2.prototype.inspectorHTML = function(fact) {
    var dataPoints = this._report.calc2DataPoints();
    var dp = this.dataPointForFact(fact);

    var html = $("<div></div>");

    if (dp !== null) {
        if (dataPoints[dp].i) {
            $("<div></div>").text("inconsistent").appendTo(html);
        }
        for (var f of dataPoints[dp].v) {
            if (f == fact.id) {
                continue;
            }
            $("<div></div>").text(f).appendTo(html);
            var dpf = this._report.getItemById(f);
            if (dpf.f.calc) {
                var list = $("<ul></ul>").appendTo(html);
                var contributingFacts = $.map(dpf.f.calc, (c, i) => this._report.getItemById(c["f"]));
                var factSet = new FactSet(contributingFacts);
                for (var ci of dpf.f.calc) {
                    list.append($("<li></li>").text(factSet.minimallyUniqueLabel(this._report.getItemById(ci["f"]) )));
                }
            }
        }
    }
    return html;
}



