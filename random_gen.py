import random

ARRAY_ROWS = 18  # real rows
ARRAY_COLS = 4
BANKS = 3

OUT_FILE = "out_random.txt"

ITERATIONS_COUNT = 300

print("Generating random shit...")

out_file = open(OUT_FILE, "w")
out_file.write(str(ARRAY_ROWS) + " " +
               str(ARRAY_COLS) + " " + str(BANKS) + "\n")

for i in range(ITERATIONS_COUNT):
    out_file.write("wcr ")
    out_file.write(str(random.randrange(0, ARRAY_ROWS//2, 1)))
    out_file.write(" ")
    for _ in range(ARRAY_COLS):
        out_file.write(str(random.randint(0, 1)))
    out_file.write("\n")

    # out_file.write("wcc ")
    # out_file.write(str(random.randrange(0, ARRAY_COLS, 1)))
    # out_file.write(" ")
    # for _ in range(ARRAY_ROWS//2):
    #     out_file.write(str(random.randint(0, 1)))
    # out_file.write("\n")

    rand = random.randint(1, 5)
    if i > 10:
        if rand == 1:
            out_file.write("sh a ")
            for _ in range(ARRAY_ROWS//2):
                out_file.write(str(random.randrange(0, 2, 1)))
            out_file.write("\n")
        if rand == 2:
            out_file.write("ra\n")

out_file.close()

print("Random shit generated!")
