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

inferredFactId = 0

def createInferredFact(builder, dts, viewerData, dp, inferredValue):
    fid = builder.nextFactId()


def serializeCalc2Results(builder, dts):

    calcs = getattr(dts, "calc2Results", None)
    if calcs is None:
        return

    from calc2 import FactBasedDataPointValue, InferredDataPointValue

    dpi = 0
    calcData = {}
    for dp, dpv in calcs.dataPoints().items():
        d = { "v": [] }
        for v in dpv.values():
            if type(v) == FactBasedDataPointValue:
                d[v].append(v.fact.id)
            else:
                pass

        if dpv.inconsistent:
            dpv[i] = True

        calcData[dpi] = d
        dpi += 1

    builder.viewerData["calc2data"] = calcData
        

