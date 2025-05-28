"""
Fuzz test failure reproduction
Seed: 282474
Capacity: 3
Failed at operation: 309
"""

from bplus_tree import BPlusTreeMap
from collections import OrderedDict

def reproduce_failure():
    tree = BPlusTreeMap(capacity=3)
    reference = OrderedDict()

    # Operation 166: delete
    del tree[9499]
    del reference[9499]
    assert tree.invariants(), "Invariants failed at step 1"

    # Operation 167: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 2"

    # Operation 168: delete
    del tree[6462]
    del reference[6462]
    assert tree.invariants(), "Invariants failed at step 3"

    # Operation 169: update
    tree[5960] = 'value_660074'
    reference[5960] = 'value_660074'
    assert tree.invariants(), "Invariants failed at step 4"

    # Operation 170: update
    tree[5960] = 'value_53074'
    reference[5960] = 'value_53074'
    assert tree.invariants(), "Invariants failed at step 5"

    # Operation 171: get
    assert tree.invariants(), "Invariants failed at step 6"

    # Operation 172: insert
    tree[9146] = 'value_857507'
    reference[9146] = 'value_857507'
    assert tree.invariants(), "Invariants failed at step 7"

    # Operation 173: insert
    tree[7936] = 'value_261164'
    reference[7936] = 'value_261164'
    assert tree.invariants(), "Invariants failed at step 8"

    # Operation 174: get
    assert tree.invariants(), "Invariants failed at step 9"

    # Operation 175: insert
    tree[2881] = 'value_275124'
    reference[2881] = 'value_275124'
    assert tree.invariants(), "Invariants failed at step 10"

    # Operation 176: update
    tree[7936] = 'value_363385'
    reference[7936] = 'value_363385'
    assert tree.invariants(), "Invariants failed at step 11"

    # Operation 177: insert
    tree[3385] = 'value_323500'
    reference[3385] = 'value_323500'
    assert tree.invariants(), "Invariants failed at step 12"

    # Operation 178: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 13"

    # Operation 179: delete
    del tree[9146]
    del reference[9146]
    assert tree.invariants(), "Invariants failed at step 14"

    # Operation 180: delete
    del tree[5960]
    del reference[5960]
    assert tree.invariants(), "Invariants failed at step 15"

    # Operation 181: get
    assert tree.invariants(), "Invariants failed at step 16"

    # Operation 182: get
    assert tree.invariants(), "Invariants failed at step 17"

    # Operation 183: insert
    tree[4635] = 'value_548557'
    reference[4635] = 'value_548557'
    assert tree.invariants(), "Invariants failed at step 18"

    # Operation 184: insert
    tree[8189] = 'value_852027'
    reference[8189] = 'value_852027'
    assert tree.invariants(), "Invariants failed at step 19"

    # Operation 185: delete
    del tree[2881]
    del reference[2881]
    assert tree.invariants(), "Invariants failed at step 20"

    # Operation 186: delete_nonexistent
    assert tree.invariants(), "Invariants failed at step 21"

    # Operation 187: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 22"

    # Operation 188: delete
    del tree[4635]
    del reference[4635]
    assert tree.invariants(), "Invariants failed at step 23"

    # Operation 189: get
    assert tree.invariants(), "Invariants failed at step 24"

    # Operation 190: delete
    del tree[7936]
    del reference[7936]
    assert tree.invariants(), "Invariants failed at step 25"

    # Operation 191: delete
    del tree[8189]
    del reference[8189]
    assert tree.invariants(), "Invariants failed at step 26"

    # Operation 192: insert
    tree[6229] = 'value_251796'
    reference[6229] = 'value_251796'
    assert tree.invariants(), "Invariants failed at step 27"

    # Operation 193: insert
    tree[229] = 'value_23873'
    reference[229] = 'value_23873'
    assert tree.invariants(), "Invariants failed at step 28"

    # Operation 194: insert
    tree[8607] = 'value_571880'
    reference[8607] = 'value_571880'
    assert tree.invariants(), "Invariants failed at step 29"

    # Operation 195: delete
    del tree[229]
    del reference[229]
    assert tree.invariants(), "Invariants failed at step 30"

    # Operation 196: insert
    tree[541] = 'value_87443'
    reference[541] = 'value_87443'
    assert tree.invariants(), "Invariants failed at step 31"

    # Operation 197: get
    assert tree.invariants(), "Invariants failed at step 32"

    # Operation 198: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 33"

    # Operation 199: get
    assert tree.invariants(), "Invariants failed at step 34"

    # Operation 200: update
    tree[6229] = 'value_101747'
    reference[6229] = 'value_101747'
    assert tree.invariants(), "Invariants failed at step 35"

    # Operation 201: get
    assert tree.invariants(), "Invariants failed at step 36"

    # Operation 202: delete
    del tree[8607]
    del reference[8607]
    assert tree.invariants(), "Invariants failed at step 37"

    # Operation 203: insert
    tree[6486] = 'value_413522'
    reference[6486] = 'value_413522'
    assert tree.invariants(), "Invariants failed at step 38"

    # Operation 204: insert
    tree[886] = 'value_484981'
    reference[886] = 'value_484981'
    assert tree.invariants(), "Invariants failed at step 39"

    # Operation 205: delete
    del tree[6229]
    del reference[6229]
    assert tree.invariants(), "Invariants failed at step 40"

    # Operation 206: insert
    tree[4272] = 'value_741389'
    reference[4272] = 'value_741389'
    assert tree.invariants(), "Invariants failed at step 41"

    # Operation 207: insert
    tree[2845] = 'value_595627'
    reference[2845] = 'value_595627'
    assert tree.invariants(), "Invariants failed at step 42"

    # Operation 208: update
    tree[3385] = 'value_167590'
    reference[3385] = 'value_167590'
    assert tree.invariants(), "Invariants failed at step 43"

    # Operation 209: get
    assert tree.invariants(), "Invariants failed at step 44"

    # Operation 210: delete
    del tree[886]
    del reference[886]
    assert tree.invariants(), "Invariants failed at step 45"

    # Operation 211: update
    tree[6486] = 'value_959796'
    reference[6486] = 'value_959796'
    assert tree.invariants(), "Invariants failed at step 46"

    # Operation 212: update
    tree[3385] = 'value_385887'
    reference[3385] = 'value_385887'
    assert tree.invariants(), "Invariants failed at step 47"

    # Operation 213: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 48"

    # Operation 214: insert
    tree[2794] = 'value_833280'
    reference[2794] = 'value_833280'
    assert tree.invariants(), "Invariants failed at step 49"

    # Operation 215: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 50"

    # Operation 216: delete
    del tree[3385]
    del reference[3385]
    assert tree.invariants(), "Invariants failed at step 51"

    # Operation 217: update
    tree[2794] = 'value_657682'
    reference[2794] = 'value_657682'
    assert tree.invariants(), "Invariants failed at step 52"

    # Operation 218: update
    tree[2794] = 'value_938076'
    reference[2794] = 'value_938076'
    assert tree.invariants(), "Invariants failed at step 53"

    # Operation 219: insert
    tree[5365] = 'value_999924'
    reference[5365] = 'value_999924'
    assert tree.invariants(), "Invariants failed at step 54"

    # Operation 220: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 55"

    # Operation 221: delete
    del tree[2794]
    del reference[2794]
    assert tree.invariants(), "Invariants failed at step 56"

    # Operation 222: insert
    tree[5894] = 'value_917874'
    reference[5894] = 'value_917874'
    assert tree.invariants(), "Invariants failed at step 57"

    # Operation 223: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 58"

    # Operation 224: insert
    tree[1225] = 'value_271815'
    reference[1225] = 'value_271815'
    assert tree.invariants(), "Invariants failed at step 59"

    # Operation 225: get
    assert tree.invariants(), "Invariants failed at step 60"

    # Operation 226: delete
    del tree[6486]
    del reference[6486]
    assert tree.invariants(), "Invariants failed at step 61"

    # Operation 227: insert
    tree[9945] = 'value_7347'
    reference[9945] = 'value_7347'
    assert tree.invariants(), "Invariants failed at step 62"

    # Operation 228: insert
    tree[1825] = 'value_796152'
    reference[1825] = 'value_796152'
    assert tree.invariants(), "Invariants failed at step 63"

    # Operation 229: delete
    del tree[541]
    del reference[541]
    assert tree.invariants(), "Invariants failed at step 64"

    # Operation 230: delete
    del tree[4272]
    del reference[4272]
    assert tree.invariants(), "Invariants failed at step 65"

    # Operation 231: get
    assert tree.invariants(), "Invariants failed at step 66"

    # Operation 232: update
    tree[1825] = 'value_891488'
    reference[1825] = 'value_891488'
    assert tree.invariants(), "Invariants failed at step 67"

    # Operation 233: get
    assert tree.invariants(), "Invariants failed at step 68"

    # Operation 234: insert
    tree[6317] = 'value_350779'
    reference[6317] = 'value_350779'
    assert tree.invariants(), "Invariants failed at step 69"

    # Operation 235: get
    assert tree.invariants(), "Invariants failed at step 70"

    # Operation 236: insert
    tree[8896] = 'value_795617'
    reference[8896] = 'value_795617'
    assert tree.invariants(), "Invariants failed at step 71"

    # Operation 237: insert
    tree[7675] = 'value_141720'
    reference[7675] = 'value_141720'
    assert tree.invariants(), "Invariants failed at step 72"

    # Operation 238: get
    assert tree.invariants(), "Invariants failed at step 73"

    # Operation 239: update
    tree[8896] = 'value_24002'
    reference[8896] = 'value_24002'
    assert tree.invariants(), "Invariants failed at step 74"

    # Operation 240: delete
    del tree[1225]
    del reference[1225]
    assert tree.invariants(), "Invariants failed at step 75"

    # Operation 241: get
    assert tree.invariants(), "Invariants failed at step 76"

    # Operation 242: delete
    del tree[8896]
    del reference[8896]
    assert tree.invariants(), "Invariants failed at step 77"

    # Operation 243: insert
    tree[7619] = 'value_191230'
    reference[7619] = 'value_191230'
    assert tree.invariants(), "Invariants failed at step 78"

    # Operation 244: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 79"

    # Operation 245: get
    assert tree.invariants(), "Invariants failed at step 80"

    # Operation 246: get
    assert tree.invariants(), "Invariants failed at step 81"

    # Operation 247: get
    assert tree.invariants(), "Invariants failed at step 82"

    # Operation 248: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 83"

    # Operation 249: update
    tree[6317] = 'value_227627'
    reference[6317] = 'value_227627'
    assert tree.invariants(), "Invariants failed at step 84"

    # Operation 250: get
    assert tree.invariants(), "Invariants failed at step 85"

    # Operation 251: insert
    tree[3568] = 'value_801398'
    reference[3568] = 'value_801398'
    assert tree.invariants(), "Invariants failed at step 86"

    # Operation 252: delete
    del tree[5894]
    del reference[5894]
    assert tree.invariants(), "Invariants failed at step 87"

    # Operation 253: get
    assert tree.invariants(), "Invariants failed at step 88"

    # Operation 254: insert
    tree[478] = 'value_547825'
    reference[478] = 'value_547825'
    assert tree.invariants(), "Invariants failed at step 89"

    # Operation 255: get
    assert tree.invariants(), "Invariants failed at step 90"

    # Operation 256: update
    tree[7619] = 'value_686208'
    reference[7619] = 'value_686208'
    assert tree.invariants(), "Invariants failed at step 91"

    # Operation 257: compact
    tree.compact()
    assert tree.invariants(), "Invariants failed at step 92"

    # Operation 258: insert
    tree[6129] = 'value_54536'
    reference[6129] = 'value_54536'
    assert tree.invariants(), "Invariants failed at step 93"

    # Operation 259: insert
    tree[6254] = 'value_930055'
    reference[6254] = 'value_930055'
    assert tree.invariants(), "Invariants failed at step 94"

    # Operation 260: insert
    tree[6184] = 'value_682786'
    reference[6184] = 'value_682786'
    assert tree.invariants(), "Invariants failed at step 95"

    # Operation 261: insert
    tree[4695] = 'value_361363'
    reference[4695] = 'value_361363'
    assert tree.invariants(), "Invariants failed at step 96"

    # Operation 262: delete
    del tree[478]
    del reference[478]
    assert tree.invariants(), "Invariants failed at step 97"

    # Operation 263: batch_delete
    keys_to_delete = [5365, 9945, 6317, 7619, 7675, 1825, 1529, 7118]
    tree.delete_batch(keys_to_delete)
    for k in keys_to_delete:
        if k in reference: del reference[k]
    assert tree.invariants(), "Invariants failed at step 98"

    # Operation 264: update
    tree[4695] = 'value_900594'
    reference[4695] = 'value_900594'
    assert tree.invariants(), "Invariants failed at step 99"

    # Operation 265: delete
    del tree[4695]
    del reference[4695]
    assert tree.invariants(), "Invariants failed at step 100"

    # Verify final consistency
    assert len(tree) == len(reference), "Length mismatch"
    for key, value in reference.items():
        assert tree[key] == value, f"Value mismatch for {key}"
    print("Reproduction completed successfully")

if __name__ == "__main__":
    reproduce_failure()
