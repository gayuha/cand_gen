import random

ARRAY_ROWS = 18  # real rows
ARRAY_COLS = 4
BANKS = 0

OUT_FILE = "out_random.txt"

ITERATIONS_COUNT = 100
GEN_ROWS = False
GEN_COLS = True
GEN_SEARCH = True
GEN_READALL = False
RANDOMIZE_ORDER = False
RA_ON_END = True

print("Generating random shit...")

out_file = open(OUT_FILE, "w")
out_file.write(str(ARRAY_ROWS) + " " +
               str(ARRAY_COLS) + " " + str(BANKS) + "\n")

for i in range(ITERATIONS_COUNT):
    if GEN_ROWS:
        out_file.write("wcr ")
        if RANDOMIZE_ORDER:
            out_file.write(str(random.randrange(0, ARRAY_ROWS//2, 1)))
        else:
            out_file.write(str(int(i % (ARRAY_ROWS/2))))
        out_file.write(" ")
        for _ in range(ARRAY_COLS):
            out_file.write(str(random.randint(0, 1)))
        out_file.write("\n")

    if GEN_COLS:
        out_file.write("wcc ")
        if RANDOMIZE_ORDER:
            out_file.write(str(random.randrange(0, ARRAY_COLS, 1)))
        else:
            out_file.write(str(i % ARRAY_COLS))
        out_file.write(" ")
        for _ in range(ARRAY_ROWS//2):
            out_file.write(str(random.randint(0, 1)))
        out_file.write("\n")

    rand = random.randint(1, 5)
    if i > 10:
        if rand == 1 and GEN_SEARCH:
            out_file.write("sh a ")
            for _ in range(ARRAY_ROWS//2):
                out_file.write(str(random.randrange(0, 2, 1)))
            out_file.write("\n")
        if rand == 2 and GEN_READALL:
            out_file.write("ra\n")

if RA_ON_END:
    out_file.write("ra\n")

out_file.close()

print("Random shit generated!")
