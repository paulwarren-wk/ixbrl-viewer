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


// ReportFact represents a fact that is present in the current iXBRL document
// (as opposed to obtained from an external data source)
//
// It can be fetched by ID from the report, and has an associated ixNode from
// the HTML document

import { Fact } from './fact.js';

export function ReportFact(report, factId) {
    Fact.call(this, report, report.data.facts[factId]);
    this._ixNode = report.getIXNodeForFactId(factId);
    this.id = factId;
}

ReportFact.prototype = Object.create(Fact.prototype);
