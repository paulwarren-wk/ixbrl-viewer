import $ from "jquery";
import { Fact } from './fact.js';

var URL = "https://api.xbrl.us";

export function XBRLAPI() {
    this._token = null;

}

XBRLAPI.prototype.aspectsToQuery = function(aspects) {
    var query = {};
    var dn = 0;
    Object.keys(aspects).forEach(function (n) {
        var v = aspects[n];
        if (n == 'c' && v) {
            query['concept.local-name'] = v.localname;
        }
        else if (n == 'e' && v) {
            query['entity.cik'] = v.localname;
        }
        else if (n == 'fp' && v) {
            query['period.fiscal-period'] = v;
        }
        else if (n.indexOf(':') > -1 ) {
            var x = n.split(':', 2);
            if (v) {
                query['aspect.' + x[1]] = v.localname;
            }
            dn++;
        }
        else {
            console.log("Unsupported query dimension: " + n);
        }
    });
    query['dimensions.count'] = dn
    query['fact.ultimus'] = true;
    return query;

}

XBRLAPI.prototype._fuzzyFindQName = function(report, ns, local) {
    var qname = report.conceptFuzzyFind(ns, local);
    if (qname === undefined) {
        qname = report.prefixMap.getOrMakePrefix(ns) + ':' + local;
    }
    console.log("{" + ns + "}" + local + " => " + qname);
    return qname
}

XBRLAPI.prototype.buildFacts = function(report, data) {
    var facts = data.data.map(d => {
        var fd = {
            'a': {
                'c': this._fuzzyFindQName(report, d['concept.namespace'], d['concept.local-name']),
                'p': d['period.instant'] || (d['period.start'] + '/' + d['period.end']),
                'e': report.prefixMap.getPrefix("http://www.sec.gov/CIK") + ':' + d['entity.cik']
            },
            'v': d['fact.value'],
        }
        var u = d['unit.qname'].match(/^\{(.*)\}(.*)$/);
        fd.a.u = report.prefixMap.getPrefix(u[1]) + ':' + u[2];

        if (d['dimensions']) {
            d['dimensions'].forEach(dim => {
                fd.a[this._fuzzyFindQName(report, dim.dimension_namespace, dim.dimension_local_name)] = this._fuzzyFindQName(report, dim.member_namespace, dim.member_local_name);
            });
        }
        
        return new Fact(report, fd);
    });
    console.log(facts);
    return facts;
}

XBRLAPI.prototype.getFacts = function (report, aspects, callback) {
    var query = this.aspectsToQuery(aspects);
    console.log(query);
    var api = this;
    query.fields = "fact.value,period.instant,period.end,period.start,dimensions,unit,entity.cik,concept.namespace,concept.local-name,unit.qname";
    var queryFunc = function () {
        console.log(api._token);
        $.ajax(URL + "/api/v1/fact/search", {
            "headers": { "Authorization": "Bearer " + api._token },
            "data": query,
            "success": function (data) {
                console.log("query success");
                console.log(data);
                callback(api.buildFacts(report, data));
            },
            "dataType": "json",
            "error": function (jqhr, stat, error) {
                alert("fail");
                console.log(stat, error);
                callback(null);
            },
        });
    }
    if (!this._token) {
        this.login(queryFunc, function () { callback(null) });
    }
    else {
        queryFunc();
    }

}

XBRLAPI.prototype.login = function (callback, errorCallback) {
    var api = this;
        var data =  {
            "grant_type": "password", 
            "client_id": process.env.XBRLUSAPI_CLIENT_ID,
            "client_secret": process.env.XBRLUSAPI_CLIENT_SECRET,
            "username": process.env.XBRLUSAPI_USERNAME,
            "password": process.env.XBRLUSAPI_PASSWORD
        };
    $.ajax(URL + "/oauth2/token", {
        "data": data,
        "method": "POST",
        "success": function (data) {
            console.log("success");
            api._token = data.access_token;
            callback();
        },
        "dataType": "json",
        "error": function (jqhr, stat, error) {
            alert("fail");
            console.log(stat, error);
            errorCallback();
        }

    });
}
