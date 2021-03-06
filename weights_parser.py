# weights csv to cand converter
import copy

WEIGHTS_FILE = "weights_layer0_2.csv"
IMAGE_FILE = "image.csv"
ROWS_PER_KERNEL = 3
COLS_PER_KERNEL = 3
TOTAL_KERNEL_ROWS = 384

STRIDE_HOR = 5
STRIDE_VER = 5

ARRAY_ROWS = 18  # real rows
ARRAY_COLS = 3  # without reference

PART_COUNT = 9
# 1-based
PART_INDEX = 6

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
            # out_string += "nop\n"  # for simulation stability
            out_string += "wcc " + str(ARRAY_COLS) + " "
            for col in range(COLS_PER_KERNEL):
                for row_i, row in enumerate(kernel):
                    if row_i+col*ROWS_PER_KERNEL <= ARRAY_ROWS/2/2:
                        out_string += row[col]
                    else:
                        out_string += str(1-int(row[col]))
            out_string += "\n"
            # out_string += "nop\n"  # for simulation stability

            # write junk column
            out_string += "wcc " + str(ARRAY_COLS-1) + " "
            for _ in range(COLS_PER_KERNEL*ROWS_PER_KERNEL):
                # out_string += str(random.randint(0, 1))
                out_string += "0"
            out_string += "\n"
            out_string += "wcc " + str(ARRAY_COLS-1) + " "
            for _ in range(COLS_PER_KERNEL*ROWS_PER_KERNEL):
                # out_string += str(random.randint(0, 1))

                out_string += "1"
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
    n = 1
    image_arr = [image_string[i:i+n]
                 for i in range(0, len(image_string), n)]
    # print(image_arr)
    # print(len(image_arr))
    for i in range(0, len(image_arr)-62, STRIDE_HOR):
        if (i % 30) > 27:
            continue
        if (i // 30) % STRIDE_VER != 0:
            continue
        out_arr.append("wcc " + str(i % 2) + " " +
                       (image_arr[i]+image_arr[i+1]+image_arr[i+2]) +
                       (image_arr[i+30]+image_arr[i+31]+image_arr[i+32]) +
                       (image_arr[i+60]+image_arr[i+61]+image_arr[i+62]))
    # out_arr.append("wcc 0 000000000")
    # out_arr.append("wcc 1 000000000")

    # print(out_arr)
    # print(len(out_arr))

    return out_arr


def weights_parser():
    print("Weights parser started!\n")

    in_weights_file = open(WEIGHTS_FILE, "r")
    in_image_file = open(IMAGE_FILE, "r")
    out_file = open(OUT_FILE, "w")
    out_file.write("18 4 3\n")

    search_string = prepare_search_string(in_weights_file)

    image_arr = prepare_image_arr(in_image_file)

    if (len(image_arr) % PART_COUNT != 0):
        print(str(len(image_arr))+" is not divisable by " +
              str(PART_COUNT)+". Will exit now.")
        exit()

    print(len(image_arr))

    # for i in range(10):
    #     print((i*len(image_arr)//2)//PART_COUNT)

    wcc_count = 0

    print("Part " + str(PART_INDEX) + " of " + str(PART_COUNT))
    # for i in range((PART_INDEX-1)*(len(image_arr)-1)//PART_COUNT//2, PART_INDEX*(len(image_arr)-1)//PART_COUNT//2, 1):
    for i in range(((PART_INDEX-1)*len(image_arr))//PART_COUNT, (PART_INDEX*len(image_arr))//PART_COUNT, 2):
        # fill in the image
        out_file.write(image_arr[i] + "\n")
        out_file.write(image_arr[i+1] + "\n")
        # out_file.write(image_arr[i+2] + "\n")
        print(image_arr[i])
        print(image_arr[i+1])
        wcc_count += 2
        # do the search
        out_file.write(search_string)

    in_weights_file.close()
    in_image_file.close()
    out_file.close()

    print("Doing " + str(wcc_count) + " writes.")
    print("Weights parser ended!")


if __name__ == "__main__":
    weights_parser()
