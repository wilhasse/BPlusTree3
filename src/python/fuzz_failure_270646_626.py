"""
Fuzz test failure reproduction
Seed: 270646
Capacity: 3
Failed at operation: 626
"""

from bplus_tree import BPlusTreeMap
from collections import OrderedDict

def reproduce_failure():
    tree = BPlusTreeMap(capacity=3)
    reference = OrderedDict()

    # Operation 1: get
    assert tree.invariants(), "Invariants failed at step 1"

    # Operation 2: insert
    tree[7213] = 'value_538078'
    reference[7213] = 'value_538078'
    assert tree.invariants(), "Invariants failed at step 2"

    # Operation 3: insert
    tree[9803] = 'value_333944'
    reference[9803] = 'value_333944'
    assert tree.invariants(), "Invariants failed at step 3"

    # Operation 4: get
    assert tree.invariants(), "Invariants failed at step 4"

    # Operation 5: update
    tree[8223] = 'value_27087'
    reference[8223] = 'value_27087'
    assert tree.invariants(), "Invariants failed at step 5"

    # Operation 6: update
    tree[1133] = 'value_535246'
    reference[1133] = 'value_535246'
    assert tree.invariants(), "Invariants failed at step 6"

    # Operation 7: delete
    del tree[1199]
    del reference[1199]
    assert tree.invariants(), "Invariants failed at step 7"

    # Operation 8: delete
    del tree[6414]
    del reference[6414]
    assert tree.invariants(), "Invariants failed at step 8"

    # Operation 9: update
    tree[9905] = 'value_511316'
    reference[9905] = 'value_511316'
    assert tree.invariants(), "Invariants failed at step 9"

    # Operation 10: get
    assert tree.invariants(), "Invariants failed at step 10"

    # Operation 11: delete
    del tree[5825]
    del reference[5825]
    assert tree.invariants(), "Invariants failed at step 11"

    # Operation 12: insert
    tree[1609] = 'value_16707'
    reference[1609] = 'value_16707'
    assert tree.invariants(), "Invariants failed at step 12"

    # Operation 13: get
    assert tree.invariants(), "Invariants failed at step 13"

    # Operation 14: delete
    del tree[9876]
    del reference[9876]
    assert tree.invariants(), "Invariants failed at step 14"

    # Operation 15: insert
    tree[9286] = 'value_24311'
    reference[9286] = 'value_24311'
    assert tree.invariants(), "Invariants failed at step 15"

    # Operation 16: batch_delete
    keys_to_delete = [709, 2440, 1067, 557, 1102, 1487, 1073, 659, 3669, 121, 1434, 8571]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 16"

    # Operation 17: update
    tree[9207] = 'value_612160'
    reference[9207] = 'value_612160'
    assert tree.invariants(), "Invariants failed at step 17"

    # Operation 18: insert
    tree[3669] = 'value_541221'
    reference[3669] = 'value_541221'
    assert tree.invariants(), "Invariants failed at step 18"

    # Operation 19: update
    tree[163] = 'value_93664'
    reference[163] = 'value_93664'
    assert tree.invariants(), "Invariants failed at step 19"

    # Operation 20: update
    tree[2299] = 'value_593518'
    reference[2299] = 'value_593518'
    assert tree.invariants(), "Invariants failed at step 20"

    # Operation 21: delete
    del tree[1854]
    del reference[1854]
    assert tree.invariants(), "Invariants failed at step 21"

    # Operation 22: delete
    del tree[725]
    del reference[725]
    assert tree.invariants(), "Invariants failed at step 22"

    # Operation 23: delete
    del tree[137]
    del reference[137]
    assert tree.invariants(), "Invariants failed at step 23"

    # Operation 24: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 24"

    # Operation 25: delete
    del tree[924]
    del reference[924]
    assert tree.invariants(), "Invariants failed at step 25"

    # Operation 26: delete
    del tree[1069]
    del reference[1069]
    assert tree.invariants(), "Invariants failed at step 26"

    # Operation 27: delete
    del tree[1387]
    del reference[1387]
    assert tree.invariants(), "Invariants failed at step 27"

    # Operation 28: insert
    tree[138] = 'value_448846'
    reference[138] = 'value_448846'
    assert tree.invariants(), "Invariants failed at step 28"

    # Operation 29: insert
    tree[9674] = 'value_205126'
    reference[9674] = 'value_205126'
    assert tree.invariants(), "Invariants failed at step 29"

    # Operation 30: update
    tree[4409] = 'value_395655'
    reference[4409] = 'value_395655'
    assert tree.invariants(), "Invariants failed at step 30"

    # Operation 31: insert
    tree[6671] = 'value_303983'
    reference[6671] = 'value_303983'
    assert tree.invariants(), "Invariants failed at step 31"

    # Operation 32: batch_delete
    keys_to_delete = [6085, 3402, 1229, 209, 3633, 957]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 32"

    # Operation 33: get
    assert tree.invariants(), "Invariants failed at step 33"

    # Operation 34: get
    assert tree.invariants(), "Invariants failed at step 34"

    # Operation 35: delete
    del tree[691]
    del reference[691]
    assert tree.invariants(), "Invariants failed at step 35"

    # Operation 36: update
    tree[5259] = 'value_338125'
    reference[5259] = 'value_338125'
    assert tree.invariants(), "Invariants failed at step 36"

    # Operation 37: get
    assert tree.invariants(), "Invariants failed at step 37"

    # Operation 38: insert
    tree[8779] = 'value_927700'
    reference[8779] = 'value_927700'
    assert tree.invariants(), "Invariants failed at step 38"

    # Operation 39: get
    assert tree.invariants(), "Invariants failed at step 39"

    # Operation 40: delete
    del tree[650]
    del reference[650]
    assert tree.invariants(), "Invariants failed at step 40"

    # Operation 41: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 41"

    # Operation 42: batch_delete
    keys_to_delete = [5059, 4, 1202, 6291, 2323, 6329, 1180, 8190]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 42"

    # Operation 43: delete
    del tree[8007]
    del reference[8007]
    assert tree.invariants(), "Invariants failed at step 43"

    # Operation 44: update
    tree[7636] = 'value_833180'
    reference[7636] = 'value_833180'
    assert tree.invariants(), "Invariants failed at step 44"

    # Operation 45: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 45"

    # Operation 46: update
    tree[250] = 'value_827624'
    reference[250] = 'value_827624'
    assert tree.invariants(), "Invariants failed at step 46"

    # Operation 47: get
    assert tree.invariants(), "Invariants failed at step 47"

    # Operation 48: update
    tree[2596] = 'value_705910'
    reference[2596] = 'value_705910'
    assert tree.invariants(), "Invariants failed at step 48"

    # Operation 49: delete
    del tree[2236]
    del reference[2236]
    assert tree.invariants(), "Invariants failed at step 49"

    # Operation 50: delete
    del tree[5663]
    del reference[5663]
    assert tree.invariants(), "Invariants failed at step 50"

    # Operation 51: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 51"

    # Operation 52: delete
    del tree[6164]
    del reference[6164]
    assert tree.invariants(), "Invariants failed at step 52"

    # Operation 53: insert
    tree[9241] = 'value_320363'
    reference[9241] = 'value_320363'
    assert tree.invariants(), "Invariants failed at step 53"

    # Operation 54: batch_delete
    keys_to_delete = [1409, 1145, 5511, 5192, 1544, 4940, 2381, 46, 370, 25, 2238, 95]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 54"

    # Operation 55: get
    assert tree.invariants(), "Invariants failed at step 55"

    # Operation 56: insert
    tree[9049] = 'value_370716'
    reference[9049] = 'value_370716'
    assert tree.invariants(), "Invariants failed at step 56"

    # Operation 57: delete
    del tree[4226]
    del reference[4226]
    assert tree.invariants(), "Invariants failed at step 57"

    # Operation 58: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 58"

    # Operation 59: batch_delete
    keys_to_delete = [380, 9298, 3851, 796]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 59"

    # Operation 60: update
    tree[1290] = 'value_457224'
    reference[1290] = 'value_457224'
    assert tree.invariants(), "Invariants failed at step 60"

    # Operation 61: batch_delete
    keys_to_delete = [64, 5826, 6679, 458, 1330, 118, 8758, 1117]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 61"

    # Operation 62: delete
    del tree[544]
    del reference[544]
    assert tree.invariants(), "Invariants failed at step 62"

    # Operation 63: update
    tree[526] = 'value_657759'
    reference[526] = 'value_657759'
    assert tree.invariants(), "Invariants failed at step 63"

    # Operation 64: update
    tree[503] = 'value_23800'
    reference[503] = 'value_23800'
    assert tree.invariants(), "Invariants failed at step 64"

    # Operation 65: get
    assert tree.invariants(), "Invariants failed at step 65"

    # Operation 66: delete
    del tree[8050]
    del reference[8050]
    assert tree.invariants(), "Invariants failed at step 66"

    # Operation 67: get
    assert tree.invariants(), "Invariants failed at step 67"

    # Operation 68: update
    tree[53] = 'value_994067'
    reference[53] = 'value_994067'
    assert tree.invariants(), "Invariants failed at step 68"

    # Operation 69: insert
    tree[2664] = 'value_732566'
    reference[2664] = 'value_732566'
    assert tree.invariants(), "Invariants failed at step 69"

    # Operation 70: delete
    del tree[5566]
    del reference[5566]
    assert tree.invariants(), "Invariants failed at step 70"

    # Operation 71: delete
    del tree[1420]
    del reference[1420]
    assert tree.invariants(), "Invariants failed at step 71"

    # Operation 72: delete
    del tree[376]
    del reference[376]
    assert tree.invariants(), "Invariants failed at step 72"

    # Operation 73: insert
    tree[2448] = 'value_407168'
    reference[2448] = 'value_407168'
    assert tree.invariants(), "Invariants failed at step 73"

    # Operation 74: update
    tree[263] = 'value_56530'
    reference[263] = 'value_56530'
    assert tree.invariants(), "Invariants failed at step 74"

    # Operation 75: delete
    del tree[8279]
    del reference[8279]
    assert tree.invariants(), "Invariants failed at step 75"

    # Operation 76: delete
    del tree[7728]
    del reference[7728]
    assert tree.invariants(), "Invariants failed at step 76"

    # Operation 77: insert
    tree[1170] = 'value_999459'
    reference[1170] = 'value_999459'
    assert tree.invariants(), "Invariants failed at step 77"

    # Operation 78: batch_delete
    keys_to_delete = [9648, 3337, 3682, 1237]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 78"

    # Operation 79: insert
    tree[3335] = 'value_727997'
    reference[3335] = 'value_727997'
    assert tree.invariants(), "Invariants failed at step 79"

    # Operation 80: batch_delete
    keys_to_delete = [6529, 1826, 2563, 1060, 1361, 3351, 2264, 703]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 80"

    # Operation 81: delete
    del tree[1184]
    del reference[1184]
    assert tree.invariants(), "Invariants failed at step 81"

    # Operation 82: get
    assert tree.invariants(), "Invariants failed at step 82"

    # Operation 83: delete
    del tree[1124]
    del reference[1124]
    assert tree.invariants(), "Invariants failed at step 83"

    # Operation 84: get
    assert tree.invariants(), "Invariants failed at step 84"

    # Operation 85: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 85"

    # Operation 86: insert
    tree[2300] = 'value_560660'
    reference[2300] = 'value_560660'
    assert tree.invariants(), "Invariants failed at step 86"

    # Operation 87: batch_delete
    keys_to_delete = [1442, 419, 5157, 3335, 9546, 1451, 5098, 430, 754, 1303, 7518, 639]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 87"

    # Operation 88: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 88"

    # Operation 89: batch_delete
    keys_to_delete = [514, 5252, 1512, 9743, 625, 3547, 5469, 2015]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 89"

    # Operation 90: batch_delete
    keys_to_delete = [769, 1925, 7627, 2732, 845, 331, 5584, 598, 886]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 90"

    # Operation 91: insert
    tree[5572] = 'value_388199'
    reference[5572] = 'value_388199'
    assert tree.invariants(), "Invariants failed at step 91"

    # Operation 92: get
    assert tree.invariants(), "Invariants failed at step 92"

    # Operation 93: update
    tree[1207] = 'value_291927'
    reference[1207] = 'value_291927'
    assert tree.invariants(), "Invariants failed at step 93"

    # Operation 94: get
    assert tree.invariants(), "Invariants failed at step 94"

    # Operation 95: insert
    tree[4066] = 'value_599560'
    reference[4066] = 'value_599560'
    assert tree.invariants(), "Invariants failed at step 95"

    # Operation 96: insert
    tree[1365] = 'value_620434'
    reference[1365] = 'value_620434'
    assert tree.invariants(), "Invariants failed at step 96"

    # Operation 97: insert
    tree[3848] = 'value_595724'
    reference[3848] = 'value_595724'
    assert tree.invariants(), "Invariants failed at step 97"

    # Operation 98: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 98"

    # Operation 99: delete
    del tree[619]
    del reference[619]
    assert tree.invariants(), "Invariants failed at step 99"

    # Operation 100: get
    assert tree.invariants(), "Invariants failed at step 100"

    # Operation 101: batch_delete
    keys_to_delete = [1220, 143, 1106, 2994, 5270, 5116]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 101"

    # Operation 102: insert
    tree[7942] = 'value_58964'
    reference[7942] = 'value_58964'
    assert tree.invariants(), "Invariants failed at step 102"

    # Operation 103: insert
    tree[4778] = 'value_863107'
    reference[4778] = 'value_863107'
    assert tree.invariants(), "Invariants failed at step 103"

    # Operation 104: delete
    del tree[1127]
    del reference[1127]
    assert tree.invariants(), "Invariants failed at step 104"

    # Operation 105: delete
    del tree[1165]
    del reference[1165]
    assert tree.invariants(), "Invariants failed at step 105"

    # Operation 106: insert
    tree[3164] = 'value_570654'
    reference[3164] = 'value_570654'
    assert tree.invariants(), "Invariants failed at step 106"

    # Operation 107: batch_delete
    keys_to_delete = [868, 744, 1609, 9674, 3083, 364, 5268, 503, 569, 4698]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 107"

    # Operation 108: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 108"

    # Operation 109: delete
    del tree[4763]
    del reference[4763]
    assert tree.invariants(), "Invariants failed at step 109"

    # Operation 110: insert
    tree[8326] = 'value_931899'
    reference[8326] = 'value_931899'
    assert tree.invariants(), "Invariants failed at step 110"

    # Operation 111: get
    assert tree.invariants(), "Invariants failed at step 111"

    # Operation 112: update
    tree[9614] = 'value_682474'
    reference[9614] = 'value_682474'
    assert tree.invariants(), "Invariants failed at step 112"

    # Operation 113: get
    assert tree.invariants(), "Invariants failed at step 113"

    # Operation 114: batch_delete
    keys_to_delete = [3009, 1157, 8101, 6536, 8490, 971, 146, 6037, 1175]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 114"

    # Operation 115: delete
    del tree[1255]
    del reference[1255]
    assert tree.invariants(), "Invariants failed at step 115"

    # Operation 116: update
    tree[4211] = 'value_872673'
    reference[4211] = 'value_872673'
    assert tree.invariants(), "Invariants failed at step 116"

    # Operation 117: update
    tree[1424] = 'value_538960'
    reference[1424] = 'value_538960'
    assert tree.invariants(), "Invariants failed at step 117"

    # Operation 118: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 118"

    # Operation 119: update
    tree[1328] = 'value_795933'
    reference[1328] = 'value_795933'
    assert tree.invariants(), "Invariants failed at step 119"

    # Operation 120: get
    assert tree.invariants(), "Invariants failed at step 120"

    # Operation 121: delete
    del tree[1221]
    del reference[1221]
    assert tree.invariants(), "Invariants failed at step 121"

    # Operation 122: delete
    del tree[5821]
    del reference[5821]
    assert tree.invariants(), "Invariants failed at step 122"

    # Operation 123: update
    tree[1076] = 'value_64674'
    reference[1076] = 'value_64674'
    assert tree.invariants(), "Invariants failed at step 123"

    # Operation 124: delete
    del tree[32]
    del reference[32]
    assert tree.invariants(), "Invariants failed at step 124"

    # Operation 125: insert
    tree[1869] = 'value_801884'
    reference[1869] = 'value_801884'
    assert tree.invariants(), "Invariants failed at step 125"

    # Operation 126: delete
    del tree[2664]
    del reference[2664]
    assert tree.invariants(), "Invariants failed at step 126"

    # Operation 127: get
    assert tree.invariants(), "Invariants failed at step 127"

    # Operation 128: update
    tree[616] = 'value_931840'
    reference[616] = 'value_931840'
    assert tree.invariants(), "Invariants failed at step 128"

    # Operation 129: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 129"

    # Operation 130: get
    assert tree.invariants(), "Invariants failed at step 130"

    # Operation 131: update
    tree[6561] = 'value_901484'
    reference[6561] = 'value_901484'
    assert tree.invariants(), "Invariants failed at step 131"

    # Operation 132: insert
    tree[2855] = 'value_181459'
    reference[2855] = 'value_181459'
    assert tree.invariants(), "Invariants failed at step 132"

    # Operation 133: update
    tree[7716] = 'value_223357'
    reference[7716] = 'value_223357'
    assert tree.invariants(), "Invariants failed at step 133"

    # Operation 134: insert
    tree[8940] = 'value_268056'
    reference[8940] = 'value_268056'
    assert tree.invariants(), "Invariants failed at step 134"

    # Operation 135: insert
    tree[6315] = 'value_479960'
    reference[6315] = 'value_479960'
    assert tree.invariants(), "Invariants failed at step 135"

    # Operation 136: get
    assert tree.invariants(), "Invariants failed at step 136"

    # Operation 137: update
    tree[1438] = 'value_84428'
    reference[1438] = 'value_84428'
    assert tree.invariants(), "Invariants failed at step 137"

    # Operation 138: get
    assert tree.invariants(), "Invariants failed at step 138"

    # Operation 139: insert
    tree[6474] = 'value_24072'
    reference[6474] = 'value_24072'
    assert tree.invariants(), "Invariants failed at step 139"

    # Operation 140: insert
    tree[408] = 'value_114936'
    reference[408] = 'value_114936'
    assert tree.invariants(), "Invariants failed at step 140"

    # Operation 141: delete
    del tree[5919]
    del reference[5919]
    assert tree.invariants(), "Invariants failed at step 141"

    # Operation 142: get
    assert tree.invariants(), "Invariants failed at step 142"

    # Operation 143: get
    assert tree.invariants(), "Invariants failed at step 143"

    # Operation 144: delete
    del tree[8895]
    del reference[8895]
    assert tree.invariants(), "Invariants failed at step 144"

    # Operation 145: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 145"

    # Operation 146: insert
    tree[6705] = 'value_670415'
    reference[6705] = 'value_670415'
    assert tree.invariants(), "Invariants failed at step 146"

    # Operation 147: get
    assert tree.invariants(), "Invariants failed at step 147"

    # Operation 148: delete
    del tree[3679]
    del reference[3679]
    assert tree.invariants(), "Invariants failed at step 148"

    # Operation 149: delete
    del tree[7103]
    del reference[7103]
    assert tree.invariants(), "Invariants failed at step 149"

    # Operation 150: get
    assert tree.invariants(), "Invariants failed at step 150"

    # Operation 151: update
    tree[992] = 'value_666043'
    reference[992] = 'value_666043'
    assert tree.invariants(), "Invariants failed at step 151"

    # Operation 152: insert
    tree[6276] = 'value_530624'
    reference[6276] = 'value_530624'
    assert tree.invariants(), "Invariants failed at step 152"

    # Operation 153: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 153"

    # Operation 154: insert
    tree[6639] = 'value_680614'
    reference[6639] = 'value_680614'
    assert tree.invariants(), "Invariants failed at step 154"

    # Operation 155: batch_delete
    keys_to_delete = [7716, 5998, 7439, 4402, 1078, 8059]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 155"

    # Operation 156: insert
    tree[3440] = 'value_993388'
    reference[3440] = 'value_993388'
    assert tree.invariants(), "Invariants failed at step 156"

    # Operation 157: batch_delete
    keys_to_delete = [3363, 7753, 1007, 1429, 3164, 349]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 157"

    # Operation 158: delete
    del tree[9635]
    del reference[9635]
    assert tree.invariants(), "Invariants failed at step 158"

    # Operation 159: batch_delete
    keys_to_delete = [1533, 7419, 8277, 1238]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 159"

    # Operation 160: insert
    tree[1901] = 'value_338627'
    reference[1901] = 'value_338627'
    assert tree.invariants(), "Invariants failed at step 160"

    # Operation 161: batch_delete
    keys_to_delete = [9988, 746, 8299, 268, 7919, 8752, 1873, 3832, 1693]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 161"

    # Operation 162: update
    tree[9207] = 'value_297471'
    reference[9207] = 'value_297471'
    assert tree.invariants(), "Invariants failed at step 162"

    # Operation 163: insert
    tree[2215] = 'value_80721'
    reference[2215] = 'value_80721'
    assert tree.invariants(), "Invariants failed at step 163"

    # Operation 164: get
    assert tree.invariants(), "Invariants failed at step 164"

    # Operation 165: delete
    del tree[8676]
    del reference[8676]
    assert tree.invariants(), "Invariants failed at step 165"

    # Operation 166: delete
    del tree[4832]
    del reference[4832]
    assert tree.invariants(), "Invariants failed at step 166"

    # Operation 167: get
    assert tree.invariants(), "Invariants failed at step 167"

    # Operation 168: delete
    del tree[1208]
    del reference[1208]
    assert tree.invariants(), "Invariants failed at step 168"

    # Operation 169: get
    assert tree.invariants(), "Invariants failed at step 169"

    # Operation 170: delete
    del tree[2797]
    del reference[2797]
    assert tree.invariants(), "Invariants failed at step 170"

    # Operation 171: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 171"

    # Operation 172: insert
    tree[4044] = 'value_383456'
    reference[4044] = 'value_383456'
    assert tree.invariants(), "Invariants failed at step 172"

    # Operation 173: insert
    tree[262] = 'value_677611'
    reference[262] = 'value_677611'
    assert tree.invariants(), "Invariants failed at step 173"

    # Operation 174: delete
    del tree[4464]
    del reference[4464]
    assert tree.invariants(), "Invariants failed at step 174"

    # Operation 175: update
    tree[1402] = 'value_818960'
    reference[1402] = 'value_818960'
    assert tree.invariants(), "Invariants failed at step 175"

    # Operation 176: get
    assert tree.invariants(), "Invariants failed at step 176"

    # Operation 177: insert
    tree[448] = 'value_877515'
    reference[448] = 'value_877515'
    assert tree.invariants(), "Invariants failed at step 177"

    # Operation 178: delete
    del tree[1424]
    del reference[1424]
    assert tree.invariants(), "Invariants failed at step 178"

    # Operation 179: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 179"

    # Operation 180: update
    tree[3858] = 'value_17123'
    reference[3858] = 'value_17123'
    assert tree.invariants(), "Invariants failed at step 180"

    # Operation 181: delete
    del tree[50]
    del reference[50]
    assert tree.invariants(), "Invariants failed at step 181"

    # Operation 182: get
    assert tree.invariants(), "Invariants failed at step 182"

    # Operation 183: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 183"

    # Operation 184: insert
    tree[8579] = 'value_583230'
    reference[8579] = 'value_583230'
    assert tree.invariants(), "Invariants failed at step 184"

    # Operation 185: delete
    del tree[9090]
    del reference[9090]
    assert tree.invariants(), "Invariants failed at step 185"

    # Operation 186: delete
    del tree[686]
    del reference[686]
    assert tree.invariants(), "Invariants failed at step 186"

    # Operation 187: delete
    del tree[683]
    del reference[683]
    assert tree.invariants(), "Invariants failed at step 187"

    # Operation 188: get
    assert tree.invariants(), "Invariants failed at step 188"

    # Operation 189: get
    assert tree.invariants(), "Invariants failed at step 189"

    # Operation 190: insert
    tree[5827] = 'value_822897'
    reference[5827] = 'value_822897'
    assert tree.invariants(), "Invariants failed at step 190"

    # Operation 191: update
    tree[3031] = 'value_587446'
    reference[3031] = 'value_587446'
    assert tree.invariants(), "Invariants failed at step 191"

    # Operation 192: get
    assert tree.invariants(), "Invariants failed at step 192"

    # Operation 193: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 193"

    # Operation 194: delete
    del tree[6315]
    del reference[6315]
    assert tree.invariants(), "Invariants failed at step 194"

    # Operation 195: delete
    del tree[2055]
    del reference[2055]
    assert tree.invariants(), "Invariants failed at step 195"

    # Operation 196: insert
    tree[4968] = 'value_48376'
    reference[4968] = 'value_48376'
    assert tree.invariants(), "Invariants failed at step 196"

    # Operation 197: get
    assert tree.invariants(), "Invariants failed at step 197"

    # Operation 198: update
    tree[475] = 'value_939464'
    reference[475] = 'value_939464'
    assert tree.invariants(), "Invariants failed at step 198"

    # Operation 199: insert
    tree[5322] = 'value_610616'
    reference[5322] = 'value_610616'
    assert tree.invariants(), "Invariants failed at step 199"

    # Operation 200: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 200"

    # Operation 201: insert
    tree[816] = 'value_118625'
    reference[816] = 'value_118625'
    assert tree.invariants(), "Invariants failed at step 201"

    # Operation 202: insert
    tree[2449] = 'value_242206'
    reference[2449] = 'value_242206'
    assert tree.invariants(), "Invariants failed at step 202"

    # Operation 203: update
    tree[8326] = 'value_772893'
    reference[8326] = 'value_772893'
    assert tree.invariants(), "Invariants failed at step 203"

    # Operation 204: update
    tree[7850] = 'value_964063'
    reference[7850] = 'value_964063'
    assert tree.invariants(), "Invariants failed at step 204"

    # Operation 205: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 205"

    # Operation 206: get
    assert tree.invariants(), "Invariants failed at step 206"

    # Operation 207: insert
    tree[5914] = 'value_200179'
    reference[5914] = 'value_200179'
    assert tree.invariants(), "Invariants failed at step 207"

    # Operation 208: get
    assert tree.invariants(), "Invariants failed at step 208"

    # Operation 209: get
    assert tree.invariants(), "Invariants failed at step 209"

    # Operation 210: insert
    tree[1840] = 'value_851964'
    reference[1840] = 'value_851964'
    assert tree.invariants(), "Invariants failed at step 210"

    # Operation 211: get
    assert tree.invariants(), "Invariants failed at step 211"

    # Operation 212: insert
    tree[6914] = 'value_578065'
    reference[6914] = 'value_578065'
    assert tree.invariants(), "Invariants failed at step 212"

    # Operation 213: get
    assert tree.invariants(), "Invariants failed at step 213"

    # Operation 214: get
    assert tree.invariants(), "Invariants failed at step 214"

    # Operation 215: update
    tree[88] = 'value_753'
    reference[88] = 'value_753'
    assert tree.invariants(), "Invariants failed at step 215"

    # Operation 216: get
    assert tree.invariants(), "Invariants failed at step 216"

    # Operation 217: get
    assert tree.invariants(), "Invariants failed at step 217"

    # Operation 218: get
    assert tree.invariants(), "Invariants failed at step 218"

    # Operation 219: get
    assert tree.invariants(), "Invariants failed at step 219"

    # Operation 220: batch_delete
    keys_to_delete = [8416, 7489, 8610, 73, 110, 2449, 466, 8018, 1396, 788, 383]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 220"

    # Operation 221: delete
    del tree[1492]
    del reference[1492]
    assert tree.invariants(), "Invariants failed at step 221"

    # Operation 222: get
    assert tree.invariants(), "Invariants failed at step 222"

    # Operation 223: get
    assert tree.invariants(), "Invariants failed at step 223"

    # Operation 224: update
    tree[1352] = 'value_932750'
    reference[1352] = 'value_932750'
    assert tree.invariants(), "Invariants failed at step 224"

    # Operation 225: delete
    del tree[80]
    del reference[80]
    assert tree.invariants(), "Invariants failed at step 225"

    # Operation 226: get
    assert tree.invariants(), "Invariants failed at step 226"

    # Operation 227: insert
    tree[4377] = 'value_229381'
    reference[4377] = 'value_229381'
    assert tree.invariants(), "Invariants failed at step 227"

    # Operation 228: insert
    tree[2753] = 'value_482567'
    reference[2753] = 'value_482567'
    assert tree.invariants(), "Invariants failed at step 228"

    # Operation 229: update
    tree[4614] = 'value_195433'
    reference[4614] = 'value_195433'
    assert tree.invariants(), "Invariants failed at step 229"

    # Operation 230: get
    assert tree.invariants(), "Invariants failed at step 230"

    # Operation 231: insert
    tree[513] = 'value_116061'
    reference[513] = 'value_116061'
    assert tree.invariants(), "Invariants failed at step 231"

    # Operation 232: insert
    tree[7606] = 'value_510519'
    reference[7606] = 'value_510519'
    assert tree.invariants(), "Invariants failed at step 232"

    # Operation 233: insert
    tree[8959] = 'value_11747'
    reference[8959] = 'value_11747'
    assert tree.invariants(), "Invariants failed at step 233"

    # Operation 234: update
    tree[8940] = 'value_739557'
    reference[8940] = 'value_739557'
    assert tree.invariants(), "Invariants failed at step 234"

    # Operation 235: batch_delete
    keys_to_delete = [263, 1481, 8714, 4041, 6258]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 235"

    # Operation 236: get
    assert tree.invariants(), "Invariants failed at step 236"

    # Operation 237: update
    tree[2645] = 'value_559641'
    reference[2645] = 'value_559641'
    assert tree.invariants(), "Invariants failed at step 237"

    # Operation 238: insert
    tree[2021] = 'value_110682'
    reference[2021] = 'value_110682'
    assert tree.invariants(), "Invariants failed at step 238"

    # Operation 239: delete
    del tree[4371]
    del reference[4371]
    assert tree.invariants(), "Invariants failed at step 239"

    # Operation 240: delete
    del tree[1366]
    del reference[1366]
    assert tree.invariants(), "Invariants failed at step 240"

    # Operation 241: delete
    del tree[482]
    del reference[482]
    assert tree.invariants(), "Invariants failed at step 241"

    # Operation 242: delete
    del tree[1076]
    del reference[1076]
    assert tree.invariants(), "Invariants failed at step 242"

    # Operation 243: update
    tree[7164] = 'value_64054'
    reference[7164] = 'value_64054'
    assert tree.invariants(), "Invariants failed at step 243"

    # Operation 244: insert
    tree[4486] = 'value_417001'
    reference[4486] = 'value_417001'
    assert tree.invariants(), "Invariants failed at step 244"

    # Operation 245: get
    assert tree.invariants(), "Invariants failed at step 245"

    # Operation 246: delete
    del tree[5546]
    del reference[5546]
    assert tree.invariants(), "Invariants failed at step 246"

    # Operation 247: insert
    tree[5471] = 'value_21770'
    reference[5471] = 'value_21770'
    assert tree.invariants(), "Invariants failed at step 247"

    # Operation 248: update
    tree[778] = 'value_463175'
    reference[778] = 'value_463175'
    assert tree.invariants(), "Invariants failed at step 248"

    # Operation 249: insert
    tree[8425] = 'value_658047'
    reference[8425] = 'value_658047'
    assert tree.invariants(), "Invariants failed at step 249"

    # Operation 250: insert
    tree[9683] = 'value_749928'
    reference[9683] = 'value_749928'
    assert tree.invariants(), "Invariants failed at step 250"

    # Operation 251: batch_delete
    keys_to_delete = [1025, 337, 6356, 3190, 88]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 251"

    # Operation 252: get
    assert tree.invariants(), "Invariants failed at step 252"

    # Operation 253: insert
    tree[7620] = 'value_394553'
    reference[7620] = 'value_394553'
    assert tree.invariants(), "Invariants failed at step 253"

    # Operation 254: delete
    del tree[4851]
    del reference[4851]
    assert tree.invariants(), "Invariants failed at step 254"

    # Operation 255: batch_delete
    keys_to_delete = [898, 1177, 4203, 9452, 9485, 1489, 7058, 697, 574]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 255"

    # Operation 256: get
    assert tree.invariants(), "Invariants failed at step 256"

    # Operation 257: get
    assert tree.invariants(), "Invariants failed at step 257"

    # Operation 258: update
    tree[3485] = 'value_589011'
    reference[3485] = 'value_589011'
    assert tree.invariants(), "Invariants failed at step 258"

    # Operation 259: insert
    tree[4510] = 'value_710845'
    reference[4510] = 'value_710845'
    assert tree.invariants(), "Invariants failed at step 259"

    # Operation 260: get
    assert tree.invariants(), "Invariants failed at step 260"

    # Operation 261: delete
    del tree[850]
    del reference[850]
    assert tree.invariants(), "Invariants failed at step 261"

    # Operation 262: delete
    del tree[613]
    del reference[613]
    assert tree.invariants(), "Invariants failed at step 262"

    # Operation 263: get
    assert tree.invariants(), "Invariants failed at step 263"

    # Operation 264: get
    assert tree.invariants(), "Invariants failed at step 264"

    # Operation 265: delete
    del tree[125]
    del reference[125]
    assert tree.invariants(), "Invariants failed at step 265"

    # Operation 266: get
    assert tree.invariants(), "Invariants failed at step 266"

    # Operation 267: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 267"

    # Operation 268: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 268"

    # Operation 269: update
    tree[394] = 'value_471515'
    reference[394] = 'value_471515'
    assert tree.invariants(), "Invariants failed at step 269"

    # Operation 270: get
    assert tree.invariants(), "Invariants failed at step 270"

    # Operation 271: insert
    tree[8674] = 'value_788706'
    reference[8674] = 'value_788706'
    assert tree.invariants(), "Invariants failed at step 271"

    # Operation 272: update
    tree[9252] = 'value_550592'
    reference[9252] = 'value_550592'
    assert tree.invariants(), "Invariants failed at step 272"

    # Operation 273: batch_delete
    keys_to_delete = [7044, 9806, 4118, 1499, 188]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 273"

    # Operation 274: get
    assert tree.invariants(), "Invariants failed at step 274"

    # Operation 275: insert
    tree[612] = 'value_328097'
    reference[612] = 'value_328097'
    assert tree.invariants(), "Invariants failed at step 275"

    # Operation 276: batch_delete
    keys_to_delete = [1378, 3554, 9956, 1381, 388, 8259, 1673, 397, 6671, 4274, 1270, 319]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 276"

    # Operation 277: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 277"

    # Operation 278: get
    assert tree.invariants(), "Invariants failed at step 278"

    # Operation 279: update
    tree[9000] = 'value_244823'
    reference[9000] = 'value_244823'
    assert tree.invariants(), "Invariants failed at step 279"

    # Operation 280: delete
    del tree[941]
    del reference[941]
    assert tree.invariants(), "Invariants failed at step 280"

    # Operation 281: delete
    del tree[965]
    del reference[965]
    assert tree.invariants(), "Invariants failed at step 281"

    # Operation 282: update
    tree[1210] = 'value_515632'
    reference[1210] = 'value_515632'
    assert tree.invariants(), "Invariants failed at step 282"

    # Operation 283: get
    assert tree.invariants(), "Invariants failed at step 283"

    # Operation 284: insert
    tree[9948] = 'value_409992'
    reference[9948] = 'value_409992'
    assert tree.invariants(), "Invariants failed at step 284"

    # Operation 285: batch_delete
    keys_to_delete = [2112, 4672, 9349, 5352, 4567]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 285"

    # Operation 286: delete
    del tree[5732]
    del reference[5732]
    assert tree.invariants(), "Invariants failed at step 286"

    # Operation 287: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 287"

    # Operation 288: get
    assert tree.invariants(), "Invariants failed at step 288"

    # Operation 289: insert
    tree[5576] = 'value_849898'
    reference[5576] = 'value_849898'
    assert tree.invariants(), "Invariants failed at step 289"

    # Operation 290: get
    assert tree.invariants(), "Invariants failed at step 290"

    # Operation 291: insert
    tree[1830] = 'value_653555'
    reference[1830] = 'value_653555'
    assert tree.invariants(), "Invariants failed at step 291"

    # Operation 292: update
    tree[1830] = 'value_350449'
    reference[1830] = 'value_350449'
    assert tree.invariants(), "Invariants failed at step 292"

    # Operation 293: insert
    tree[4714] = 'value_606643'
    reference[4714] = 'value_606643'
    assert tree.invariants(), "Invariants failed at step 293"

    # Operation 294: update
    tree[4849] = 'value_808080'
    reference[4849] = 'value_808080'
    assert tree.invariants(), "Invariants failed at step 294"

    # Operation 295: get
    assert tree.invariants(), "Invariants failed at step 295"

    # Operation 296: get
    assert tree.invariants(), "Invariants failed at step 296"

    # Operation 297: delete
    del tree[10]
    del reference[10]
    assert tree.invariants(), "Invariants failed at step 297"

    # Operation 298: update
    tree[634] = 'value_714664'
    reference[634] = 'value_714664'
    assert tree.invariants(), "Invariants failed at step 298"

    # Operation 299: insert
    tree[7817] = 'value_278375'
    reference[7817] = 'value_278375'
    assert tree.invariants(), "Invariants failed at step 299"

    # Operation 300: delete
    del tree[2300]
    del reference[2300]
    assert tree.invariants(), "Invariants failed at step 300"

    # Operation 301: insert
    tree[488] = 'value_676037'
    reference[488] = 'value_676037'
    assert tree.invariants(), "Invariants failed at step 301"

    # Operation 302: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 302"

    # Operation 303: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 303"

    # Operation 304: insert
    tree[3184] = 'value_368380'
    reference[3184] = 'value_368380'
    assert tree.invariants(), "Invariants failed at step 304"

    # Operation 305: get
    assert tree.invariants(), "Invariants failed at step 305"

    # Operation 306: delete
    del tree[227]
    del reference[227]
    assert tree.invariants(), "Invariants failed at step 306"

    # Operation 307: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 307"

    # Operation 308: insert
    tree[8039] = 'value_259337'
    reference[8039] = 'value_259337'
    assert tree.invariants(), "Invariants failed at step 308"

    # Operation 309: update
    tree[4198] = 'value_759043'
    reference[4198] = 'value_759043'
    assert tree.invariants(), "Invariants failed at step 309"

    # Operation 310: delete
    del tree[6869]
    del reference[6869]
    assert tree.invariants(), "Invariants failed at step 310"

    # Operation 311: delete
    del tree[7965]
    del reference[7965]
    assert tree.invariants(), "Invariants failed at step 311"

    # Operation 312: update
    tree[163] = 'value_354628'
    reference[163] = 'value_354628'
    assert tree.invariants(), "Invariants failed at step 312"

    # Operation 313: batch_delete
    keys_to_delete = [7104, 6498, 9990, 1290, 299, 715, 1590, 5790, 8223]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 313"

    # Operation 314: update
    tree[6723] = 'value_2700'
    reference[6723] = 'value_2700'
    assert tree.invariants(), "Invariants failed at step 314"

    # Operation 315: delete
    del tree[1189]
    del reference[1189]
    assert tree.invariants(), "Invariants failed at step 315"

    # Operation 316: delete
    del tree[127]
    del reference[127]
    assert tree.invariants(), "Invariants failed at step 316"

    # Operation 317: update
    tree[2860] = 'value_919234'
    reference[2860] = 'value_919234'
    assert tree.invariants(), "Invariants failed at step 317"

    # Operation 318: insert
    tree[6834] = 'value_53015'
    reference[6834] = 'value_53015'
    assert tree.invariants(), "Invariants failed at step 318"

    # Operation 319: get
    assert tree.invariants(), "Invariants failed at step 319"

    # Operation 320: get
    assert tree.invariants(), "Invariants failed at step 320"

    # Operation 321: delete
    del tree[1339]
    del reference[1339]
    assert tree.invariants(), "Invariants failed at step 321"

    # Operation 322: delete
    del tree[5855]
    del reference[5855]
    assert tree.invariants(), "Invariants failed at step 322"

    # Operation 323: insert
    tree[789] = 'value_647860'
    reference[789] = 'value_647860'
    assert tree.invariants(), "Invariants failed at step 323"

    # Operation 324: delete
    del tree[2393]
    del reference[2393]
    assert tree.invariants(), "Invariants failed at step 324"

    # Operation 325: batch_delete
    keys_to_delete = [224, 4899, 7878, 1319, 5576, 2344, 1195, 334, 5240, 1150, 542]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 325"

    # Operation 326: insert
    tree[3971] = 'value_973466'
    reference[3971] = 'value_973466'
    assert tree.invariants(), "Invariants failed at step 326"

    # Operation 327: delete
    del tree[202]
    del reference[202]
    assert tree.invariants(), "Invariants failed at step 327"

    # Operation 328: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 328"

    # Operation 329: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 329"

    # Operation 330: update
    tree[454] = 'value_180919'
    reference[454] = 'value_180919'
    assert tree.invariants(), "Invariants failed at step 330"

    # Operation 331: insert
    tree[7772] = 'value_891130'
    reference[7772] = 'value_891130'
    assert tree.invariants(), "Invariants failed at step 331"

    # Operation 332: insert
    tree[6103] = 'value_165204'
    reference[6103] = 'value_165204'
    assert tree.invariants(), "Invariants failed at step 332"

    # Operation 333: insert
    tree[5560] = 'value_980385'
    reference[5560] = 'value_980385'
    assert tree.invariants(), "Invariants failed at step 333"

    # Operation 334: delete
    del tree[892]
    del reference[892]
    assert tree.invariants(), "Invariants failed at step 334"

    # Operation 335: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 335"

    # Operation 336: insert
    tree[6829] = 'value_448357'
    reference[6829] = 'value_448357'
    assert tree.invariants(), "Invariants failed at step 336"

    # Operation 337: update
    tree[1223] = 'value_531912'
    reference[1223] = 'value_531912'
    assert tree.invariants(), "Invariants failed at step 337"

    # Operation 338: get
    assert tree.invariants(), "Invariants failed at step 338"

    # Operation 339: batch_delete
    keys_to_delete = [407, 1394, 8093, 3823]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 339"

    # Operation 340: insert
    tree[6625] = 'value_490208'
    reference[6625] = 'value_490208'
    assert tree.invariants(), "Invariants failed at step 340"

    # Operation 341: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 341"

    # Operation 342: delete
    del tree[1723]
    del reference[1723]
    assert tree.invariants(), "Invariants failed at step 342"

    # Operation 343: get
    assert tree.invariants(), "Invariants failed at step 343"

    # Operation 344: delete
    del tree[1262]
    del reference[1262]
    assert tree.invariants(), "Invariants failed at step 344"

    # Operation 345: insert
    tree[2994] = 'value_859751'
    reference[2994] = 'value_859751'
    assert tree.invariants(), "Invariants failed at step 345"

    # Operation 346: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 346"

    # Operation 347: insert
    tree[6826] = 'value_222976'
    reference[6826] = 'value_222976'
    assert tree.invariants(), "Invariants failed at step 347"

    # Operation 348: delete
    del tree[2331]
    del reference[2331]
    assert tree.invariants(), "Invariants failed at step 348"

    # Operation 349: insert
    tree[2253] = 'value_267017'
    reference[2253] = 'value_267017'
    assert tree.invariants(), "Invariants failed at step 349"

    # Operation 350: update
    tree[2596] = 'value_335176'
    reference[2596] = 'value_335176'
    assert tree.invariants(), "Invariants failed at step 350"

    # Operation 351: insert
    tree[6954] = 'value_197146'
    reference[6954] = 'value_197146'
    assert tree.invariants(), "Invariants failed at step 351"

    # Operation 352: delete
    del tree[8425]
    del reference[8425]
    assert tree.invariants(), "Invariants failed at step 352"

    # Operation 353: delete
    del tree[478]
    del reference[478]
    assert tree.invariants(), "Invariants failed at step 353"

    # Operation 354: delete
    del tree[8497]
    del reference[8497]
    assert tree.invariants(), "Invariants failed at step 354"

    # Operation 355: delete
    del tree[293]
    del reference[293]
    assert tree.invariants(), "Invariants failed at step 355"

    # Operation 356: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 356"

    # Operation 357: delete
    del tree[9504]
    del reference[9504]
    assert tree.invariants(), "Invariants failed at step 357"

    # Operation 358: batch_delete
    keys_to_delete = [832, 2405, 5000, 7147, 1419, 8211, 6773, 3707, 6077, 926]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 358"

    # Operation 359: insert
    tree[8044] = 'value_809997'
    reference[8044] = 'value_809997'
    assert tree.invariants(), "Invariants failed at step 359"

    # Operation 360: delete
    del tree[1438]
    del reference[1438]
    assert tree.invariants(), "Invariants failed at step 360"

    # Operation 361: batch_delete
    keys_to_delete = [97, 358, 5544, 1901, 6575, 2159, 4979, 3382]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 361"

    # Operation 362: insert
    tree[9005] = 'value_169557'
    reference[9005] = 'value_169557'
    assert tree.invariants(), "Invariants failed at step 362"

    # Operation 363: get
    assert tree.invariants(), "Invariants failed at step 363"

    # Operation 364: insert
    tree[1044] = 'value_354207'
    reference[1044] = 'value_354207'
    assert tree.invariants(), "Invariants failed at step 364"

    # Operation 365: insert
    tree[2741] = 'value_400159'
    reference[2741] = 'value_400159'
    assert tree.invariants(), "Invariants failed at step 365"

    # Operation 366: insert
    tree[9601] = 'value_607561'
    reference[9601] = 'value_607561'
    assert tree.invariants(), "Invariants failed at step 366"

    # Operation 367: batch_delete
    keys_to_delete = [8674, 1192, 9356, 943, 3184, 9043, 2265, 3514, 1372]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 367"

    # Operation 368: insert
    tree[4607] = 'value_562453'
    reference[4607] = 'value_562453'
    assert tree.invariants(), "Invariants failed at step 368"

    # Operation 369: insert
    tree[9991] = 'value_308200'
    reference[9991] = 'value_308200'
    assert tree.invariants(), "Invariants failed at step 369"

    # Operation 370: delete
    del tree[1207]
    del reference[1207]
    assert tree.invariants(), "Invariants failed at step 370"

    # Operation 371: update
    tree[6561] = 'value_653512'
    reference[6561] = 'value_653512'
    assert tree.invariants(), "Invariants failed at step 371"

    # Operation 372: batch_delete
    keys_to_delete = [2848, 1569, 1869, 9207, 6714, 8668, 1022]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 372"

    # Operation 373: insert
    tree[7642] = 'value_724717'
    reference[7642] = 'value_724717'
    assert tree.invariants(), "Invariants failed at step 373"

    # Operation 374: insert
    tree[738] = 'value_866910'
    reference[738] = 'value_866910'
    assert tree.invariants(), "Invariants failed at step 374"

    # Operation 375: delete
    del tree[5646]
    del reference[5646]
    assert tree.invariants(), "Invariants failed at step 375"

    # Operation 376: delete
    del tree[1668]
    del reference[1668]
    assert tree.invariants(), "Invariants failed at step 376"

    # Operation 377: update
    tree[9559] = 'value_394904'
    reference[9559] = 'value_394904'
    assert tree.invariants(), "Invariants failed at step 377"

    # Operation 378: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 378"

    # Operation 379: delete
    del tree[7682]
    del reference[7682]
    assert tree.invariants(), "Invariants failed at step 379"

    # Operation 380: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 380"

    # Operation 381: delete
    del tree[814]
    del reference[814]
    assert tree.invariants(), "Invariants failed at step 381"

    # Operation 382: insert
    tree[8204] = 'value_437031'
    reference[8204] = 'value_437031'
    assert tree.invariants(), "Invariants failed at step 382"

    # Operation 383: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 383"

    # Operation 384: delete
    del tree[4812]
    del reference[4812]
    assert tree.invariants(), "Invariants failed at step 384"

    # Operation 385: batch_delete
    keys_to_delete = [841, 197, 7649, 1622]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 385"

    # Operation 386: delete
    del tree[3370]
    del reference[3370]
    assert tree.invariants(), "Invariants failed at step 386"

    # Operation 387: insert
    tree[8739] = 'value_964358'
    reference[8739] = 'value_964358'
    assert tree.invariants(), "Invariants failed at step 387"

    # Operation 388: delete
    del tree[622]
    del reference[622]
    assert tree.invariants(), "Invariants failed at step 388"

    # Operation 389: delete
    del tree[590]
    del reference[590]
    assert tree.invariants(), "Invariants failed at step 389"

    # Operation 390: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 390"

    # Operation 391: get
    assert tree.invariants(), "Invariants failed at step 391"

    # Operation 392: batch_delete
    keys_to_delete = [5912, 404, 6364, 656]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 392"

    # Operation 393: delete
    del tree[1265]
    del reference[1265]
    assert tree.invariants(), "Invariants failed at step 393"

    # Operation 394: insert
    tree[9133] = 'value_86843'
    reference[9133] = 'value_86843'
    assert tree.invariants(), "Invariants failed at step 394"

    # Operation 395: batch_delete
    keys_to_delete = [1121, 5827, 7018, 2448, 9620, 1015, 4409, 6458, 7293]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 395"

    # Operation 396: insert
    tree[6872] = 'value_390133'
    reference[6872] = 'value_390133'
    assert tree.invariants(), "Invariants failed at step 396"

    # Operation 397: get
    assert tree.invariants(), "Invariants failed at step 397"

    # Operation 398: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 398"

    # Operation 399: insert
    tree[2532] = 'value_445770'
    reference[2532] = 'value_445770'
    assert tree.invariants(), "Invariants failed at step 399"

    # Operation 400: get
    assert tree.invariants(), "Invariants failed at step 400"

    # Operation 401: delete
    del tree[377]
    del reference[377]
    assert tree.invariants(), "Invariants failed at step 401"

    # Operation 402: update
    tree[3690] = 'value_532237'
    reference[3690] = 'value_532237'
    assert tree.invariants(), "Invariants failed at step 402"

    # Operation 403: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 403"

    # Operation 404: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 404"

    # Operation 405: delete
    del tree[1289]
    del reference[1289]
    assert tree.invariants(), "Invariants failed at step 405"

    # Operation 406: get
    assert tree.invariants(), "Invariants failed at step 406"

    # Operation 407: delete
    del tree[677]
    del reference[677]
    assert tree.invariants(), "Invariants failed at step 407"

    # Operation 408: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 408"

    # Operation 409: update
    tree[932] = 'value_355614'
    reference[932] = 'value_355614'
    assert tree.invariants(), "Invariants failed at step 409"

    # Operation 410: get
    assert tree.invariants(), "Invariants failed at step 410"

    # Operation 411: delete
    del tree[8263]
    del reference[8263]
    assert tree.invariants(), "Invariants failed at step 411"

    # Operation 412: batch_delete
    keys_to_delete = [6881, 4066, 4036, 6054, 616, 778, 172, 1135, 8980, 3029, 7418]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 412"

    # Operation 413: batch_delete
    keys_to_delete = [385, 8676, 2629, 7622, 266, 491, 1010]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 413"

    # Operation 414: insert
    tree[6745] = 'value_532812'
    reference[6745] = 'value_532812'
    assert tree.invariants(), "Invariants failed at step 414"

    # Operation 415: update
    tree[7632] = 'value_41260'
    reference[7632] = 'value_41260'
    assert tree.invariants(), "Invariants failed at step 415"

    # Operation 416: insert
    tree[574] = 'value_827262'
    reference[574] = 'value_827262'
    assert tree.invariants(), "Invariants failed at step 416"

    # Operation 417: insert
    tree[5518] = 'value_726728'
    reference[5518] = 'value_726728'
    assert tree.invariants(), "Invariants failed at step 417"

    # Operation 418: update
    tree[7772] = 'value_25957'
    reference[7772] = 'value_25957'
    assert tree.invariants(), "Invariants failed at step 418"

    # Operation 419: get
    assert tree.invariants(), "Invariants failed at step 419"

    # Operation 420: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 420"

    # Operation 421: insert
    tree[3991] = 'value_66351'
    reference[3991] = 'value_66351'
    assert tree.invariants(), "Invariants failed at step 421"

    # Operation 422: insert
    tree[5495] = 'value_643254'
    reference[5495] = 'value_643254'
    assert tree.invariants(), "Invariants failed at step 422"

    # Operation 423: update
    tree[5348] = 'value_272861'
    reference[5348] = 'value_272861'
    assert tree.invariants(), "Invariants failed at step 423"

    # Operation 424: batch_delete
    keys_to_delete = [2113, 513, 2372, 4614, 3724, 1403, 3288, 1115, 1343]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 424"

    # Operation 425: insert
    tree[4644] = 'value_475251'
    reference[4644] = 'value_475251'
    assert tree.invariants(), "Invariants failed at step 425"

    # Operation 426: delete
    del tree[1276]
    del reference[1276]
    assert tree.invariants(), "Invariants failed at step 426"

    # Operation 427: delete
    del tree[6353]
    del reference[6353]
    assert tree.invariants(), "Invariants failed at step 427"

    # Operation 428: insert
    tree[5834] = 'value_287146'
    reference[5834] = 'value_287146'
    assert tree.invariants(), "Invariants failed at step 428"

    # Operation 429: delete
    del tree[2418]
    del reference[2418]
    assert tree.invariants(), "Invariants failed at step 429"

    # Operation 430: insert
    tree[5087] = 'value_480872'
    reference[5087] = 'value_480872'
    assert tree.invariants(), "Invariants failed at step 430"

    # Operation 431: update
    tree[793] = 'value_839850'
    reference[793] = 'value_839850'
    assert tree.invariants(), "Invariants failed at step 431"

    # Operation 432: delete
    del tree[7042]
    del reference[7042]
    assert tree.invariants(), "Invariants failed at step 432"

    # Operation 433: update
    tree[564] = 'value_626312'
    reference[564] = 'value_626312'
    assert tree.invariants(), "Invariants failed at step 433"

    # Operation 434: insert
    tree[1107] = 'value_317911'
    reference[1107] = 'value_317911'
    assert tree.invariants(), "Invariants failed at step 434"

    # Operation 435: get
    assert tree.invariants(), "Invariants failed at step 435"

    # Operation 436: update
    tree[738] = 'value_612999'
    reference[738] = 'value_612999'
    assert tree.invariants(), "Invariants failed at step 436"

    # Operation 437: delete
    del tree[5380]
    del reference[5380]
    assert tree.invariants(), "Invariants failed at step 437"

    # Operation 438: insert
    tree[826] = 'value_602812'
    reference[826] = 'value_602812'
    assert tree.invariants(), "Invariants failed at step 438"

    # Operation 439: delete
    del tree[9350]
    del reference[9350]
    assert tree.invariants(), "Invariants failed at step 439"

    # Operation 440: update
    tree[2334] = 'value_71663'
    reference[2334] = 'value_71663'
    assert tree.invariants(), "Invariants failed at step 440"

    # Operation 441: update
    tree[2810] = 'value_704056'
    reference[2810] = 'value_704056'
    assert tree.invariants(), "Invariants failed at step 441"

    # Operation 442: delete
    del tree[445]
    del reference[445]
    assert tree.invariants(), "Invariants failed at step 442"

    # Operation 443: get
    assert tree.invariants(), "Invariants failed at step 443"

    # Operation 444: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 444"

    # Operation 445: get
    assert tree.invariants(), "Invariants failed at step 445"

    # Operation 446: update
    tree[901] = 'value_176711'
    reference[901] = 'value_176711'
    assert tree.invariants(), "Invariants failed at step 446"

    # Operation 447: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 447"

    # Operation 448: insert
    tree[9393] = 'value_519536'
    reference[9393] = 'value_519536'
    assert tree.invariants(), "Invariants failed at step 448"

    # Operation 449: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 449"

    # Operation 450: get
    assert tree.invariants(), "Invariants failed at step 450"

    # Operation 451: insert
    tree[2897] = 'value_622028'
    reference[2897] = 'value_622028'
    assert tree.invariants(), "Invariants failed at step 451"

    # Operation 452: get
    assert tree.invariants(), "Invariants failed at step 452"

    # Operation 453: get
    assert tree.invariants(), "Invariants failed at step 453"

    # Operation 454: get
    assert tree.invariants(), "Invariants failed at step 454"

    # Operation 455: insert
    tree[842] = 'value_799778'
    reference[842] = 'value_799778'
    assert tree.invariants(), "Invariants failed at step 455"

    # Operation 456: delete
    del tree[394]
    del reference[394]
    assert tree.invariants(), "Invariants failed at step 456"

    # Operation 457: insert
    tree[4983] = 'value_795830'
    reference[4983] = 'value_795830'
    assert tree.invariants(), "Invariants failed at step 457"

    # Operation 458: delete
    del tree[775]
    del reference[775]
    assert tree.invariants(), "Invariants failed at step 458"

    # Operation 459: get
    assert tree.invariants(), "Invariants failed at step 459"

    # Operation 460: delete
    del tree[6864]
    del reference[6864]
    assert tree.invariants(), "Invariants failed at step 460"

    # Operation 461: get
    assert tree.invariants(), "Invariants failed at step 461"

    # Operation 462: insert
    tree[4189] = 'value_264954'
    reference[4189] = 'value_264954'
    assert tree.invariants(), "Invariants failed at step 462"

    # Operation 463: get
    assert tree.invariants(), "Invariants failed at step 463"

    # Operation 464: get
    assert tree.invariants(), "Invariants failed at step 464"

    # Operation 465: get
    assert tree.invariants(), "Invariants failed at step 465"

    # Operation 466: insert
    tree[936] = 'value_7235'
    reference[936] = 'value_7235'
    assert tree.invariants(), "Invariants failed at step 466"

    # Operation 467: insert
    tree[7313] = 'value_749550'
    reference[7313] = 'value_749550'
    assert tree.invariants(), "Invariants failed at step 467"

    # Operation 468: get
    assert tree.invariants(), "Invariants failed at step 468"

    # Operation 469: update
    tree[4510] = 'value_642862'
    reference[4510] = 'value_642862'
    assert tree.invariants(), "Invariants failed at step 469"

    # Operation 470: delete
    del tree[1044]
    del reference[1044]
    assert tree.invariants(), "Invariants failed at step 470"

    # Operation 471: insert
    tree[9151] = 'value_95268'
    reference[9151] = 'value_95268'
    assert tree.invariants(), "Invariants failed at step 471"

    # Operation 472: update
    tree[1899] = 'value_927886'
    reference[1899] = 'value_927886'
    assert tree.invariants(), "Invariants failed at step 472"

    # Operation 473: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 473"

    # Operation 474: delete
    del tree[4270]
    del reference[4270]
    assert tree.invariants(), "Invariants failed at step 474"

    # Operation 475: update
    tree[517] = 'value_341298'
    reference[517] = 'value_341298'
    assert tree.invariants(), "Invariants failed at step 475"

    # Operation 476: update
    tree[593] = 'value_758014'
    reference[593] = 'value_758014'
    assert tree.invariants(), "Invariants failed at step 476"

    # Operation 477: insert
    tree[9231] = 'value_544098'
    reference[9231] = 'value_544098'
    assert tree.invariants(), "Invariants failed at step 477"

    # Operation 478: insert
    tree[1630] = 'value_873644'
    reference[1630] = 'value_873644'
    assert tree.invariants(), "Invariants failed at step 478"

    # Operation 479: insert
    tree[4523] = 'value_743495'
    reference[4523] = 'value_743495'
    assert tree.invariants(), "Invariants failed at step 479"

    # Operation 480: delete
    del tree[6954]
    del reference[6954]
    assert tree.invariants(), "Invariants failed at step 480"

    # Operation 481: delete
    del tree[9376]
    del reference[9376]
    assert tree.invariants(), "Invariants failed at step 481"

    # Operation 482: batch_delete
    keys_to_delete = [8326, 8779, 1100, 14, 1520, 1247]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 482"

    # Operation 483: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 483"

    # Operation 484: delete
    del tree[9328]
    del reference[9328]
    assert tree.invariants(), "Invariants failed at step 484"

    # Operation 485: delete
    del tree[6103]
    del reference[6103]
    assert tree.invariants(), "Invariants failed at step 485"

    # Operation 486: insert
    tree[9076] = 'value_740514'
    reference[9076] = 'value_740514'
    assert tree.invariants(), "Invariants failed at step 486"

    # Operation 487: insert
    tree[8974] = 'value_985654'
    reference[8974] = 'value_985654'
    assert tree.invariants(), "Invariants failed at step 487"

    # Operation 488: update
    tree[9393] = 'value_42039'
    reference[9393] = 'value_42039'
    assert tree.invariants(), "Invariants failed at step 488"

    # Operation 489: insert
    tree[3976] = 'value_190182'
    reference[3976] = 'value_190182'
    assert tree.invariants(), "Invariants failed at step 489"

    # Operation 490: insert
    tree[4837] = 'value_138638'
    reference[4837] = 'value_138638'
    assert tree.invariants(), "Invariants failed at step 490"

    # Operation 491: insert
    tree[4050] = 'value_705796'
    reference[4050] = 'value_705796'
    assert tree.invariants(), "Invariants failed at step 491"

    # Operation 492: batch_delete
    keys_to_delete = [131, 9316, 581, 5639, 9521, 596, 6869, 8698]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 492"

    # Operation 493: insert
    tree[5526] = 'value_185141'
    reference[5526] = 'value_185141'
    assert tree.invariants(), "Invariants failed at step 493"

    # Operation 494: get
    assert tree.invariants(), "Invariants failed at step 494"

    # Operation 495: insert
    tree[8261] = 'value_790209'
    reference[8261] = 'value_790209'
    assert tree.invariants(), "Invariants failed at step 495"

    # Operation 496: update
    tree[5999] = 'value_893079'
    reference[5999] = 'value_893079'
    assert tree.invariants(), "Invariants failed at step 496"

    # Operation 497: delete
    del tree[3074]
    del reference[3074]
    assert tree.invariants(), "Invariants failed at step 497"

    # Operation 498: delete
    del tree[611]
    del reference[611]
    assert tree.invariants(), "Invariants failed at step 498"

    # Operation 499: delete
    del tree[593]
    del reference[593]
    assert tree.invariants(), "Invariants failed at step 499"

    # Operation 500: update
    tree[5206] = 'value_470343'
    reference[5206] = 'value_470343'
    assert tree.invariants(), "Invariants failed at step 500"

    # Operation 501: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 501"

    # Operation 502: insert
    tree[7448] = 'value_679269'
    reference[7448] = 'value_679269'
    assert tree.invariants(), "Invariants failed at step 502"

    # Operation 503: batch_delete
    keys_to_delete = [356, 4644, 1159, 1096, 1231, 308, 216, 5177, 701, 1855]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 503"

    # Operation 504: delete
    del tree[49]
    del reference[49]
    assert tree.invariants(), "Invariants failed at step 504"

    # Operation 505: delete
    del tree[2994]
    del reference[2994]
    assert tree.invariants(), "Invariants failed at step 505"

    # Operation 506: insert
    tree[787] = 'value_88851'
    reference[787] = 'value_88851'
    assert tree.invariants(), "Invariants failed at step 506"

    # Operation 507: insert
    tree[2205] = 'value_654447'
    reference[2205] = 'value_654447'
    assert tree.invariants(), "Invariants failed at step 507"

    # Operation 508: get
    assert tree.invariants(), "Invariants failed at step 508"

    # Operation 509: update
    tree[3031] = 'value_497205'
    reference[3031] = 'value_497205'
    assert tree.invariants(), "Invariants failed at step 509"

    # Operation 510: update
    tree[5273] = 'value_762027'
    reference[5273] = 'value_762027'
    assert tree.invariants(), "Invariants failed at step 510"

    # Operation 511: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 511"

    # Operation 512: get
    assert tree.invariants(), "Invariants failed at step 512"

    # Operation 513: update
    tree[2215] = 'value_190124'
    reference[2215] = 'value_190124'
    assert tree.invariants(), "Invariants failed at step 513"

    # Operation 514: delete
    del tree[1334]
    del reference[1334]
    assert tree.invariants(), "Invariants failed at step 514"

    # Operation 515: insert
    tree[2925] = 'value_178044'
    reference[2925] = 'value_178044'
    assert tree.invariants(), "Invariants failed at step 515"

    # Operation 516: delete
    del tree[8156]
    del reference[8156]
    assert tree.invariants(), "Invariants failed at step 516"

    # Operation 517: update
    tree[6394] = 'value_961178'
    reference[6394] = 'value_961178'
    assert tree.invariants(), "Invariants failed at step 517"

    # Operation 518: insert
    tree[8747] = 'value_22344'
    reference[8747] = 'value_22344'
    assert tree.invariants(), "Invariants failed at step 518"

    # Operation 519: insert
    tree[9324] = 'value_573864'
    reference[9324] = 'value_573864'
    assert tree.invariants(), "Invariants failed at step 519"

    # Operation 520: insert
    tree[4278] = 'value_388247'
    reference[4278] = 'value_388247'
    assert tree.invariants(), "Invariants failed at step 520"

    # Operation 521: get
    assert tree.invariants(), "Invariants failed at step 521"

    # Operation 522: insert
    tree[2402] = 'value_875454'
    reference[2402] = 'value_875454'
    assert tree.invariants(), "Invariants failed at step 522"

    # Operation 523: get
    assert tree.invariants(), "Invariants failed at step 523"

    # Operation 524: get
    assert tree.invariants(), "Invariants failed at step 524"

    # Operation 525: insert
    tree[5758] = 'value_922435'
    reference[5758] = 'value_922435'
    assert tree.invariants(), "Invariants failed at step 525"

    # Operation 526: update
    tree[7420] = 'value_707122'
    reference[7420] = 'value_707122'
    assert tree.invariants(), "Invariants failed at step 526"

    # Operation 527: delete
    del tree[103]
    del reference[103]
    assert tree.invariants(), "Invariants failed at step 527"

    # Operation 528: delete
    del tree[7313]
    del reference[7313]
    assert tree.invariants(), "Invariants failed at step 528"

    # Operation 529: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 529"

    # Operation 530: insert
    tree[7701] = 'value_793358'
    reference[7701] = 'value_793358'
    assert tree.invariants(), "Invariants failed at step 530"

    # Operation 531: batch_delete
    keys_to_delete = [7208, 2601, 8015, 16, 368, 7164, 1118]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 531"

    # Operation 532: insert
    tree[6837] = 'value_919606'
    reference[6837] = 'value_919606'
    assert tree.invariants(), "Invariants failed at step 532"

    # Operation 533: delete
    del tree[113]
    del reference[113]
    assert tree.invariants(), "Invariants failed at step 533"

    # Operation 534: batch_delete
    keys_to_delete = [416, 7942, 1259, 3179, 8974, 665, 2003, 2553]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 534"

    # Operation 535: insert
    tree[9691] = 'value_297134'
    reference[9691] = 'value_297134'
    assert tree.invariants(), "Invariants failed at step 535"

    # Operation 536: update
    tree[6610] = 'value_620061'
    reference[6610] = 'value_620061'
    assert tree.invariants(), "Invariants failed at step 536"

    # Operation 537: batch_delete
    keys_to_delete = [352, 865, 641, 288, 100, 5868, 86, 4054, 7000, 1046]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 537"

    # Operation 538: update
    tree[9573] = 'value_386102'
    reference[9573] = 'value_386102'
    assert tree.invariants(), "Invariants failed at step 538"

    # Operation 539: update
    tree[1133] = 'value_818293'
    reference[1133] = 'value_818293'
    assert tree.invariants(), "Invariants failed at step 539"

    # Operation 540: insert
    tree[7303] = 'value_703898'
    reference[7303] = 'value_703898'
    assert tree.invariants(), "Invariants failed at step 540"

    # Operation 541: delete
    del tree[694]
    del reference[694]
    assert tree.invariants(), "Invariants failed at step 541"

    # Operation 542: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 542"

    # Operation 543: get
    assert tree.invariants(), "Invariants failed at step 543"

    # Operation 544: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 544"

    # Operation 545: get
    assert tree.invariants(), "Invariants failed at step 545"

    # Operation 546: delete
    del tree[2987]
    del reference[2987]
    assert tree.invariants(), "Invariants failed at step 546"

    # Operation 547: insert
    tree[1036] = 'value_931354'
    reference[1036] = 'value_931354'
    assert tree.invariants(), "Invariants failed at step 547"

    # Operation 548: delete
    del tree[574]
    del reference[574]
    assert tree.invariants(), "Invariants failed at step 548"

    # Operation 549: insert
    tree[4947] = 'value_63332'
    reference[4947] = 'value_63332'
    assert tree.invariants(), "Invariants failed at step 549"

    # Operation 550: get
    assert tree.invariants(), "Invariants failed at step 550"

    # Operation 551: get
    assert tree.invariants(), "Invariants failed at step 551"

    # Operation 552: update
    tree[1111] = 'value_116262'
    reference[1111] = 'value_116262'
    assert tree.invariants(), "Invariants failed at step 552"

    # Operation 553: batch_delete
    keys_to_delete = [6147, 525, 6829, 1337, 7323]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 553"

    # Operation 554: get
    assert tree.invariants(), "Invariants failed at step 554"

    # Operation 555: update
    tree[488] = 'value_543748'
    reference[488] = 'value_543748'
    assert tree.invariants(), "Invariants failed at step 555"

    # Operation 556: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 556"

    # Operation 557: get
    assert tree.invariants(), "Invariants failed at step 557"

    # Operation 558: update
    tree[238] = 'value_645309'
    reference[238] = 'value_645309'
    assert tree.invariants(), "Invariants failed at step 558"

    # Operation 559: get
    assert tree.invariants(), "Invariants failed at step 559"

    # Operation 560: insert
    tree[6012] = 'value_84732'
    reference[6012] = 'value_84732'
    assert tree.invariants(), "Invariants failed at step 560"

    # Operation 561: insert
    tree[2434] = 'value_571546'
    reference[2434] = 'value_571546'
    assert tree.invariants(), "Invariants failed at step 561"

    # Operation 562: batch_delete
    keys_to_delete = [6369, 6810, 2596, 245, 1463, 5658, 1399]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 562"

    # Operation 563: get
    assert tree.invariants(), "Invariants failed at step 563"

    # Operation 564: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 564"

    # Operation 565: delete
    del tree[689]
    del reference[689]
    assert tree.invariants(), "Invariants failed at step 565"

    # Operation 566: batch_delete
    keys_to_delete = [8578, 2855, 7084, 433, 9905, 1043, 7861, 8118, 7448, 59]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 566"

    # Operation 567: delete
    del tree[8437]
    del reference[8437]
    assert tree.invariants(), "Invariants failed at step 567"

    # Operation 568: get
    assert tree.invariants(), "Invariants failed at step 568"

    # Operation 569: insert
    tree[14] = 'value_2438'
    reference[14] = 'value_2438'
    assert tree.invariants(), "Invariants failed at step 569"

    # Operation 570: update
    tree[4987] = 'value_860112'
    reference[4987] = 'value_860112'
    assert tree.invariants(), "Invariants failed at step 570"

    # Operation 571: get
    assert tree.invariants(), "Invariants failed at step 571"

    # Operation 572: insert
    tree[6909] = 'value_508956'
    reference[6909] = 'value_508956'
    assert tree.invariants(), "Invariants failed at step 572"

    # Operation 573: get
    assert tree.invariants(), "Invariants failed at step 573"

    # Operation 574: batch_delete
    keys_to_delete = [101, 550, 8494, 2359, 1465, 3551]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 574"

    # Operation 575: insert
    tree[5765] = 'value_823027'
    reference[5765] = 'value_823027'
    assert tree.invariants(), "Invariants failed at step 575"

    # Operation 576: insert
    tree[6771] = 'value_237507'
    reference[6771] = 'value_237507'
    assert tree.invariants(), "Invariants failed at step 576"

    # Operation 577: delete
    del tree[935]
    del reference[935]
    assert tree.invariants(), "Invariants failed at step 577"

    # Operation 578: insert
    tree[8367] = 'value_850090'
    reference[8367] = 'value_850090'
    assert tree.invariants(), "Invariants failed at step 578"

    # Operation 579: get
    assert tree.invariants(), "Invariants failed at step 579"

    # Operation 580: insert
    tree[5083] = 'value_622530'
    reference[5083] = 'value_622530'
    assert tree.invariants(), "Invariants failed at step 580"

    # Operation 581: insert
    tree[6061] = 'value_897405'
    reference[6061] = 'value_897405'
    assert tree.invariants(), "Invariants failed at step 581"

    # Operation 582: get
    assert tree.invariants(), "Invariants failed at step 582"

    # Operation 583: get
    assert tree.invariants(), "Invariants failed at step 583"

    # Operation 584: get
    assert tree.invariants(), "Invariants failed at step 584"

    # Operation 585: insert
    tree[4072] = 'value_266043'
    reference[4072] = 'value_266043'
    assert tree.invariants(), "Invariants failed at step 585"

    # Operation 586: delete
    del tree[587]
    del reference[587]
    assert tree.invariants(), "Invariants failed at step 586"

    # Operation 587: delete
    del tree[1087]
    del reference[1087]
    assert tree.invariants(), "Invariants failed at step 587"

    # Operation 588: batch_delete
    keys_to_delete = [785, 365, 1469, 3501]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 588"

    # Operation 589: delete
    del tree[29]
    del reference[29]
    assert tree.invariants(), "Invariants failed at step 589"

    # Operation 590: insert
    tree[9330] = 'value_104408'
    reference[9330] = 'value_104408'
    assert tree.invariants(), "Invariants failed at step 590"

    # Operation 591: delete
    del tree[554]
    del reference[554]
    assert tree.invariants(), "Invariants failed at step 591"

    # Operation 592: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 592"

    # Operation 593: insert
    tree[6321] = 'value_583076'
    reference[6321] = 'value_583076'
    assert tree.invariants(), "Invariants failed at step 593"

    # Operation 594: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 594"

    # Operation 595: get
    assert tree.invariants(), "Invariants failed at step 595"

    # Operation 596: insert
    tree[9320] = 'value_265733'
    reference[9320] = 'value_265733'
    assert tree.invariants(), "Invariants failed at step 596"

    # Operation 597: insert
    tree[4342] = 'value_321558'
    reference[4342] = 'value_321558'
    assert tree.invariants(), "Invariants failed at step 597"

    # Operation 598: get
    assert tree.invariants(), "Invariants failed at step 598"

    # Operation 599: get
    assert tree.invariants(), "Invariants failed at step 599"

    # Operation 600: delete
    del tree[538]
    del reference[538]
    assert tree.invariants(), "Invariants failed at step 600"

    # Operation 601: update
    tree[2180] = 'value_942931'
    reference[2180] = 'value_942931'
    assert tree.invariants(), "Invariants failed at step 601"

    # Operation 602: delete
    del tree[302]
    del reference[302]
    assert tree.invariants(), "Invariants failed at step 602"

    # Operation 603: insert
    tree[4496] = 'value_605088'
    reference[4496] = 'value_605088'
    assert tree.invariants(), "Invariants failed at step 603"

    # Operation 604: get
    assert tree.invariants(), "Invariants failed at step 604"

    # Operation 605: delete
    del tree[4086]
    del reference[4086]
    assert tree.invariants(), "Invariants failed at step 605"

    # Operation 606: update
    tree[9334] = 'value_988086'
    reference[9334] = 'value_988086'
    assert tree.invariants(), "Invariants failed at step 606"

    # Operation 607: insert
    tree[1434] = 'value_979987'
    reference[1434] = 'value_979987'
    assert tree.invariants(), "Invariants failed at step 607"

    # Operation 608: delete
    del tree[706]
    del reference[706]
    assert tree.invariants(), "Invariants failed at step 608"

    # Operation 609: batch_delete
    keys_to_delete = [256, 1058, 871, 1995, 1003, 7309, 653, 9806, 272, 4523, 947, 5083]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 609"

    # Operation 610: update
    tree[4198] = 'value_126965'
    reference[4198] = 'value_126965'
    assert tree.invariants(), "Invariants failed at step 610"

    # Operation 611: update
    tree[517] = 'value_640566'
    reference[517] = 'value_640566'
    assert tree.invariants(), "Invariants failed at step 611"

    # Operation 612: update
    tree[2379] = 'value_309372'
    reference[2379] = 'value_309372'
    assert tree.invariants(), "Invariants failed at step 612"

    # Operation 613: insert
    tree[8046] = 'value_888616'
    reference[8046] = 'value_888616'
    assert tree.invariants(), "Invariants failed at step 613"

    # Operation 614: delete
    del tree[5087]
    del reference[5087]
    assert tree.invariants(), "Invariants failed at step 614"

    # Operation 615: get
    assert tree.invariants(), "Invariants failed at step 615"

    # Operation 616: batch_delete
    keys_to_delete = [6178, 8051, 6775, 5145, 666, 4863]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 616"

    # Operation 617: get
    assert tree.invariants(), "Invariants failed at step 617"

    # Operation 618: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 618"

    # Operation 619: batch_delete
    keys_to_delete = [6276, 1159, 6065, 914, 1267, 9205, 826, 571, 7772, 989]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 619"

    # Operation 620: batch_delete
    keys_to_delete = [2843, 2402, 1346, 8233, 7177, 877, 401, 4692, 9339]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 620"

    # Operation 621: batch_delete
    keys_to_delete = [1217, 4579, 9644, 5361, 2711]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 621"

    # Operation 622: update
    tree[855] = 'value_437183'
    reference[855] = 'value_437183'
    assert tree.invariants(), "Invariants failed at step 622"

    # Operation 623: batch_delete
    keys_to_delete = [35, 9220, 7817, 685, 7706]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 623"

    # Operation 624: insert
    tree[1572] = 'value_244193'
    reference[1572] = 'value_244193'
    assert tree.invariants(), "Invariants failed at step 624"

    # Operation 625: insert
    tree[2035] = 'value_175167'
    reference[2035] = 'value_175167'
    assert tree.invariants(), "Invariants failed at step 625"

    # Operation 626: batch_delete
    keys_to_delete = [1475, 4837, 8965, 2793, 1198, 1142, 4694, 9338]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 626"

    # Verify final consistency
    assert len(tree) == len(reference), "Length mismatch"
    for key, value in reference.items():
        assert tree[key] == value, f"Value mismatch for {key}"
    print("Reproduction completed successfully")

if __name__ == "__main__":
    reproduce_failure()
