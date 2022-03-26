import csv
from os import read

RESULTS_FOLDER = "results"
PARSED_RESULTS_FOLDER = "parsed_results"
INPUT_FILE = "out.txt"
HOLD_TIME = 100  # usecs
KERNEL_COUNT = 128

ARRAY_ROWS = 18  # real rows
ARRAY_COLS = 4   # real columns

REF_COL_CSV = 2 * ARRAY_COLS - 1
JUNK_COL_CSV = 2 * ARRAY_COLS - 3

PICTURE_NUMBER = 1
PART_COUNT = 3


def parse_results(part_number):
    print("Started parsing results!")
    print("Parsing picture "+str(PICTURE_NUMBER) +
          " part "+str(part_number)+"/"+str(PART_COUNT))

    search_times = []

    with open(INPUT_FILE, 'r') as input_file:
        elapsed_time = 0
        for i, line in enumerate(input_file):
            if i == 0:
                continue

            args = line.split()
            if len(args) == 0:
                continue
            command = args[0]

            if command == "wcc":
                elapsed_time = elapsed_time + 2*HOLD_TIME
                continue
            if command == "sh":
                search_times.append(elapsed_time)
                elapsed_time = elapsed_time + HOLD_TIME
                continue

            print("Unknown command: " + command)
            exit()

    search_times = [(num + HOLD_TIME/2) / 1e6 for num in search_times]
    # print(search_times)
    # print(len(search_times))

    rows = []
    for i in range(KERNEL_COUNT):
        rows += [[i]]

    with open(RESULTS_FOLDER+"/pic"+str(PICTURE_NUMBER)+"_part"+str(part_number)+".csv", "r") as csv_infile:
        with open(PARSED_RESULTS_FOLDER+"/pic"+str(PICTURE_NUMBER)+"_part"+str(part_number)+"_parsed.csv", "w", newline='') as csv_outfile:
            reader = csv.reader(csv_infile, delimiter=',')
            writer = csv.writer(csv_outfile, delimiter=",")
            kernel_index = 0
            counter = 0
            search_times_index = 0
            for i, row in enumerate(reader):
                if i == 0:
                    continue

                # print(", ".join(row))
                # print(type(row[0]))
                # print(float(row[0]))
                # print(type(float(row[0])))

                if float(row[0]) >= search_times[search_times_index]:
                    # print("performing search at time: " + row[0], end=", ")
                    output_row = []
                    # output_row = [kernel_index]
                    ref = float(row[REF_COL_CSV])
                    # print("ref is ", ref, end=", ")
                    for col in range(1, JUNK_COL_CSV, 2):
                        curr = float(row[col])
                        # print("row[", col, "] is ", row[col], end=", ")
                        # print("bigger? ", curr > ref, end=", ")
                        output_row.append(int(curr > ref))
                    # print("")
                    # writer.writerow(output_row)
                    rows[kernel_index] += (output_row)
                    counter += 1

                    kernel_index += 1
                    search_times_index += 1
                    if search_times_index >= len(search_times):
                        # print("ERROR! Not enough searches in csv.")
                        # exit()
                        break

                    if kernel_index >= KERNEL_COUNT:
                        # print("Passed all kernels!")
                        kernel_index = 0
                        continue

                # if i > 10000:
                #     break

            writer.writerows(rows)
    print(counter)
    print("Finished parsing results!")


if __name__ == "__main__":
    for part_number in range(1, PART_COUNT+1, 1):
        parse_results(part_number)
