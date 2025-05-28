"""
Fuzz test failure reproduction
Seed: 642890
Capacity: 4
Failed at operation: 450
"""

from bplus_tree import BPlusTreeMap
from collections import OrderedDict

def reproduce_failure():
    tree = BPlusTreeMap(capacity=4)
    reference = OrderedDict()

    # Operation 1: insert
    tree[2072] = 'value_688725'
    reference[2072] = 'value_688725'
    assert tree.invariants(), "Invariants failed at step 1"

    # Operation 2: insert
    tree[8490] = 'value_274729'
    reference[8490] = 'value_274729'
    assert tree.invariants(), "Invariants failed at step 2"

    # Operation 3: delete
    del tree[8490]
    del reference[8490]
    assert tree.invariants(), "Invariants failed at step 3"

    # Operation 4: get
    assert tree.invariants(), "Invariants failed at step 4"

    # Operation 5: delete
    del tree[2072]
    del reference[2072]
    assert tree.invariants(), "Invariants failed at step 5"

    # Operation 6: get
    assert tree.invariants(), "Invariants failed at step 6"

    # Operation 7: get
    assert tree.invariants(), "Invariants failed at step 7"

    # Operation 8: insert
    tree[8067] = 'value_543320'
    reference[8067] = 'value_543320'
    assert tree.invariants(), "Invariants failed at step 8"

    # Operation 9: insert
    tree[9187] = 'value_1128'
    reference[9187] = 'value_1128'
    assert tree.invariants(), "Invariants failed at step 9"

    # Operation 10: update
    tree[9187] = 'value_400391'
    reference[9187] = 'value_400391'
    assert tree.invariants(), "Invariants failed at step 10"

    # Operation 11: get
    assert tree.invariants(), "Invariants failed at step 11"

    # Operation 12: get
    assert tree.invariants(), "Invariants failed at step 12"

    # Operation 13: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 13"

    # Operation 14: get
    assert tree.invariants(), "Invariants failed at step 14"

    # Operation 15: update
    tree[9187] = 'value_724525'
    reference[9187] = 'value_724525'
    assert tree.invariants(), "Invariants failed at step 15"

    # Operation 16: get
    assert tree.invariants(), "Invariants failed at step 16"

    # Operation 17: delete
    del tree[9187]
    del reference[9187]
    assert tree.invariants(), "Invariants failed at step 17"

    # Operation 18: insert
    tree[6970] = 'value_864380'
    reference[6970] = 'value_864380'
    assert tree.invariants(), "Invariants failed at step 18"

    # Operation 19: insert
    tree[6878] = 'value_714268'
    reference[6878] = 'value_714268'
    assert tree.invariants(), "Invariants failed at step 19"

    # Operation 20: get
    assert tree.invariants(), "Invariants failed at step 20"

    # Operation 21: update
    tree[6970] = 'value_651546'
    reference[6970] = 'value_651546'
    assert tree.invariants(), "Invariants failed at step 21"

    # Operation 22: update
    tree[8067] = 'value_943892'
    reference[8067] = 'value_943892'
    assert tree.invariants(), "Invariants failed at step 22"

    # Operation 23: insert
    tree[7211] = 'value_696585'
    reference[7211] = 'value_696585'
    assert tree.invariants(), "Invariants failed at step 23"

    # Operation 24: insert
    tree[6498] = 'value_21264'
    reference[6498] = 'value_21264'
    assert tree.invariants(), "Invariants failed at step 24"

    # Operation 25: insert
    tree[7239] = 'value_794924'
    reference[7239] = 'value_794924'
    assert tree.invariants(), "Invariants failed at step 25"

    # Operation 26: delete
    del tree[6970]
    del reference[6970]
    assert tree.invariants(), "Invariants failed at step 26"

    # Operation 27: delete
    del tree[7239]
    del reference[7239]
    assert tree.invariants(), "Invariants failed at step 27"

    # Operation 28: delete
    del tree[8067]
    del reference[8067]
    assert tree.invariants(), "Invariants failed at step 28"

    # Operation 29: insert
    tree[807] = 'value_857396'
    reference[807] = 'value_857396'
    assert tree.invariants(), "Invariants failed at step 29"

    # Operation 30: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 30"

    # Operation 31: delete
    del tree[6878]
    del reference[6878]
    assert tree.invariants(), "Invariants failed at step 31"

    # Operation 32: delete
    del tree[807]
    del reference[807]
    assert tree.invariants(), "Invariants failed at step 32"

    # Operation 33: insert
    tree[5260] = 'value_358379'
    reference[5260] = 'value_358379'
    assert tree.invariants(), "Invariants failed at step 33"

    # Operation 34: delete
    del tree[5260]
    del reference[5260]
    assert tree.invariants(), "Invariants failed at step 34"

    # Operation 35: insert
    tree[5406] = 'value_293241'
    reference[5406] = 'value_293241'
    assert tree.invariants(), "Invariants failed at step 35"

    # Operation 36: insert
    tree[8348] = 'value_604293'
    reference[8348] = 'value_604293'
    assert tree.invariants(), "Invariants failed at step 36"

    # Operation 37: update
    tree[8348] = 'value_712406'
    reference[8348] = 'value_712406'
    assert tree.invariants(), "Invariants failed at step 37"

    # Operation 38: insert
    tree[8873] = 'value_189373'
    reference[8873] = 'value_189373'
    assert tree.invariants(), "Invariants failed at step 38"

    # Operation 39: insert
    tree[21] = 'value_631175'
    reference[21] = 'value_631175'
    assert tree.invariants(), "Invariants failed at step 39"

    # Operation 40: insert
    tree[5297] = 'value_636423'
    reference[5297] = 'value_636423'
    assert tree.invariants(), "Invariants failed at step 40"

    # Operation 41: delete
    del tree[7211]
    del reference[7211]
    assert tree.invariants(), "Invariants failed at step 41"

    # Operation 42: get
    assert tree.invariants(), "Invariants failed at step 42"

    # Operation 43: delete
    del tree[21]
    del reference[21]
    assert tree.invariants(), "Invariants failed at step 43"

    # Operation 44: insert
    tree[8001] = 'value_853676'
    reference[8001] = 'value_853676'
    assert tree.invariants(), "Invariants failed at step 44"

    # Operation 45: get
    assert tree.invariants(), "Invariants failed at step 45"

    # Operation 46: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 46"

    # Operation 47: get
    assert tree.invariants(), "Invariants failed at step 47"

    # Operation 48: insert
    tree[8292] = 'value_629112'
    reference[8292] = 'value_629112'
    assert tree.invariants(), "Invariants failed at step 48"

    # Operation 49: delete
    del tree[6498]
    del reference[6498]
    assert tree.invariants(), "Invariants failed at step 49"

    # Operation 50: insert
    tree[4638] = 'value_356707'
    reference[4638] = 'value_356707'
    assert tree.invariants(), "Invariants failed at step 50"

    # Operation 51: batch_delete
    keys_to_delete = [5297, 8873, 4638, 4695, 3185]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 51"

    # Operation 52: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 52"

    # Operation 53: delete
    del tree[8001]
    del reference[8001]
    assert tree.invariants(), "Invariants failed at step 53"

    # Operation 54: update
    tree[5406] = 'value_646339'
    reference[5406] = 'value_646339'
    assert tree.invariants(), "Invariants failed at step 54"

    # Operation 55: delete
    del tree[8348]
    del reference[8348]
    assert tree.invariants(), "Invariants failed at step 55"

    # Operation 56: delete
    del tree[5406]
    del reference[5406]
    assert tree.invariants(), "Invariants failed at step 56"

    # Operation 57: get
    assert tree.invariants(), "Invariants failed at step 57"

    # Operation 58: delete
    del tree[8292]
    del reference[8292]
    assert tree.invariants(), "Invariants failed at step 58"

    # Operation 59: get
    assert tree.invariants(), "Invariants failed at step 59"

    # Operation 60: insert
    tree[8561] = 'value_158262'
    reference[8561] = 'value_158262'
    assert tree.invariants(), "Invariants failed at step 60"

    # Operation 61: update
    tree[8561] = 'value_630353'
    reference[8561] = 'value_630353'
    assert tree.invariants(), "Invariants failed at step 61"

    # Operation 62: delete
    del tree[8561]
    del reference[8561]
    assert tree.invariants(), "Invariants failed at step 62"

    # Operation 63: insert
    tree[2042] = 'value_741977'
    reference[2042] = 'value_741977'
    assert tree.invariants(), "Invariants failed at step 63"

    # Operation 64: update
    tree[2042] = 'value_388663'
    reference[2042] = 'value_388663'
    assert tree.invariants(), "Invariants failed at step 64"

    # Operation 65: insert
    tree[4276] = 'value_953369'
    reference[4276] = 'value_953369'
    assert tree.invariants(), "Invariants failed at step 65"

    # Operation 66: delete
    del tree[4276]
    del reference[4276]
    assert tree.invariants(), "Invariants failed at step 66"

    # Operation 67: update
    tree[2042] = 'value_384100'
    reference[2042] = 'value_384100'
    assert tree.invariants(), "Invariants failed at step 67"

    # Operation 68: insert
    tree[9499] = 'value_909512'
    reference[9499] = 'value_909512'
    assert tree.invariants(), "Invariants failed at step 68"

    # Operation 69: delete
    del tree[2042]
    del reference[2042]
    assert tree.invariants(), "Invariants failed at step 69"

    # Operation 70: delete
    del tree[9499]
    del reference[9499]
    assert tree.invariants(), "Invariants failed at step 70"

    # Operation 71: insert
    tree[2071] = 'value_632601'
    reference[2071] = 'value_632601'
    assert tree.invariants(), "Invariants failed at step 71"

    # Operation 72: delete
    del tree[2071]
    del reference[2071]
    assert tree.invariants(), "Invariants failed at step 72"

    # Operation 73: get
    assert tree.invariants(), "Invariants failed at step 73"

    # Operation 74: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 74"

    # Operation 75: get
    assert tree.invariants(), "Invariants failed at step 75"

    # Operation 76: insert
    tree[2202] = 'value_25574'
    reference[2202] = 'value_25574'
    assert tree.invariants(), "Invariants failed at step 76"

    # Operation 77: insert
    tree[8979] = 'value_102339'
    reference[8979] = 'value_102339'
    assert tree.invariants(), "Invariants failed at step 77"

    # Operation 78: delete
    del tree[2202]
    del reference[2202]
    assert tree.invariants(), "Invariants failed at step 78"

    # Operation 79: update
    tree[8979] = 'value_958634'
    reference[8979] = 'value_958634'
    assert tree.invariants(), "Invariants failed at step 79"

    # Operation 80: insert
    tree[2250] = 'value_78837'
    reference[2250] = 'value_78837'
    assert tree.invariants(), "Invariants failed at step 80"

    # Operation 81: get
    assert tree.invariants(), "Invariants failed at step 81"

    # Operation 82: update
    tree[8979] = 'value_498504'
    reference[8979] = 'value_498504'
    assert tree.invariants(), "Invariants failed at step 82"

    # Operation 83: delete
    del tree[8979]
    del reference[8979]
    assert tree.invariants(), "Invariants failed at step 83"

    # Operation 84: update
    tree[2250] = 'value_348806'
    reference[2250] = 'value_348806'
    assert tree.invariants(), "Invariants failed at step 84"

    # Operation 85: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 85"

    # Operation 86: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 86"

    # Operation 87: delete
    del tree[2250]
    del reference[2250]
    assert tree.invariants(), "Invariants failed at step 87"

    # Operation 88: get
    assert tree.invariants(), "Invariants failed at step 88"

    # Operation 89: insert
    tree[917] = 'value_536863'
    reference[917] = 'value_536863'
    assert tree.invariants(), "Invariants failed at step 89"

    # Operation 90: update
    tree[917] = 'value_649395'
    reference[917] = 'value_649395'
    assert tree.invariants(), "Invariants failed at step 90"

    # Operation 91: delete
    del tree[917]
    del reference[917]
    assert tree.invariants(), "Invariants failed at step 91"

    # Operation 92: insert
    tree[8361] = 'value_308203'
    reference[8361] = 'value_308203'
    assert tree.invariants(), "Invariants failed at step 92"

    # Operation 93: insert
    tree[2556] = 'value_591760'
    reference[2556] = 'value_591760'
    assert tree.invariants(), "Invariants failed at step 93"

    # Operation 94: insert
    tree[9754] = 'value_854154'
    reference[9754] = 'value_854154'
    assert tree.invariants(), "Invariants failed at step 94"

    # Operation 95: insert
    tree[6571] = 'value_846468'
    reference[6571] = 'value_846468'
    assert tree.invariants(), "Invariants failed at step 95"

    # Operation 96: insert
    tree[7403] = 'value_491010'
    reference[7403] = 'value_491010'
    assert tree.invariants(), "Invariants failed at step 96"

    # Operation 97: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 97"

    # Operation 98: get
    assert tree.invariants(), "Invariants failed at step 98"

    # Operation 99: insert
    tree[3053] = 'value_445349'
    reference[3053] = 'value_445349'
    assert tree.invariants(), "Invariants failed at step 99"

    # Operation 100: insert
    tree[361] = 'value_690530'
    reference[361] = 'value_690530'
    assert tree.invariants(), "Invariants failed at step 100"

    # Operation 101: insert
    tree[9056] = 'value_532465'
    reference[9056] = 'value_532465'
    assert tree.invariants(), "Invariants failed at step 101"

    # Operation 102: insert
    tree[1448] = 'value_737084'
    reference[1448] = 'value_737084'
    assert tree.invariants(), "Invariants failed at step 102"

    # Operation 103: update
    tree[1448] = 'value_113904'
    reference[1448] = 'value_113904'
    assert tree.invariants(), "Invariants failed at step 103"

    # Operation 104: update
    tree[8361] = 'value_581739'
    reference[8361] = 'value_581739'
    assert tree.invariants(), "Invariants failed at step 104"

    # Operation 105: batch_delete
    keys_to_delete = [8361, 361, 3053, 9056, 4994, 9640]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 105"

    # Operation 106: insert
    tree[4765] = 'value_958746'
    reference[4765] = 'value_958746'
    assert tree.invariants(), "Invariants failed at step 106"

    # Operation 107: batch_delete
    keys_to_delete = [1448, 2556, 7403, 8397, 3532]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 107"

    # Operation 108: delete
    del tree[9754]
    del reference[9754]
    assert tree.invariants(), "Invariants failed at step 108"

    # Operation 109: delete
    del tree[6571]
    del reference[6571]
    assert tree.invariants(), "Invariants failed at step 109"

    # Operation 110: delete
    del tree[4765]
    del reference[4765]
    assert tree.invariants(), "Invariants failed at step 110"

    # Operation 111: insert
    tree[5130] = 'value_889627'
    reference[5130] = 'value_889627'
    assert tree.invariants(), "Invariants failed at step 111"

    # Operation 112: insert
    tree[2702] = 'value_10230'
    reference[2702] = 'value_10230'
    assert tree.invariants(), "Invariants failed at step 112"

    # Operation 113: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 113"

    # Operation 114: insert
    tree[3558] = 'value_486411'
    reference[3558] = 'value_486411'
    assert tree.invariants(), "Invariants failed at step 114"

    # Operation 115: insert
    tree[8151] = 'value_502582'
    reference[8151] = 'value_502582'
    assert tree.invariants(), "Invariants failed at step 115"

    # Operation 116: update
    tree[8151] = 'value_230217'
    reference[8151] = 'value_230217'
    assert tree.invariants(), "Invariants failed at step 116"

    # Operation 117: update
    tree[5130] = 'value_338819'
    reference[5130] = 'value_338819'
    assert tree.invariants(), "Invariants failed at step 117"

    # Operation 118: delete
    del tree[3558]
    del reference[3558]
    assert tree.invariants(), "Invariants failed at step 118"

    # Operation 119: insert
    tree[7393] = 'value_625983'
    reference[7393] = 'value_625983'
    assert tree.invariants(), "Invariants failed at step 119"

    # Operation 120: insert
    tree[3938] = 'value_861208'
    reference[3938] = 'value_861208'
    assert tree.invariants(), "Invariants failed at step 120"

    # Operation 121: delete
    del tree[3938]
    del reference[3938]
    assert tree.invariants(), "Invariants failed at step 121"

    # Operation 122: get
    assert tree.invariants(), "Invariants failed at step 122"

    # Operation 123: get
    assert tree.invariants(), "Invariants failed at step 123"

    # Operation 124: insert
    tree[7740] = 'value_294891'
    reference[7740] = 'value_294891'
    assert tree.invariants(), "Invariants failed at step 124"

    # Operation 125: insert
    tree[6334] = 'value_289987'
    reference[6334] = 'value_289987'
    assert tree.invariants(), "Invariants failed at step 125"

    # Operation 126: delete
    del tree[5130]
    del reference[5130]
    assert tree.invariants(), "Invariants failed at step 126"

    # Operation 127: insert
    tree[7414] = 'value_273451'
    reference[7414] = 'value_273451'
    assert tree.invariants(), "Invariants failed at step 127"

    # Operation 128: insert
    tree[6318] = 'value_509930'
    reference[6318] = 'value_509930'
    assert tree.invariants(), "Invariants failed at step 128"

    # Operation 129: delete
    del tree[7414]
    del reference[7414]
    assert tree.invariants(), "Invariants failed at step 129"

    # Operation 130: batch_delete
    keys_to_delete = [8151, 2702, 7740, 593, 3313]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 130"

    # Operation 131: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 131"

    # Operation 132: insert
    tree[3027] = 'value_381338'
    reference[3027] = 'value_381338'
    assert tree.invariants(), "Invariants failed at step 132"

    # Operation 133: update
    tree[3027] = 'value_925136'
    reference[3027] = 'value_925136'
    assert tree.invariants(), "Invariants failed at step 133"

    # Operation 134: delete
    del tree[6318]
    del reference[6318]
    assert tree.invariants(), "Invariants failed at step 134"

    # Operation 135: get
    assert tree.invariants(), "Invariants failed at step 135"

    # Operation 136: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 136"

    # Operation 137: insert
    tree[8351] = 'value_724070'
    reference[8351] = 'value_724070'
    assert tree.invariants(), "Invariants failed at step 137"

    # Operation 138: delete
    del tree[8351]
    del reference[8351]
    assert tree.invariants(), "Invariants failed at step 138"

    # Operation 139: update
    tree[3027] = 'value_62575'
    reference[3027] = 'value_62575'
    assert tree.invariants(), "Invariants failed at step 139"

    # Operation 140: update
    tree[3027] = 'value_760407'
    reference[3027] = 'value_760407'
    assert tree.invariants(), "Invariants failed at step 140"

    # Operation 141: get
    assert tree.invariants(), "Invariants failed at step 141"

    # Operation 142: get
    assert tree.invariants(), "Invariants failed at step 142"

    # Operation 143: delete
    del tree[3027]
    del reference[3027]
    assert tree.invariants(), "Invariants failed at step 143"

    # Operation 144: insert
    tree[4717] = 'value_512672'
    reference[4717] = 'value_512672'
    assert tree.invariants(), "Invariants failed at step 144"

    # Operation 145: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 145"

    # Operation 146: insert
    tree[9234] = 'value_825089'
    reference[9234] = 'value_825089'
    assert tree.invariants(), "Invariants failed at step 146"

    # Operation 147: get
    assert tree.invariants(), "Invariants failed at step 147"

    # Operation 148: insert
    tree[1749] = 'value_933842'
    reference[1749] = 'value_933842'
    assert tree.invariants(), "Invariants failed at step 148"

    # Operation 149: delete
    del tree[9234]
    del reference[9234]
    assert tree.invariants(), "Invariants failed at step 149"

    # Operation 150: delete
    del tree[1749]
    del reference[1749]
    assert tree.invariants(), "Invariants failed at step 150"

    # Operation 151: insert
    tree[8324] = 'value_588870'
    reference[8324] = 'value_588870'
    assert tree.invariants(), "Invariants failed at step 151"

    # Operation 152: insert
    tree[6568] = 'value_84307'
    reference[6568] = 'value_84307'
    assert tree.invariants(), "Invariants failed at step 152"

    # Operation 153: insert
    tree[702] = 'value_854594'
    reference[702] = 'value_854594'
    assert tree.invariants(), "Invariants failed at step 153"

    # Operation 154: delete
    del tree[702]
    del reference[702]
    assert tree.invariants(), "Invariants failed at step 154"

    # Operation 155: insert
    tree[2538] = 'value_752025'
    reference[2538] = 'value_752025'
    assert tree.invariants(), "Invariants failed at step 155"

    # Operation 156: batch_delete
    keys_to_delete = [4717, 8324, 6334, 238, 1828]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 156"

    # Operation 157: update
    tree[2538] = 'value_464935'
    reference[2538] = 'value_464935'
    assert tree.invariants(), "Invariants failed at step 157"

    # Operation 158: insert
    tree[7077] = 'value_625368'
    reference[7077] = 'value_625368'
    assert tree.invariants(), "Invariants failed at step 158"

    # Operation 159: update
    tree[7393] = 'value_605891'
    reference[7393] = 'value_605891'
    assert tree.invariants(), "Invariants failed at step 159"

    # Operation 160: delete
    del tree[7077]
    del reference[7077]
    assert tree.invariants(), "Invariants failed at step 160"

    # Operation 161: get
    assert tree.invariants(), "Invariants failed at step 161"

    # Operation 162: get
    assert tree.invariants(), "Invariants failed at step 162"

    # Operation 163: get
    assert tree.invariants(), "Invariants failed at step 163"

    # Operation 164: insert
    tree[8675] = 'value_206916'
    reference[8675] = 'value_206916'
    assert tree.invariants(), "Invariants failed at step 164"

    # Operation 165: delete
    del tree[8675]
    del reference[8675]
    assert tree.invariants(), "Invariants failed at step 165"

    # Operation 166: insert
    tree[8380] = 'value_249731'
    reference[8380] = 'value_249731'
    assert tree.invariants(), "Invariants failed at step 166"

    # Operation 167: insert
    tree[3990] = 'value_21838'
    reference[3990] = 'value_21838'
    assert tree.invariants(), "Invariants failed at step 167"

    # Operation 168: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 168"

    # Operation 169: get
    assert tree.invariants(), "Invariants failed at step 169"

    # Operation 170: delete
    del tree[8380]
    del reference[8380]
    assert tree.invariants(), "Invariants failed at step 170"

    # Operation 171: get
    assert tree.invariants(), "Invariants failed at step 171"

    # Operation 172: get
    assert tree.invariants(), "Invariants failed at step 172"

    # Operation 173: delete
    del tree[2538]
    del reference[2538]
    assert tree.invariants(), "Invariants failed at step 173"

    # Operation 174: update
    tree[3990] = 'value_411385'
    reference[3990] = 'value_411385'
    assert tree.invariants(), "Invariants failed at step 174"

    # Operation 175: insert
    tree[2802] = 'value_823126'
    reference[2802] = 'value_823126'
    assert tree.invariants(), "Invariants failed at step 175"

    # Operation 176: delete
    del tree[3990]
    del reference[3990]
    assert tree.invariants(), "Invariants failed at step 176"

    # Operation 177: delete
    del tree[2802]
    del reference[2802]
    assert tree.invariants(), "Invariants failed at step 177"

    # Operation 178: insert
    tree[6016] = 'value_685589'
    reference[6016] = 'value_685589'
    assert tree.invariants(), "Invariants failed at step 178"

    # Operation 179: update
    tree[6016] = 'value_903368'
    reference[6016] = 'value_903368'
    assert tree.invariants(), "Invariants failed at step 179"

    # Operation 180: insert
    tree[8177] = 'value_650176'
    reference[8177] = 'value_650176'
    assert tree.invariants(), "Invariants failed at step 180"

    # Operation 181: get
    assert tree.invariants(), "Invariants failed at step 181"

    # Operation 182: get
    assert tree.invariants(), "Invariants failed at step 182"

    # Operation 183: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 183"

    # Operation 184: delete
    del tree[8177]
    del reference[8177]
    assert tree.invariants(), "Invariants failed at step 184"

    # Operation 185: get
    assert tree.invariants(), "Invariants failed at step 185"

    # Operation 186: get
    assert tree.invariants(), "Invariants failed at step 186"

    # Operation 187: delete
    del tree[6016]
    del reference[6016]
    assert tree.invariants(), "Invariants failed at step 187"

    # Operation 188: insert
    tree[3446] = 'value_580591'
    reference[3446] = 'value_580591'
    assert tree.invariants(), "Invariants failed at step 188"

    # Operation 189: update
    tree[7393] = 'value_358655'
    reference[7393] = 'value_358655'
    assert tree.invariants(), "Invariants failed at step 189"

    # Operation 190: insert
    tree[1140] = 'value_7662'
    reference[1140] = 'value_7662'
    assert tree.invariants(), "Invariants failed at step 190"

    # Operation 191: get
    assert tree.invariants(), "Invariants failed at step 191"

    # Operation 192: update
    tree[7393] = 'value_618276'
    reference[7393] = 'value_618276'
    assert tree.invariants(), "Invariants failed at step 192"

    # Operation 193: delete
    del tree[3446]
    del reference[3446]
    assert tree.invariants(), "Invariants failed at step 193"

    # Operation 194: insert
    tree[6186] = 'value_736698'
    reference[6186] = 'value_736698'
    assert tree.invariants(), "Invariants failed at step 194"

    # Operation 195: delete
    del tree[1140]
    del reference[1140]
    assert tree.invariants(), "Invariants failed at step 195"

    # Operation 196: insert
    tree[9535] = 'value_238238'
    reference[9535] = 'value_238238'
    assert tree.invariants(), "Invariants failed at step 196"

    # Operation 197: update
    tree[7393] = 'value_339465'
    reference[7393] = 'value_339465'
    assert tree.invariants(), "Invariants failed at step 197"

    # Operation 198: get
    assert tree.invariants(), "Invariants failed at step 198"

    # Operation 199: delete
    del tree[7393]
    del reference[7393]
    assert tree.invariants(), "Invariants failed at step 199"

    # Operation 200: delete
    del tree[6568]
    del reference[6568]
    assert tree.invariants(), "Invariants failed at step 200"

    # Operation 201: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 201"

    # Operation 202: get
    assert tree.invariants(), "Invariants failed at step 202"

    # Operation 203: insert
    tree[5020] = 'value_982877'
    reference[5020] = 'value_982877'
    assert tree.invariants(), "Invariants failed at step 203"

    # Operation 204: get
    assert tree.invariants(), "Invariants failed at step 204"

    # Operation 205: delete
    del tree[5020]
    del reference[5020]
    assert tree.invariants(), "Invariants failed at step 205"

    # Operation 206: insert
    tree[70] = 'value_564316'
    reference[70] = 'value_564316'
    assert tree.invariants(), "Invariants failed at step 206"

    # Operation 207: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 207"

    # Operation 208: insert
    tree[6185] = 'value_155920'
    reference[6185] = 'value_155920'
    assert tree.invariants(), "Invariants failed at step 208"

    # Operation 209: insert
    tree[3423] = 'value_267866'
    reference[3423] = 'value_267866'
    assert tree.invariants(), "Invariants failed at step 209"

    # Operation 210: get
    assert tree.invariants(), "Invariants failed at step 210"

    # Operation 211: delete
    del tree[6186]
    del reference[6186]
    assert tree.invariants(), "Invariants failed at step 211"

    # Operation 212: delete
    del tree[9535]
    del reference[9535]
    assert tree.invariants(), "Invariants failed at step 212"

    # Operation 213: delete
    del tree[6185]
    del reference[6185]
    assert tree.invariants(), "Invariants failed at step 213"

    # Operation 214: delete
    del tree[3423]
    del reference[3423]
    assert tree.invariants(), "Invariants failed at step 214"

    # Operation 215: insert
    tree[3589] = 'value_76585'
    reference[3589] = 'value_76585'
    assert tree.invariants(), "Invariants failed at step 215"

    # Operation 216: get
    assert tree.invariants(), "Invariants failed at step 216"

    # Operation 217: update
    tree[3589] = 'value_650329'
    reference[3589] = 'value_650329'
    assert tree.invariants(), "Invariants failed at step 217"

    # Operation 218: update
    tree[3589] = 'value_79804'
    reference[3589] = 'value_79804'
    assert tree.invariants(), "Invariants failed at step 218"

    # Operation 219: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 219"

    # Operation 220: delete
    del tree[70]
    del reference[70]
    assert tree.invariants(), "Invariants failed at step 220"

    # Operation 221: update
    tree[3589] = 'value_423649'
    reference[3589] = 'value_423649'
    assert tree.invariants(), "Invariants failed at step 221"

    # Operation 222: insert
    tree[4033] = 'value_43947'
    reference[4033] = 'value_43947'
    assert tree.invariants(), "Invariants failed at step 222"

    # Operation 223: update
    tree[3589] = 'value_645734'
    reference[3589] = 'value_645734'
    assert tree.invariants(), "Invariants failed at step 223"

    # Operation 224: delete
    del tree[3589]
    del reference[3589]
    assert tree.invariants(), "Invariants failed at step 224"

    # Operation 225: delete
    del tree[4033]
    del reference[4033]
    assert tree.invariants(), "Invariants failed at step 225"

    # Operation 226: get
    assert tree.invariants(), "Invariants failed at step 226"

    # Operation 227: insert
    tree[2059] = 'value_932303'
    reference[2059] = 'value_932303'
    assert tree.invariants(), "Invariants failed at step 227"

    # Operation 228: insert
    tree[3648] = 'value_173055'
    reference[3648] = 'value_173055'
    assert tree.invariants(), "Invariants failed at step 228"

    # Operation 229: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 229"

    # Operation 230: delete
    del tree[3648]
    del reference[3648]
    assert tree.invariants(), "Invariants failed at step 230"

    # Operation 231: get
    assert tree.invariants(), "Invariants failed at step 231"

    # Operation 232: get
    assert tree.invariants(), "Invariants failed at step 232"

    # Operation 233: delete
    del tree[2059]
    del reference[2059]
    assert tree.invariants(), "Invariants failed at step 233"

    # Operation 234: insert
    tree[248] = 'value_198552'
    reference[248] = 'value_198552'
    assert tree.invariants(), "Invariants failed at step 234"

    # Operation 235: get
    assert tree.invariants(), "Invariants failed at step 235"

    # Operation 236: delete
    del tree[248]
    del reference[248]
    assert tree.invariants(), "Invariants failed at step 236"

    # Operation 237: insert
    tree[201] = 'value_772525'
    reference[201] = 'value_772525'
    assert tree.invariants(), "Invariants failed at step 237"

    # Operation 238: insert
    tree[6402] = 'value_214699'
    reference[6402] = 'value_214699'
    assert tree.invariants(), "Invariants failed at step 238"

    # Operation 239: insert
    tree[8779] = 'value_328343'
    reference[8779] = 'value_328343'
    assert tree.invariants(), "Invariants failed at step 239"

    # Operation 240: get
    assert tree.invariants(), "Invariants failed at step 240"

    # Operation 241: delete
    del tree[6402]
    del reference[6402]
    assert tree.invariants(), "Invariants failed at step 241"

    # Operation 242: update
    tree[8779] = 'value_586390'
    reference[8779] = 'value_586390'
    assert tree.invariants(), "Invariants failed at step 242"

    # Operation 243: insert
    tree[5628] = 'value_705590'
    reference[5628] = 'value_705590'
    assert tree.invariants(), "Invariants failed at step 243"

    # Operation 244: insert
    tree[9756] = 'value_886787'
    reference[9756] = 'value_886787'
    assert tree.invariants(), "Invariants failed at step 244"

    # Operation 245: insert
    tree[9565] = 'value_595870'
    reference[9565] = 'value_595870'
    assert tree.invariants(), "Invariants failed at step 245"

    # Operation 246: get
    assert tree.invariants(), "Invariants failed at step 246"

    # Operation 247: update
    tree[5628] = 'value_218443'
    reference[5628] = 'value_218443'
    assert tree.invariants(), "Invariants failed at step 247"

    # Operation 248: delete
    del tree[8779]
    del reference[8779]
    assert tree.invariants(), "Invariants failed at step 248"

    # Operation 249: get
    assert tree.invariants(), "Invariants failed at step 249"

    # Operation 250: insert
    tree[5147] = 'value_214717'
    reference[5147] = 'value_214717'
    assert tree.invariants(), "Invariants failed at step 250"

    # Operation 251: delete
    del tree[9565]
    del reference[9565]
    assert tree.invariants(), "Invariants failed at step 251"

    # Operation 252: delete
    del tree[9756]
    del reference[9756]
    assert tree.invariants(), "Invariants failed at step 252"

    # Operation 253: insert
    tree[217] = 'value_662793'
    reference[217] = 'value_662793'
    assert tree.invariants(), "Invariants failed at step 253"

    # Operation 254: get
    assert tree.invariants(), "Invariants failed at step 254"

    # Operation 255: insert
    tree[8201] = 'value_435956'
    reference[8201] = 'value_435956'
    assert tree.invariants(), "Invariants failed at step 255"

    # Operation 256: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 256"

    # Operation 257: delete
    del tree[5628]
    del reference[5628]
    assert tree.invariants(), "Invariants failed at step 257"

    # Operation 258: insert
    tree[2690] = 'value_315550'
    reference[2690] = 'value_315550'
    assert tree.invariants(), "Invariants failed at step 258"

    # Operation 259: batch_delete
    keys_to_delete = [8201, 2690, 6233, 2556]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 259"

    # Operation 260: update
    tree[201] = 'value_479178'
    reference[201] = 'value_479178'
    assert tree.invariants(), "Invariants failed at step 260"

    # Operation 261: delete
    del tree[5147]
    del reference[5147]
    assert tree.invariants(), "Invariants failed at step 261"

    # Operation 262: update
    tree[217] = 'value_969077'
    reference[217] = 'value_969077'
    assert tree.invariants(), "Invariants failed at step 262"

    # Operation 263: update
    tree[201] = 'value_562064'
    reference[201] = 'value_562064'
    assert tree.invariants(), "Invariants failed at step 263"

    # Operation 264: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 264"

    # Operation 265: get
    assert tree.invariants(), "Invariants failed at step 265"

    # Operation 266: insert
    tree[6293] = 'value_174465'
    reference[6293] = 'value_174465'
    assert tree.invariants(), "Invariants failed at step 266"

    # Operation 267: insert
    tree[9196] = 'value_448039'
    reference[9196] = 'value_448039'
    assert tree.invariants(), "Invariants failed at step 267"

    # Operation 268: insert
    tree[7216] = 'value_381331'
    reference[7216] = 'value_381331'
    assert tree.invariants(), "Invariants failed at step 268"

    # Operation 269: delete
    del tree[9196]
    del reference[9196]
    assert tree.invariants(), "Invariants failed at step 269"

    # Operation 270: update
    tree[7216] = 'value_212135'
    reference[7216] = 'value_212135'
    assert tree.invariants(), "Invariants failed at step 270"

    # Operation 271: insert
    tree[6113] = 'value_662517'
    reference[6113] = 'value_662517'
    assert tree.invariants(), "Invariants failed at step 271"

    # Operation 272: delete
    del tree[201]
    del reference[201]
    assert tree.invariants(), "Invariants failed at step 272"

    # Operation 273: update
    tree[217] = 'value_996095'
    reference[217] = 'value_996095'
    assert tree.invariants(), "Invariants failed at step 273"

    # Operation 274: delete
    del tree[7216]
    del reference[7216]
    assert tree.invariants(), "Invariants failed at step 274"

    # Operation 275: get
    assert tree.invariants(), "Invariants failed at step 275"

    # Operation 276: get
    assert tree.invariants(), "Invariants failed at step 276"

    # Operation 277: delete
    del tree[6113]
    del reference[6113]
    assert tree.invariants(), "Invariants failed at step 277"

    # Operation 278: update
    tree[217] = 'value_656090'
    reference[217] = 'value_656090'
    assert tree.invariants(), "Invariants failed at step 278"

    # Operation 279: delete
    del tree[217]
    del reference[217]
    assert tree.invariants(), "Invariants failed at step 279"

    # Operation 280: get
    assert tree.invariants(), "Invariants failed at step 280"

    # Operation 281: get
    assert tree.invariants(), "Invariants failed at step 281"

    # Operation 282: delete
    del tree[6293]
    del reference[6293]
    assert tree.invariants(), "Invariants failed at step 282"

    # Operation 283: get
    assert tree.invariants(), "Invariants failed at step 283"

    # Operation 284: insert
    tree[3022] = 'value_708600'
    reference[3022] = 'value_708600'
    assert tree.invariants(), "Invariants failed at step 284"

    # Operation 285: insert
    tree[2567] = 'value_568759'
    reference[2567] = 'value_568759'
    assert tree.invariants(), "Invariants failed at step 285"

    # Operation 286: get
    assert tree.invariants(), "Invariants failed at step 286"

    # Operation 287: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 287"

    # Operation 288: update
    tree[2567] = 'value_537296'
    reference[2567] = 'value_537296'
    assert tree.invariants(), "Invariants failed at step 288"

    # Operation 289: get
    assert tree.invariants(), "Invariants failed at step 289"

    # Operation 290: delete
    del tree[3022]
    del reference[3022]
    assert tree.invariants(), "Invariants failed at step 290"

    # Operation 291: get
    assert tree.invariants(), "Invariants failed at step 291"

    # Operation 292: insert
    tree[4561] = 'value_689384'
    reference[4561] = 'value_689384'
    assert tree.invariants(), "Invariants failed at step 292"

    # Operation 293: update
    tree[4561] = 'value_369293'
    reference[4561] = 'value_369293'
    assert tree.invariants(), "Invariants failed at step 293"

    # Operation 294: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 294"

    # Operation 295: update
    tree[2567] = 'value_821871'
    reference[2567] = 'value_821871'
    assert tree.invariants(), "Invariants failed at step 295"

    # Operation 296: delete
    del tree[2567]
    del reference[2567]
    assert tree.invariants(), "Invariants failed at step 296"

    # Operation 297: get
    assert tree.invariants(), "Invariants failed at step 297"

    # Operation 298: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 298"

    # Operation 299: update
    tree[4561] = 'value_777351'
    reference[4561] = 'value_777351'
    assert tree.invariants(), "Invariants failed at step 299"

    # Operation 300: delete
    del tree[4561]
    del reference[4561]
    assert tree.invariants(), "Invariants failed at step 300"

    # Operation 301: insert
    tree[2558] = 'value_480826'
    reference[2558] = 'value_480826'
    assert tree.invariants(), "Invariants failed at step 301"

    # Operation 302: delete
    del tree[2558]
    del reference[2558]
    assert tree.invariants(), "Invariants failed at step 302"

    # Operation 303: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 303"

    # Operation 304: get
    assert tree.invariants(), "Invariants failed at step 304"

    # Operation 305: insert
    tree[6740] = 'value_600729'
    reference[6740] = 'value_600729'
    assert tree.invariants(), "Invariants failed at step 305"

    # Operation 306: insert
    tree[1107] = 'value_270907'
    reference[1107] = 'value_270907'
    assert tree.invariants(), "Invariants failed at step 306"

    # Operation 307: insert
    tree[2461] = 'value_85860'
    reference[2461] = 'value_85860'
    assert tree.invariants(), "Invariants failed at step 307"

    # Operation 308: insert
    tree[1636] = 'value_850300'
    reference[1636] = 'value_850300'
    assert tree.invariants(), "Invariants failed at step 308"

    # Operation 309: insert
    tree[45] = 'value_392792'
    reference[45] = 'value_392792'
    assert tree.invariants(), "Invariants failed at step 309"

    # Operation 310: get
    assert tree.invariants(), "Invariants failed at step 310"

    # Operation 311: get
    assert tree.invariants(), "Invariants failed at step 311"

    # Operation 312: insert
    tree[3038] = 'value_660556'
    reference[3038] = 'value_660556'
    assert tree.invariants(), "Invariants failed at step 312"

    # Operation 313: insert
    tree[6092] = 'value_920811'
    reference[6092] = 'value_920811'
    assert tree.invariants(), "Invariants failed at step 313"

    # Operation 314: delete
    del tree[1636]
    del reference[1636]
    assert tree.invariants(), "Invariants failed at step 314"

    # Operation 315: update
    tree[6092] = 'value_771910'
    reference[6092] = 'value_771910'
    assert tree.invariants(), "Invariants failed at step 315"

    # Operation 316: insert
    tree[6625] = 'value_723357'
    reference[6625] = 'value_723357'
    assert tree.invariants(), "Invariants failed at step 316"

    # Operation 317: delete
    del tree[45]
    del reference[45]
    assert tree.invariants(), "Invariants failed at step 317"

    # Operation 318: insert
    tree[6276] = 'value_431601'
    reference[6276] = 'value_431601'
    assert tree.invariants(), "Invariants failed at step 318"

    # Operation 319: insert
    tree[681] = 'value_542607'
    reference[681] = 'value_542607'
    assert tree.invariants(), "Invariants failed at step 319"

    # Operation 320: insert
    tree[5562] = 'value_16138'
    reference[5562] = 'value_16138'
    assert tree.invariants(), "Invariants failed at step 320"

    # Operation 321: get
    assert tree.invariants(), "Invariants failed at step 321"

    # Operation 322: insert
    tree[7118] = 'value_620695'
    reference[7118] = 'value_620695'
    assert tree.invariants(), "Invariants failed at step 322"

    # Operation 323: delete
    del tree[6092]
    del reference[6092]
    assert tree.invariants(), "Invariants failed at step 323"

    # Operation 324: batch_delete
    keys_to_delete = [681, 6625, 6740, 5562, 4567, 1976]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 324"

    # Operation 325: get
    assert tree.invariants(), "Invariants failed at step 325"

    # Operation 326: delete
    del tree[1107]
    del reference[1107]
    assert tree.invariants(), "Invariants failed at step 326"

    # Operation 327: get
    assert tree.invariants(), "Invariants failed at step 327"

    # Operation 328: get
    assert tree.invariants(), "Invariants failed at step 328"

    # Operation 329: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 329"

    # Operation 330: insert
    tree[9206] = 'value_744146'
    reference[9206] = 'value_744146'
    assert tree.invariants(), "Invariants failed at step 330"

    # Operation 331: delete
    del tree[7118]
    del reference[7118]
    assert tree.invariants(), "Invariants failed at step 331"

    # Operation 332: insert
    tree[5106] = 'value_177022'
    reference[5106] = 'value_177022'
    assert tree.invariants(), "Invariants failed at step 332"

    # Operation 333: delete
    del tree[2461]
    del reference[2461]
    assert tree.invariants(), "Invariants failed at step 333"

    # Operation 334: delete
    del tree[3038]
    del reference[3038]
    assert tree.invariants(), "Invariants failed at step 334"

    # Operation 335: get
    assert tree.invariants(), "Invariants failed at step 335"

    # Operation 336: delete
    del tree[9206]
    del reference[9206]
    assert tree.invariants(), "Invariants failed at step 336"

    # Operation 337: insert
    tree[1293] = 'value_895712'
    reference[1293] = 'value_895712'
    assert tree.invariants(), "Invariants failed at step 337"

    # Operation 338: insert
    tree[8238] = 'value_473546'
    reference[8238] = 'value_473546'
    assert tree.invariants(), "Invariants failed at step 338"

    # Operation 339: insert
    tree[264] = 'value_462011'
    reference[264] = 'value_462011'
    assert tree.invariants(), "Invariants failed at step 339"

    # Operation 340: insert
    tree[6844] = 'value_419656'
    reference[6844] = 'value_419656'
    assert tree.invariants(), "Invariants failed at step 340"

    # Operation 341: delete
    del tree[1293]
    del reference[1293]
    assert tree.invariants(), "Invariants failed at step 341"

    # Operation 342: get
    assert tree.invariants(), "Invariants failed at step 342"

    # Operation 343: insert
    tree[2883] = 'value_669871'
    reference[2883] = 'value_669871'
    assert tree.invariants(), "Invariants failed at step 343"

    # Operation 344: insert
    tree[6186] = 'value_501480'
    reference[6186] = 'value_501480'
    assert tree.invariants(), "Invariants failed at step 344"

    # Operation 345: delete
    del tree[6276]
    del reference[6276]
    assert tree.invariants(), "Invariants failed at step 345"

    # Operation 346: get
    assert tree.invariants(), "Invariants failed at step 346"

    # Operation 347: delete
    del tree[6844]
    del reference[6844]
    assert tree.invariants(), "Invariants failed at step 347"

    # Operation 348: insert
    tree[3964] = 'value_298087'
    reference[3964] = 'value_298087'
    assert tree.invariants(), "Invariants failed at step 348"

    # Operation 349: get
    assert tree.invariants(), "Invariants failed at step 349"

    # Operation 350: delete
    del tree[264]
    del reference[264]
    assert tree.invariants(), "Invariants failed at step 350"

    # Operation 351: insert
    tree[3205] = 'value_795310'
    reference[3205] = 'value_795310'
    assert tree.invariants(), "Invariants failed at step 351"

    # Operation 352: insert
    tree[1807] = 'value_669083'
    reference[1807] = 'value_669083'
    assert tree.invariants(), "Invariants failed at step 352"

    # Operation 353: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 353"

    # Operation 354: insert
    tree[2648] = 'value_612778'
    reference[2648] = 'value_612778'
    assert tree.invariants(), "Invariants failed at step 354"

    # Operation 355: get
    assert tree.invariants(), "Invariants failed at step 355"

    # Operation 356: insert
    tree[8444] = 'value_195845'
    reference[8444] = 'value_195845'
    assert tree.invariants(), "Invariants failed at step 356"

    # Operation 357: delete
    del tree[1807]
    del reference[1807]
    assert tree.invariants(), "Invariants failed at step 357"

    # Operation 358: update
    tree[8238] = 'value_363743'
    reference[8238] = 'value_363743'
    assert tree.invariants(), "Invariants failed at step 358"

    # Operation 359: delete
    del tree[2883]
    del reference[2883]
    assert tree.invariants(), "Invariants failed at step 359"

    # Operation 360: update
    tree[3205] = 'value_99336'
    reference[3205] = 'value_99336'
    assert tree.invariants(), "Invariants failed at step 360"

    # Operation 361: get
    assert tree.invariants(), "Invariants failed at step 361"

    # Operation 362: delete
    del tree[8238]
    del reference[8238]
    assert tree.invariants(), "Invariants failed at step 362"

    # Operation 363: delete
    del tree[3205]
    del reference[3205]
    assert tree.invariants(), "Invariants failed at step 363"

    # Operation 364: batch_delete
    keys_to_delete = [2648, 3964, 6077, 7051]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 364"

    # Operation 365: delete
    del tree[8444]
    del reference[8444]
    assert tree.invariants(), "Invariants failed at step 365"

    # Operation 366: get
    assert tree.invariants(), "Invariants failed at step 366"

    # Operation 367: update
    tree[6186] = 'value_60962'
    reference[6186] = 'value_60962'
    assert tree.invariants(), "Invariants failed at step 367"

    # Operation 368: get
    assert tree.invariants(), "Invariants failed at step 368"

    # Operation 369: get
    assert tree.invariants(), "Invariants failed at step 369"

    # Operation 370: delete
    del tree[5106]
    del reference[5106]
    assert tree.invariants(), "Invariants failed at step 370"

    # Operation 371: delete
    del tree[6186]
    del reference[6186]
    assert tree.invariants(), "Invariants failed at step 371"

    # Operation 372: get
    assert tree.invariants(), "Invariants failed at step 372"

    # Operation 373: get
    assert tree.invariants(), "Invariants failed at step 373"

    # Operation 374: insert
    tree[4665] = 'value_387123'
    reference[4665] = 'value_387123'
    assert tree.invariants(), "Invariants failed at step 374"

    # Operation 375: get
    assert tree.invariants(), "Invariants failed at step 375"

    # Operation 376: get
    assert tree.invariants(), "Invariants failed at step 376"

    # Operation 377: get
    assert tree.invariants(), "Invariants failed at step 377"

    # Operation 378: delete
    del tree[4665]
    del reference[4665]
    assert tree.invariants(), "Invariants failed at step 378"

    # Operation 379: insert
    tree[3480] = 'value_913700'
    reference[3480] = 'value_913700'
    assert tree.invariants(), "Invariants failed at step 379"

    # Operation 380: get
    assert tree.invariants(), "Invariants failed at step 380"

    # Operation 381: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 381"

    # Operation 382: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 382"

    # Operation 383: get
    assert tree.invariants(), "Invariants failed at step 383"

    # Operation 384: get
    assert tree.invariants(), "Invariants failed at step 384"

    # Operation 385: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 385"

    # Operation 386: delete
    del tree[3480]
    del reference[3480]
    assert tree.invariants(), "Invariants failed at step 386"

    # Operation 387: get
    assert tree.invariants(), "Invariants failed at step 387"

    # Operation 388: insert
    tree[9277] = 'value_720904'
    reference[9277] = 'value_720904'
    assert tree.invariants(), "Invariants failed at step 388"

    # Operation 389: get
    assert tree.invariants(), "Invariants failed at step 389"

    # Operation 390: insert
    tree[6835] = 'value_572327'
    reference[6835] = 'value_572327'
    assert tree.invariants(), "Invariants failed at step 390"

    # Operation 391: delete
    del tree[6835]
    del reference[6835]
    assert tree.invariants(), "Invariants failed at step 391"

    # Operation 392: delete
    del tree[9277]
    del reference[9277]
    assert tree.invariants(), "Invariants failed at step 392"

    # Operation 393: insert
    tree[4802] = 'value_773590'
    reference[4802] = 'value_773590'
    assert tree.invariants(), "Invariants failed at step 393"

    # Operation 394: insert
    tree[4852] = 'value_880637'
    reference[4852] = 'value_880637'
    assert tree.invariants(), "Invariants failed at step 394"

    # Operation 395: delete
    del tree[4852]
    del reference[4852]
    assert tree.invariants(), "Invariants failed at step 395"

    # Operation 396: get
    assert tree.invariants(), "Invariants failed at step 396"

    # Operation 397: delete
    del tree[4802]
    del reference[4802]
    assert tree.invariants(), "Invariants failed at step 397"

    # Operation 398: get
    assert tree.invariants(), "Invariants failed at step 398"

    # Operation 399: insert
    tree[6552] = 'value_860851'
    reference[6552] = 'value_860851'
    assert tree.invariants(), "Invariants failed at step 399"

    # Operation 400: update
    tree[6552] = 'value_61569'
    reference[6552] = 'value_61569'
    assert tree.invariants(), "Invariants failed at step 400"

    # Operation 401: insert
    tree[4221] = 'value_158519'
    reference[4221] = 'value_158519'
    assert tree.invariants(), "Invariants failed at step 401"

    # Operation 402: insert
    tree[6494] = 'value_219673'
    reference[6494] = 'value_219673'
    assert tree.invariants(), "Invariants failed at step 402"

    # Operation 403: insert
    tree[6135] = 'value_811023'
    reference[6135] = 'value_811023'
    assert tree.invariants(), "Invariants failed at step 403"

    # Operation 404: update
    tree[6552] = 'value_137460'
    reference[6552] = 'value_137460'
    assert tree.invariants(), "Invariants failed at step 404"

    # Operation 405: insert
    tree[1469] = 'value_888405'
    reference[1469] = 'value_888405'
    assert tree.invariants(), "Invariants failed at step 405"

    # Operation 406: delete
    del tree[1469]
    del reference[1469]
    assert tree.invariants(), "Invariants failed at step 406"

    # Operation 407: insert
    tree[4108] = 'value_151147'
    reference[4108] = 'value_151147'
    assert tree.invariants(), "Invariants failed at step 407"

    # Operation 408: insert
    tree[4581] = 'value_692711'
    reference[4581] = 'value_692711'
    assert tree.invariants(), "Invariants failed at step 408"

    # Verify final consistency
    assert len(tree) == len(reference), "Length mismatch"
    for key, value in reference.items():
        assert tree[key] == value, f"Value mismatch for {key}"
    print("Reproduction completed successfully")

if __name__ == "__main__":
    reproduce_failure()
