import csv
import numpy as np


def csv_to_nparr(parsed_csv, np_shape):
    results = np.empty(shape=np_shape)
    total_count = 0
    with open(parsed_csv, "r") as csv_infile:
        reader = csv.reader(csv_infile, delimiter=',')

        for i, csv_row in enumerate(reader):
            row_index = 0
            col_index = 0

            for csv_col_index in range(len(csv_row)):
                total_count += 1
                # print(str(i) + " " +
                #       str(row_index) + " " + str(col_index))
                results[i][row_index][col_index] = csv_row[csv_col_index]

                col_index = col_index+1
                if col_index >= np_shape[2]:
                    col_index = 0
                    row_index = row_index + 1

    # print(results)
    print(np.shape(results))
    print(total_count)
    print(total_count == np_shape[0]*np_shape[1]*np_shape[2])
    return results


if __name__ == "__main__":
    csv_to_nparr("parsed.csv", (128, 6, 6))
