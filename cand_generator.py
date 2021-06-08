import os

HOLD_TIME = 1
SWITCH_TIME = HOLD_TIME/100
OUT_DIR = "out"
INPUT_FILE = "input16_5.txt"
# ======================


print("Generator started!\n")
current_time = 0
in_file = open(INPUT_FILE, "r")

# Set size
params = in_file.readline().split()
if(len(params) != 3):
    print(f"Error: 3 parameters should be given, {len(params)} given.")
    exit()
row_count = int(params[0])
col_count = int(params[1])
banks_count = int(params[2])

print(f"Parsed array size: {row_count} rows, {col_count} columns.")

BL = []
BuL = []
WL = []
SL = []
BL_SW = []
SL_SW = []
ML_SW = []
for _ in range(col_count):
    BL.append([])
    BuL.append([])
    BL_SW.append([])
for _ in range(row_count):
    WL.append([])
    SL.append([])
    SL_SW.append([])

for _ in range(banks_count-1):
    ML_SW.append([])


inputs = [BL, BuL, WL, SL, BL_SW, SL_SW, ML_SW]
input_names = ["bl", "bul", "wl", "sl", "bl_sw", "sl_sw", "ml_sw"]
# ======================


def append_ml_sw(flip=False):
    for ml_sw in ML_SW:
        if(len(ml_sw) == 0):
            if flip:
                ml_sw.append(-1)
            else:
                ml_sw.append(1)
        else:
            if flip:
                ml_sw.append(-ml_sw[-1])
            else:
                ml_sw.append(ml_sw[-1])


def perform_read(rows, cols=[]):
    print(f"Reading rows {rows}, columns {cols}")
    for row in rows:
        if(row >= row_count):
            print(
                f"Error: Row index is out of bounds. Number of rows is {row_count}")
            exit()

    # actual read
    for bl in BL:
        bl.append(0)
    for bul in BuL:
        bul.append(0)
    append_ml_sw()

    for i, bl_sw in enumerate(BL_SW):
        if i in cols or len(cols) == 0:
            bl_sw.append(1)
        else:
            bl_sw.append(-1)
    for i, sl_sw in enumerate(SL_SW):
        if i in rows:
            sl_sw.append(1)
        else:
            sl_sw.append(-1)

    for i, wl in enumerate(WL):
        if i in rows:  # selected row
            wl.append("VWL")
        else:  # unselected row
            wl.append("0")

    for i, sl in enumerate(SL):
        if i in rows:  # selected row
            sl.append("VSL")
        else:  # unselected row
            sl.append("0")


def perform_write(row0, bits):
    print(f"Writing bits {bits} to row {row0}")
    if(len(bits) != col_count):
        print(
            f"Error: Number of columns is {col_count}, attempted to write {len(bits)} bits.")
        exit()
    if(row0 >= row_count):
        print(
            f"Error: Row index is out of bounds. Number of rows is {row_count}")
        exit()

    # the actual write

    for _ in range(2):  # we write zeros in one cycle, and ones in another cycle
        # setup rows
        for sl in SL:
            sl.append(0)

        # setup BL
        for bl in BL:
            bl.append(0)

        # setup switches
        for sl_sw in SL_SW:
            sl_sw.append(1)
        for bl_sw in BL_SW:
            bl_sw.append(1)

        append_ml_sw()

    # write zeros
    for i, bit in enumerate(bits):
        if bit == "0":
            BuL[i].append(0)
        else:
            BuL[i].append("2*VW0/3")

    for i, wl in enumerate(WL):
        if i == row0:  # selected row
            wl.append("VW0")
        else:  # unselected row
            wl.append("VW0/3")

    # write ones
    for i, bit in enumerate(bits):
        if bit == "1":
            BuL[i].append("-VW1/2")
        else:
            BuL[i].append(0)

    for i, wl in enumerate(WL):
        if i == row0:  # selected row
            wl.append("VW1/2")
        else:  # unselected row
            wl.append(0)


