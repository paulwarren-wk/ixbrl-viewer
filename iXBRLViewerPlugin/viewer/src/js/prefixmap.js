

export function PrefixMap(map) {
    this._map = map;
    this._generateIndex = 0;
}

PrefixMap.prototype.getURI = function(prefix) {
    return this._map[prefix];
}

PrefixMap.prototype.getPrefix = function (uri) {
    return Object.keys(this._map).filter(p => this._map[p] == uri)[0];
}

PrefixMap.prototype.getOrMakePrefix = function (uri) {
    var p = this.getPrefix(uri);
    if (p !== undefined) {
        return p
    }
    do {
        p = "ns" + ++this._generateIndex;
    } while (this._map[p] !== undefined);

    this._map[p] = uri;
    return p;
}


