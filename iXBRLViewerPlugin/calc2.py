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

inferredFactIds = dict()

def createInferredFact(builder, calcs, dp, inferredValue):
    fact = {
        "a": {
            "c": builder.nsmap.qname(dp.concept),
            "p": dp.period,
            "u": builder.nsmap.qname(dp.unit),
            "e": dp.entity,
        },
        "v": str(inferredValue.value.midpoint),
        "vmin": str(inferredValue.value.a),
        "vmax": str(inferredValue.value.b)
    }
    for dim in dp.taxonomyDefinedDimensions:
        if dp.dimensionValue(dim) is not None:
            fact["a"][builder.nsmap.qname(dim)] = builder.nsmap.qname(dp.dimensionValue(dim))

    fact["calc"] = []
    for c, w in inferredValue.relationship.contributingDataPoints(dp):
        if calcs.getValue(c) is not None:
            fact["calc"].append({ "f": idForDataPointValue(builder, c, calcs.getValue(c)), "w": w })

    return fact

def idForDataPointValue(builder, dp, v):
    from calc2.datapoints import FactBasedDataPointValue, CalculatedDataPointValue
    if type(v) == FactBasedDataPointValue:
        return v.fact.id 
    else:
        ifid = inferredFactIds.get(dp, {}).get(v.relationship, None)
        if ifid is None:
            ifid = builder.nextFactId()
            inferredFactIds.setdefault(dp, {})[v.relationship] = ifid
        return ifid

def serializeCalc2Results(builder, dts):

    calcs = getattr(dts, "calc2Results", None)
    if calcs is None:
        return

    from calc2.datapoints import FactBasedDataPointValue, CalculatedDataPointValue

    dpi = 0
    calcData = {}
    for dp in calcs.known:
        d = { "v": [] }
        for v in calcs.values(dp):
            fid = idForDataPointValue(builder, dp, v)
            d["v"].append(fid)
            if type(v) == CalculatedDataPointValue:
                builder.viewerData["facts"][fid] = createInferredFact(builder, calcs, dp, v)

        if not calcs.isConsistent(dp):
            d["i"] = True

        calcData[dpi] = d
        dpi += 1

    builder.viewerData["calc2data"] = calcData
        