# ======================
for line in in_file:
    print(f"parsing: {line}", end="")
    args = line.split()
    if len(args) == 0:
        continue
    command = args[0]

    # WRITE
    if command == "w":
        if(len(args) != 3):
            print("Error: Wrong amount of arguments.")
            exit()
        row0 = int(args[1])
        bits = list(args[2])
        perform_write(row0, bits)

    elif command == "wc":
        if(len(args) != 3):
            print("Error: Wrong amount of arguments.")
            exit()
        row0 = int(args[1])*2
        row1 = int(args[1])*2+1
        bits = list(args[2])
        bits_not = [str(1-int(bit)) for bit in bits]
        perform_write(row0, bits)
        perform_write(row1, bits_not)

    # READ
    elif command == "r":
        if(len(args) < 2):
            print("Error: Wrong amount of arguments.")
            exit()
        rows = args[1:]
        rows = [int(row) for row in rows]
        print(f"Reading rows {rows}")
        perform_read(rows)

    # READ
    elif command == "ra":
        if(len(args) < 1 or len(args) > 1):
            print("Error: Wrong amount of arguments.")
            exit()
        print(f"Reading all rows.")
        for row in range(row_count):
            perform_read([row])

    # CAM SEARCH
    elif command == "sh" or command == "sl":
        if(len(args) != 3):
            print("Error: Wrong amount of arguments.")
            exit()
        print("Doing CAM search!")

        cols = args[1]
        if cols[0] == "a":
            cols = []
        cols = list(cols)
        cols = [int(col) for col in cols]

        bits = list(args[2])
        bits = [int(bit) for bit in bits]
        if len(bits) != row_count/2:
            print(
                f"Error: Wrong amount of bits to search. {int(row_count/2)} required, {len(bits)} given.")
            exit
        rows = []
        if command == "sh":
            for i, bit in enumerate(bits):
                if bit == 1:
                    rows.append(2*i)
                else:
                    rows.append(2*i+1)
        else:  # sl
            for i, bit in enumerate(bits):
                if bit == 0:
                    rows.append(2*i)
                else:
                    rows.append(2*i+1)
        perform_read(rows, cols)

    elif command == "sw":
        if(len(args) != 2):
            print("Error: Wrong amount of arguments.")
            exit()
        bank = int(args[1])
        if bank + 1 >= banks_count:
            print("Error: Bank index too large.")
            exit()
        print(f"Switching banks {bank} and {bank+1}!")
        for i, ml_sw in enumerate(ML_SW):
            if(i == bank):
                ML_SW[i].append(-(ML_SW[i][-1]))
            else:
                ML_SW[i].append(ML_SW[i][-1])
        # fill in all inputs with zeros
        for bl in BL:
            bl.append(0)
        for bul in BuL:
            bul.append(0)

        for bl_sw in BL_SW:
            bl_sw.append(-1)
        for sl_sw in SL_SW:
            sl_sw.append(-1)

        for wl in WL:
            wl.append("0")

        for sl in SL:
            sl.append("0")

    # COMMENT
    elif command[0] == "#":
        continue
    # ERROR
    else:
        print(f"Error: Unknown command: {command}")
        exit()
    print("End of line\n")
in_file.close()


print("Parsing finished.")
# print("Parsing finished. Printing results:")
# print("BL : ", BL)
# print("BuL: ", BuL)
# print("WL : ", WL)
# print("SL : ", SL)

# sanity check
length = len(WL[0])
for input in inputs:
    for arr in input:
        if (len(arr) != length):
            print("Error: Resulting arrays are not of the same length.")
            exit()

print(f"Sanity check passed: arrays are of the same length: {length}.")
print(f"Simulation length should be at least: {length*HOLD_TIME}us.")
print(f"Hold Time is: {HOLD_TIME}us.")
print(f"Switch Time is: {SWITCH_TIME}us.")

# print(inputs)

# create output directory
os.system(f"rm -rf {OUT_DIR}")
try:
    os.mkdir(OUT_DIR)
    print("Created output directory.")
except FileExistsError:
    print("Notice: output directory already exists.")

for input_id, input in enumerate(inputs):
    for i, arr in enumerate(input):
        out_file = open(f"{OUT_DIR}/{input_names[input_id]}_{i}.txt", "w")
        out_file.write("0u 0\n")
        for i, v in enumerate(arr):
            out_file.write(f"{i*HOLD_TIME+SWITCH_TIME}u {v}\n")
            out_file.write(f"{(i+1)*HOLD_TIME}u {v}\n")
        out_file.close()

print("Wrote files.")
print("Generator finished successfully!")
