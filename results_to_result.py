import csv

PARSED_RESULTS_FOLDER = "parsed_results"

PICTURE_NUMBER = 1
PARTS_COUNT = 3

WEIGHTS_COUNT = 128


def results_to_result():
    results = []
    for _ in range(WEIGHTS_COUNT):
        results.append([])

    with open("parsed.csv", "w", newline='') as csv_outfile:
        writer = csv.writer(csv_outfile, delimiter=",")
        for part_number in range(1, PARTS_COUNT+1):
            with open(PARSED_RESULTS_FOLDER+"/pic"+str(PICTURE_NUMBER)+"_part"+str(part_number)+"_parsed.csv", "r") as csv_infile:
                reader = csv.reader(csv_infile, delimiter=',')

                for i, csv_row in enumerate(reader):
                    weight_index = int(csv_row[0])

                    # writer.writerow(csv_row[1:])
                    results[weight_index] += csv_row[1:]
        writer.writerows(results)

    # print(results)
    print(len(results))
    print(len(results[0]))


if __name__ == "__main__":
    results_to_result()
