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

class Calc2Serializer:

    def __init__(self, builder, dts):
        self.inferredFactIds = dict()
        self.builder = builder
        self.dts = dts
        self.dataPoints = getattr(dts, "calc2Results", None)
        self.relationshipToId = dict()
        self.calcId = 0
        self.relationships = dict()

    def serializeRelationship(self, rel):
        from calc2.calc2model import ConceptSummationRelationship, DimensionAggregationRelationship
        if type(rel) == ConceptSummationRelationship:
            res = {
                "type": "concept",
                "items": [{ "n": self.builder.nsmap.qname(i["concept"]), "w": i["weight"] } for i in rel.items ],
                "total": self.builder.nsmap.qname(rel.total),
            }
        elif type(rel) == DimensionAggregationRelationship:
            res = {
                "type": "dimagg",
                "items": [{ "n": self.builder.nsmap.qname(i), "w": 1 } for i in rel.items],
                "total": self.builder.nsmap.qname(rel.total) if rel.total is not None else 'default',
                "dimension": self.builder.nsmap.qname(rel.dimension),
            }

        return res

    def createInferredFact(self, dp, inferredValue):
        fact = {
            "a": {
                "c": self.builder.nsmap.qname(dp.concept),
                "p": dp.period,
                "u": self.builder.nsmap.qname(dp.unit),
                "e": dp.entity,
            },
            "v": str(inferredValue.value.midpoint),
            "vmin": str(inferredValue.value.a),
            "vmax": str(inferredValue.value.b)
        }
        for dim in dp.taxonomyDefinedDimensions:
            if dp.dimensionValue(dim) is not None:
                fact["a"][self.builder.nsmap.qname(dim)] = self.builder.nsmap.qname(dp.dimensionValue(dim))

        calcId = self.relationshipToId.get(inferredValue.relationship, None)
        if calcId is None:
            self.calcId += 1
            calcId = 'c%d' % self.calcId
            self.relationshipToId[inferredValue.relationship] = calcId
            self.relationships[calcId] = self.serializeRelationship(inferredValue.relationship)

        fact['calc'] = calcId

        return fact

    def idForDataPointValue(self, dp, v):
        from calc2.datapoints import FactBasedDataPointValue, CalculatedDataPointValue
        if type(v) == FactBasedDataPointValue:
            return v.fact.id 
        else:
            ifid = self.inferredFactIds.get(dp, {}).get(v.relationship, None)
            if ifid is None:
                ifid = self.builder.nextFactId()
                self.inferredFactIds.setdefault(dp, {})[v.relationship] = ifid
            return ifid

    def serializeCalc2Results(self):
        if self.dataPoints is None:
            return

        from calc2.datapoints import FactBasedDataPointValue, CalculatedDataPointValue

        dpi = 0
        calcData = {}
        for dp in self.dataPoints.known:
            for v in self.dataPoints.values(dp):
                fid = self.idForDataPointValue(dp, v)
                if type(v) == CalculatedDataPointValue:
                    self.builder.viewerData["facts"][fid] = self.createInferredFact(dp, v)

        self.builder.viewerData["calc2rels"] = self.relationships
        

