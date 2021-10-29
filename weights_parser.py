# weights csv to cand converter
import os
import copy

WEIGHTS_FILE = "weights_layer0.csv"
IMAGE_FILE = "image.csv"
ROWS_PER_KERNEL = 3
COLS_PER_KERNEL = 3
TOTAL_KERNEL_ROWS = 384

ARRAY_ROWS = 18  # real rows
ARRAY_COLS = 3


OUT_FILE = "out.txt"

# output searches and reference columns


def prepare_search_string(in_weights_file):
    out_string = ""
    kernel_orig = []
    kernel = []
    for row in range(ROWS_PER_KERNEL):
        kernel.append([])
    kernel_orig = copy.deepcopy(kernel)

    i = 0
    for line in in_weights_file:
        kernel[i] += line.replace(",", "").replace("\n", "").replace(" ", "")
        i = i+1
        if i == ROWS_PER_KERNEL:
            # print(kernel)
            i = 0

            # write reference column
            out_string += "wcc " + str(ARRAY_COLS) + " "
            for col in range(COLS_PER_KERNEL):
                for row_i, row in enumerate(kernel):
                    if row_i+col*ROWS_PER_KERNEL <= ARRAY_ROWS/2/2:
                        out_string += row[col]
                    else:
                        out_string += str(1-int(row[col]))
            out_string += "\n"

            # search
            out_string += "sh  a "
            for col in range(COLS_PER_KERNEL):
                for row in kernel:
                    out_string += row[col]
            out_string += "\n"
            kernel = copy.deepcopy(kernel_orig)

    return out_string


def prepare_image_arr(in_image_file):
    out_arr = []

    # padding
    image_string = in_image_file.read()
    image_string = "0"*28 + "\n" + image_string + "0"*28 + "\n"
    image_arr = image_string.split("\n")
    image_arr = image_arr[:-1]  # remove newline in the end
    for i, line in enumerate(image_arr):
        image_arr[i] = "0" + line + "0"
    image_string = "".join(image_arr)
    # print(image_string)
    # splits to pieces
    n = 3
    image_arr = [image_string[i:i+n]
                 for i in range(0, len(image_string), n)]
    # print(image_arr)
    # print(len(image_arr))
    for i in range(0, len(image_arr)-20, 1):
        out_arr.append("wcc " + str(i % 3) + " " +
                       image_arr[i] + image_arr[i+10] + image_arr[i+20])
    out_arr.append("wcc 1 000000000")
    out_arr.append("wcc 2 000000000")

    # print(out_arr)
    # print(len(out_arr))

    return out_arr


def main():
    print("Weights parser started!\n")

    in_weights_file = open(WEIGHTS_FILE, "r")
    in_image_file = open(IMAGE_FILE, "r")
    out_file = open(OUT_FILE, "w")
    out_file.write("18 4 3\n")

    search_string = prepare_search_string(in_weights_file)

    image_arr = prepare_image_arr(in_image_file)
    for i in range(0, (len(image_arr)-2)//2, 3):
        # fill in the image
        out_file.write(image_arr[i] + "\n")
        out_file.write(image_arr[i+1] + "\n")
        out_file.write(image_arr[i+2] + "\n")

        # do the search
        out_file.write(search_string)

        # switch 1
        out_file.write("sw 0\n")

        # do the search
        out_file.write(search_string)

        # switch 2
        out_file.write("sw 0\n")
        out_file.write("sw 1\n")

        # do the search
        out_file.write(search_string)

        # switch back to normal
        out_file.write("sw 1\n")

    in_weights_file.close()
    in_image_file.close()
    out_file.close()

    print("Weights parser ended!")


if __name__ == "__main__":
    main()
