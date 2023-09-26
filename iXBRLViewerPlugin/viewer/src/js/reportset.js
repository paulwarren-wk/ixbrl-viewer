// See COPYRIGHT.md for copyright information

import { XBRLReport } from './report.js';
import { Fact } from "./fact.js"
import { Footnote } from "./footnote.js"
import { Unit } from "./unit";
import { titleCase, viewerUniqueId } from "./util.js";
import { QName } from "./qname.js";
import { ViewerOptions } from './viewerOptions.js';
import $ from 'jquery'


// Class represents the set of XBRL "target" reports shown in the viewer.
// Each contained report represents the data from a single target document in a
// single iXBRL Document or iXBRL Document Set

export class ReportSet {
    constructor(data) {
        this._data = data;
        this._ixNodeMap = {};
        this.viewerOptions = new ViewerOptions()
    }

    /*
     * Set additional information about facts obtained from parsing the iXBRL.
     */
    setIXNodeMap(ixData) {
        this._ixNodeMap = ixData;
        this._initialize();
    }

    _initialize() {
        this._items = {};
        this.reports = [];
        // Build an array of footnotes IDs in document order so that we can assign
        // numbers to foonotes
        const fnorder = Object.keys(this._ixNodeMap).filter((id) => this._ixNodeMap[id].footnote);
        fnorder.sort((a,b) => this._ixNodeMap[a].docOrderindex - this._ixNodeMap[b].docOrderindex);

        // Create Fact objects for all facts.
        for (const [reportIndex, reportData] of this.reportsData().entries()) {
            const report = new XBRLReport(this, reportData);
            this.reports.push(report);
            for (const [id, factData] of Object.entries(reportData.facts)) {
                const vuid = viewerUniqueId(reportIndex, id);
                this._items[vuid] = new Fact(report, vuid, factData);
            }

            // Now resolve footnote references, creating footnote objects for "normal"
            // footnotes, and finding Fact objects for fact->fact footnotes.  
            //
            // Associate source facts with target footnote/facts to allow two way
            // navigation.
            for (const [id, factData] of Object.entries(reportData.facts)) {
                const vuid = viewerUniqueId(reportIndex, id);
                const fact = this._items[vuid];
                const fns = factData.fn || [];
                fns.forEach((fnid) => {
                    const fnvuid = viewerUniqueId(reportIndex, fnid);
                    var fn = this._items[fnvuid];
                    if (fn === undefined) {
                        fn = new Footnote(fact.report, fnvuid, "Footnote " + (fnorder.indexOf(fnvuid) + 1));
                        this._items[fnvuid] = fn;
                    }
                    // Associate fact with footnote
                    fn.addLinkedFact(fact);
                    fact.addFootnote(fn);
                });
            }
        }
    }



    availableLanguages() {
        return Array.from(this.reports.reduce(
            (langs, report) => new Set([...langs, ...report.availableLanguages()]), 
            new Set()
        ));
    }

    getItemById(id) {
        return this._items[id];
    }

    getIXNodeForItemId(id) {
        return this._ixNodeMap[id] || {};
    }

    facts() {
        return Object.values(this._items).filter(i => i instanceof Fact);
    }

    filingDocuments() {
        return this._data.filingDocuments;
    }

    prefixMap() {
        return this._data.prefixes;
    }

    namespaceGroups() {
        const counts = {};
        $.each(this.facts(), function (i, f) {
            counts[f.conceptQName().prefix] = counts[f.conceptQName().prefix] || 0;
            counts[f.conceptQName().prefix]++;
        });
        const prefixes = Object.keys(counts);
        prefixes.sort(function (a, b) { return counts[b] - counts[a] });
        return prefixes;
    }

    getUsedPrefixes() {
        if (this._usedPrefixes === undefined) {
            this._usedPrefixes = new Set(Object.values(this._items)
                    .filter(f => f instanceof Fact)
                    .map(f => f.getConceptPrefix()));
        }
        return this._usedPrefixes;
    }

    /**
     * Returns a set of OIM format unit strings used by facts on this report. Lazy-loaded.
     * @return {Set[String]} Set of OIM format unit strings
     */
    getUsedUnits() {
        if (this._usedUnits === undefined) {
            this._usedUnits = new Set(Object.values(this._items)
                    .filter(f => f instanceof Fact)
                    .map(f => f.unit()?.value())
                    .filter(f => f)
                    .sort());
        }
        return this._usedUnits;
    }

    /**
     * Returns details about the provided unit. Lazy-loaded once per unit.
     * @param  {String} unitKey  Unit in OIM format
     * @return {Unit}  Unit instance corresponding with provided key
     */
    getUnit(unitKey) {
        if (this._unitsMap === undefined) {
            this._unitsMap = {};
        }
        if (this._unitsMap[unitKey] === undefined) {
            this._unitsMap[unitKey] = new Unit(this, unitKey)
        }
        return this._unitsMap[unitKey];
    }

    getUsedScalesMap() {
        // Do not lazy load. This is language-dependent so needs to re-evaluate after language changes.
        const usedScalesMap = {};
        Object.values(this._items)
            .filter(f => f instanceof Fact)
            .forEach(fact => {
                const scale = fact.scale();
                if (scale !== null && scale !== undefined) {
                    if (!(scale in usedScalesMap)) {
                        usedScalesMap[scale] = new Set();
                    }
                    const labels = usedScalesMap[scale];
                    const label = titleCase(fact.getScaleLabel(scale));
                    if (label && !labels.has(label)) {
                        labels.add(label);
                    }
                }
            });
        return usedScalesMap;
    }

    languageNames() {
        return this._data.languages;
    }

    roleMap() {
        return this._data.roles;
    }

    qname(v) {
        return new QName(this.prefixMap(), v);
    }

    reportsData() {
        return this._data.reports ?? [ this._data ];
    }

    documentSetFiles() {
        return this.reportsData().map((x, n) => (x.docSetFiles ?? []).map(file => ({ index: n, file: file }))).flat();
    }

    isDocumentSet() {
        return this.documentSetFiles().length > 1;
    }

    usesAnchoring() {
        // XXX hard-coded to first report
        return this.reportsData()[0].rels["w-n"] !== undefined;
    }

    hasValidationErrors() {
        return this._data.validation !== undefined && this._data.validation.length > 0;
    }

    validation() {
        return this._data.validation;
    }

    factsForReport(report) {
        return Object.values(this._items).filter(i => i instanceof Fact && i.report == report);
    }
    
}
