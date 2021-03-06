import os
import math
import logging

HOLD_TIME = 100
SWITCH_TIME = HOLD_TIME/3
SWITCH_VOLTAGE = 1
# DECIMAL_COUNT = max(0, math.ceil(-math.log(min(HOLD_TIME, SWITCH_TIME), 10)))
DECIMAL_COUNT = 3
# FORMAT_STR = "{:."+str(DECIMAL_COUNT)+"f}"
OUT_DIR = "out"
INPUT_FILE = "out.txt"
# INPUT_FILE = "input18_32_3.txt"
# INPUT_FILE = "input18_4_3.txt"
# INPUT_FILE = "out_random.txt"

VW0 = -0.7
VW1 = 2
VWL = 1.5
VSL = 1.5


VOLTAGE_PRECISION = 3  # number of digits after decimal point for voltages
INTERPOLATION_POINTS = 2
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

print(
    f"Parsed array size: {row_count} rows, {col_count} columns, {banks_count} banks.")

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
                ml_sw.append(-SWITCH_VOLTAGE)
            else:
                ml_sw.append(SWITCH_VOLTAGE)
        else:
            if flip:
                ml_sw.append(-ml_sw[-1])
            else:
                ml_sw.append(ml_sw[-1])


def perform_read(rows, cols=[]):
    # print(f"Reading rows {rows}, columns {cols}")
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
            bl_sw.append(SWITCH_VOLTAGE)
        else:
            bl_sw.append(-SWITCH_VOLTAGE)
    for i, sl_sw in enumerate(SL_SW):
        if i in rows:
            sl_sw.append(SWITCH_VOLTAGE)
        else:
            sl_sw.append(-SWITCH_VOLTAGE)

    for i, wl in enumerate(WL):
        if i in rows:  # selected row
            wl.append(VWL)
        else:  # unselected row
            wl.append(0)

    for i, sl in enumerate(SL):
        if i in rows:  # selected row
            sl.append(VSL)
        else:  # unselected row
            sl.append(0)


def perform_row_write(row0, bits):
    # print(f"Writing bits {bits} to row {row0}")
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
            sl_sw.append(SWITCH_VOLTAGE)
        for bl_sw in BL_SW:
            bl_sw.append(SWITCH_VOLTAGE)

        append_ml_sw()

    # write zeros
    for i, bit in enumerate(bits):
        if bit == "0":
            BuL[i].append(0)
        else:
            BuL[i].append(2*VW0/3)

    for i, wl in enumerate(WL):
        if i == row0:  # selected row
            wl.append(VW0)
        else:  # unselected row
            wl.append(VW0/3)

    # write ones
    for i, bit in enumerate(bits):
        if bit == "1":
            BuL[i].append(-VW1/2)
        else:
            BuL[i].append(0)

    for i, wl in enumerate(WL):
        if i == row0:  # selected row
            wl.append(VW1/2)
        else:  # unselected row
            wl.append(0)


def perform_col_write(col0, bits):
    # print(f"Writing bits {bits} to col {col0}")
    if(len(bits) != row_count):
        print(
            f"Error: Number of rows is {row_count}, attempted to write {len(bits)} bits.")
        exit()
    if(col0 >= col_count):
        print(
            f"Error: Column index is out of bounds. Number of columns is {col_count}")
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
            sl_sw.append(SWITCH_VOLTAGE)
        for i, bl_sw in enumerate(BL_SW):
            if (i == col0):
                bl_sw.append(SWITCH_VOLTAGE)
            else:
                bl_sw.append(-SWITCH_VOLTAGE)  # close unneeded columns

        append_ml_sw()

    # write zeros
    for i, bul in enumerate(BuL):
        if i == col0:
            BuL[i].append(0)
        else:
            BuL[i].append(2*VW0/3)

    for i, bit in enumerate(bits):
        if bit == "0":
            WL[i].append(VW0)
        else:
            WL[i].append(VW0/3)

    # write ones
    for i, bul in enumerate(BuL):
        if i == col0:
            BuL[i].append(-VW1/2)
        else:
            BuL[i].append(0)

    for i, bit in enumerate(bits):
        if bit == "1":
            WL[i].append(VW1/2)
        else:
            WL[i].append(0)


def interpolate(t0, t1, v0, v1, point_count):
    result = []
    if v0 == v1:
        return [(t0, v0), (t1, v1)]

    # if (v0 <= 0 or v1 <= 0 or v0 >= 1 or v1 >= 1):
    #     return [(t0, v0), (t1, v1)]

    # print("\n")
    # print("(t0,v0) = ", end="")
    # print((str(t0), str(v0)))
    # print("(t1,v1) = ", end="")
    # print((str(t1), str(v1)))
    # exit()
    # return [(t0, v0), (t1, v1)]

    c = min(v0, v1) - 0.01
    v0 -= c
    v1 -= c

    a = abs(v1-v0)+0.1
    v0 /= a
    v1 /= a

    # print("c = ", str(c))
    # print("a = ", str(a))

    # print(v0)
    # print(math.log(v0/(1-v0)))
    # print(v1)
    # print(math.log(v1/(1-v1)))

    A = math.log(v0/(1-v0))/math.log(v1/(1-v1))
    m = (t0-A*t1)/(1-A)
    k = math.log(v0/(1-v0))/(t0-m)

    for i in range(point_count):
        t = t0+i*(t1-t0)/(point_count-1)
        v = 1/(1+math.exp(-k*(t-m)))
        # print((t, v))
        v *= a
        v += c
        result.append((t, v))

    # midpoint = ((t0+t1)/2, (v0+v1)/2)
    # return [(t0, v0), midpoint, (t1, v1)]
    # print(result)
    return result
    # return [(t0, v0), (t1, v1)]


# ======================

# inputs = [BL, BuL, WL, SL, BL_SW, SL_SW, ML_SW]
for input in inputs:
    for i in input:
        i.append(0)

for line in in_file:
    # print(f"parsing: {line}", end="")
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
        perform_row_write(row0, bits)

    elif command == "wcr":  # write cam row
        if(len(args) != 3):
            print("Error: Wrong amount of arguments.")
            exit()
        row0 = int(args[1])*2
        row1 = int(args[1])*2+1
        bits = list(args[2])
        bits_not = [str(1-int(bit)) for bit in bits]
        perform_row_write(row0, bits)
        perform_row_write(row1, bits_not)

    elif command == "wcc":  # write cam column
        if(len(args) != 3):
            print("Error: Wrong amount of arguments.")
            exit()
        col = int(args[1])
        bits_orig = list(args[2])
        bits = []
        for bit in bits_orig:
            bits.append(bit)
            bits.append(str(1-int(bit)))
        perform_col_write(col, bits)

    # READ
    elif command == "r":
        if(len(args) < 2):
            print("Error: Wrong amount of arguments.")
            exit()
        rows = args[1:]
        rows = [int(row) for row in rows]
        perform_read(rows)

    # READ ALL
    elif command == "ra":
        if(len(args) < 1 or len(args) > 1):
            print("Error: Wrong amount of arguments.")
            exit()
        # print(f"Reading all rows.")
        for row in range(row_count):
            perform_read([row])

    # CAM SEARCH
    elif command == "sh" or command == "sl":
        if(len(args) != 3):
            print("Error: Wrong amount of arguments.")
            exit()
        # print("Doing CAM search!")

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

    # BANK SWITCH
    elif command == "sw":
        if(len(args) != 2):
            print("Error: Wrong amount of arguments.")
            exit()
        bank = int(args[1])
        if bank + 1 >= banks_count:
            print("Error: Bank index too large.")
            exit()
        # print(f"Switching banks {bank} and {bank+1}!")
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
    # NOP
    elif command == "nop":
        for bl in BL:
            bl.append(0)
        for bul in BuL:
            bul.append(0)

        for bl_sw in BL_SW:
            bl_sw.append(-1)
        for sl_sw in SL_SW:
            sl_sw.append(-1)
        append_ml_sw()

        for wl in WL:
            wl.append("0")

        for sl in SL:
            sl.append("0")
        continue
    # COMMENT
    elif command[0] == "#":
        pass
    # ERROR
    else:
        print(f"Error: Unknown command: {command}")
        exit()
    # print("End of line\n")
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
print(f"Simulation length should be at least: {length*HOLD_TIME}u")
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

print("Writing output files... ", end="", flush=True)

for input_id, input in enumerate(inputs):
    for i, arr in enumerate(input):
        out_file = open(f"{OUT_DIR}/{input_names[input_id]}_{i}.txt", "w")
        # out_file.write("0u 0\n")
        # if(f"{input_names[input_id]}_{i}.txt" == "bul_0.txt"):
        #     print(arr)
        for j, v in enumerate(arr[1:]):
            time_0 = j*HOLD_TIME
            time_1 = j*HOLD_TIME+SWITCH_TIME

            points = interpolate(
                time_0, time_1, arr[j], arr[j+1], INTERPOLATION_POINTS)

            for point in points:
                # time_str = FORMAT_STR.format(point[0])
                time_str = round(point[0], DECIMAL_COUNT)
                v_str = str(round(point[1], VOLTAGE_PRECISION))
                out_file.write(f"{time_str}u {v_str}\n")

            # time_0_str = FORMAT_STR.format(time_0)
            # time_1_str = FORMAT_STR.format(time_1)

            # out_file.write(f"{time_0_str}u {arr[j-1]}\n")
            # out_file.write(f"{time_1_str}u {arr[j]}\n")
        out_file.close()

print(" Wrote files.")
print("Generator finished successfully!")
