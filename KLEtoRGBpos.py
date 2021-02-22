#!/usr/bin/env python3

#use python3.8.4
import sys, re, json, math
import matplotlib.pyplot as plt

X_COORD_OFFSET = 0.0
Y_COORD_OFFSET = 0.0

class Key:
    """All required information about a single keyboard key"""
    x_unit = 0.0
    y_unit = 0.0
    x_coord = 0.0
    y_coord = 0.0
    width = 0.0
    height = 0.0
    rot = 0
    num = 0
    legend = "<N/A>"


def natural_sort_key_for_list_of_lists(sublist):
    return [int(element) if element.isdigit() else element
            for element in re.split("([0-9]+)",sublist[0])]

def main(args):
    # handle error checking
    if len(args) != 5:
        print("./KLEtoRGBpos <file.json> <num_per_line> <index_start: 0 or 1> <index_end:32/36/48/64/117>")
        exit()
    
    print("input = " + args[1])
    print("num = " + args[2])
    num_per_line = int(args[2])
    index_start = int(args[3])
    index_end = int(args[4])

    # list of RGB
    contents_list = []

    # keys list of json
    keys = []

    # open KLE json
    with open(args[1], "r", encoding="latin-1") as read_file:
        kle_json = json.load(read_file)
            # First create a list of switches, each with its own X,Y coordinate
        current_y = -0.5
        key_num = 0
        for row in kle_json:
            current_x = -0.5
            if isinstance(row, list):
                # Default keysize is 1x1
                key_width = 1.0
                key_height = 1.0
                # Extract all keys in a row
                for item in row:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key == "x":
                                current_x += value
                            elif key == "y":
                                current_y += value
                            elif key == "w":
                                key_width = value
                            elif key == "h":
                                key_height = value
                    elif isinstance(item, str):
                        new_key = Key()
                        new_key.num = key_num
                        new_key.x_unit = current_x + key_width / 2
                        new_key.y_unit = current_y + key_height / 2
                        new_key.legend = item
                        new_key.width = key_width
                        new_key.height = key_height

                        keys.append(new_key)

                        # if key_num == 45:
                        #     print(new_key.__dict__)

                        current_x += key_width
                        key_num += 1.0
                        key_width = 1.0
                        key_height = 1.0
                    else:
                        print("Found unexpected JSON element (", item, "). Exiting")
                        exit()
                current_y += 1.0
                current_x = 0.0
            else:
                pass

        for keysw in keys:
            keysw.x_coord = float("{:.8f}".format(keysw.x_unit * 19.05 + X_COORD_OFFSET))
            keysw.y_coord = float("{:.8f}".format(keysw.y_unit * 19.05 + X_COORD_OFFSET))
            # print("{:.8f} {:.8f}".format(keysw.x_coord, keysw.y_coord))

    print("keys =", len(keys))
    print(keys[0].__dict__)

    # move keys into contents list
    #  0       1         2        3       4      5        6       7       8        9        10
    # name, x_coord, y_coord, mod x,   mod y, xcoordm, ycoordm, atan2, distance, angle, dist_final
    for keysw in keys:
        item = []
        item.append(keysw.legend)
        item.append(keysw.x_coord)
        item.append(keysw.y_coord)
        #check for duplicates
        # if any(item[0] in sublist for sublist in contents_list):
        #     print("ERROR: FOUND EXISTS TWICE")
        #     print(item[0])
        #     exit()
        contents_list.append(item)
        # print(keysw.legend ,keysw.x_unit,  keysw.y_unit)

    # find min/max of x and y
    min_x = min(contents_list, key=lambda x: x[1])[1]
    min_y = min(contents_list, key=lambda x: x[2])[2]

    # math to normalise to top left 0,0
    for keysw in contents_list:
        keysw[1] -= min_x
        keysw[2] -= min_y

    max_x = max(contents_list, key=lambda x: x[1])[1] - min_x
    max_y = max(contents_list, key=lambda x: x[2])[2] - min_y

    # print('min max', min_x, min_y, max_x, max_y)

    for keysw in contents_list:
        #3
        keysw.append(int(round(keysw[1]*224/max_x)))
        #4
        keysw.append(int(round(keysw[2]*64/max_y)))

    # center keyboard over middle
    mid_x = max_x/2
    mid_y = max_y/2

    # print(mid_x, mid_y)

    # print('min', min_x, min_y)
    # print('mid', mid_x, mid_y)
    # print('max', max_x, max_y)

    for keysw in contents_list:
        #5
        keysw.append(round((keysw[1]-mid_x)/mid_x,10))
        #6
        keysw.append(round((keysw[2]-mid_y)/mid_y,10))
        #7
        atan2_angle = (math.atan2(keysw[5],keysw[6]))
        if (atan2_angle < 0):
            atan2_angle += math.pi * 2
        atan2_angle /= 2 * math.pi
        keysw.append(atan2_angle)
        #8
        keysw.append(math.sqrt(keysw[5]**2 + keysw[6]**2))
        #9
        keysw.append(round(keysw[7]*256))
        #10
        dist = round(keysw[8]*256)
        if dist > 255:
            dist = 255
        keysw.append(dist)
        #print(keysw)
    
    # sort normally A1,A2...A30 etc.
    contents_list.sort(key=natural_sort_key_for_list_of_lists)

    # list for unused so we can generate which ones to disable
    list_unused = []

    # list of indexes/letter starts. e.g. [A,B] or [A,B,C,D,E,F]
    list_of_letters = []
    for x in contents_list:
        letter = ''.join(i for i in x[0] if not i.isdigit())
        if letter not in list_of_letters:
            list_of_letters.append(letter)

    print(list_of_letters)

    ### THIS PRINTS THE XY COORDS
    print("XY COORDS PRINTING")

    # counter because row sucks and wont let us start at our index start
    count = index_start
    # row counter
    row_counter = 0
    # prev index letter
    prev_ID_letter = ''.join(i for i in contents_list[0][0] if not i.isdigit())
    
    # test = contents_list[31]
    # print('legend:', test[0])
    # print('x_coord:', test[1])
    # print('y_coord:', test[2])
    # print('mod x:', test[3])
    # print('mod y:', test[4])
    # print('xcoordm:', test[5])
    # print('ycoordm:', test[6])
    # print('atan2:', test[7])
    # print('distance:', test[8])
    # print('angle:', test[9])
    # print('dist_final:', test[10])
    
    #  0       1         2        3       4      5        6       7       8        9        10
    # name, x_coord, y_coord, mod x,   mod y, xcoordm, ycoordm, atan2, distance, angle, dist_final
    # print(contents_list[0][0])
    for row in contents_list:
        # print(row[0])
        # print(count)
        ID = row[0]
        ID_letter = ''.join(i for i in ID if not i.isdigit())
        ID_number = int(''.join(i for i in ID if i.isdigit()))

        # print(ID, ID_letter, ID_number, prev_ID_letter)

        # check if we moved to another bank e.g. A->B
        if ID_letter != prev_ID_letter:
            print('moved to another bank')
            # if we're at the end, but are missing from count to index_end
            # then fill them in as blank
            # e.g. index_end = 64, current ID = A60, next ID = B02
            # fill in A61 - A64
            if count != index_end + 1:
                while count <= index_end:
                    list_unused.append(prev_ID_letter + str(count))
                    print("{255,255}, ", end ="")
                    row_counter += 1
                    if row_counter == num_per_line:
                        print("")
                        row_counter = 0
                    count += 1
            count = index_start
            prev_ID_letter = ID_letter

        if count != ID_number:
            # check for missing gaps of LEDs
            # e.g. A1 -> A5, missing A2, A3, A4
            # this will fill in A2 - A4
            while count < ID_number:
                list_unused.append(ID_letter + str(count))
                print("{255,255}, ", end ="")
                row_counter += 1
                if row_counter == num_per_line:
                    print("")
                    row_counter = 0
                count += 1

        # print the data
        string = "{"
        string += "{}".format(row[3])
        string += " "*(3-len(str(row[3])))
        string += ","
        string += " "*(3-len(str(row[4])))
        string += "{}".format(row[4])
        string += "}"
        print(string, end = ", ")
        # new line at <num_per_line>
        row_counter += 1
        if row_counter == num_per_line:
            print("")
            row_counter = 0
        count += 1
    
    # when we end the loop, make sure the last bank also gets checked
    # since we cannot go back to the start of the loop
    while count <= index_end:
        list_unused.append(prev_ID_letter + str(count))
        print("{255,255}, ", end ="")
        row_counter += 1
        if row_counter == num_per_line:
            print("")
            row_counter = 0
        count += 1


    ### THIS PRINTS THE AD COORDS
    print("")
    print("ANGLE DIST COORDS PRINTING")

    # counter because row sucks and wont let us start at our index start
    count = index_start
    # row counter
    row_counter = 0
    # prev index letter
    prev_ID_letter = ''.join(i for i in contents_list[0][0] if not i.isdigit())

    for row in contents_list:
        #print(count)
        ID = row[0]
        ID_letter = ''.join(i for i in ID if not i.isdigit())
        ID_number = int(''.join(i for i in ID if i.isdigit()))

        # check if we moved to another bank e.g. A->B
        if ID_letter != prev_ID_letter:
            # if we're at the end, but are missing from count to index_end
            # then fill them in as blank
            # e.g. index_end = 64, current ID = A60, next ID = B02
            # fill in A61 - A64
            if count != index_end + 1:
                while count <= index_end:
                    print("{255,255}, ", end ="")
                    row_counter += 1
                    if row_counter == num_per_line:
                        print("")
                        row_counter = 0
                    count += 1
            count = index_start
            prev_ID_letter = ID_letter

        if count != ID_number:
            # check for missing gaps of LEDs
            # e.g. A1 -> A5, missing A2, A3, A4
            # this will fill in A2 - A4
            while count < ID_number:
                print("{255,255}, ", end ="")
                row_counter += 1
                if row_counter == num_per_line:
                    print("")
                    row_counter = 0
                count += 1

        # print the data
        string = "{"
        string += "{}".format(row[9])
        string += " "*(3-len(str(row[9])))
        string += ","
        string += " "*(3-len(str(row[10])))
        string += "{}".format(row[10])
        string += "}"
        print(string, end = ", ")
        # new line at <num_per_line>
        row_counter += 1
        if row_counter == num_per_line:
            print("")
            row_counter = 0
        count += 1
    
    # when we end the loop, make sure the last bank also gets checked
    # since we cannot go back to the start of the loop
    while count <= index_end:
        print("{255,255}, ", end ="")
        row_counter += 1
        if row_counter == num_per_line:
            print("")
            row_counter = 0
        count += 1


    # PRINT UNUSED
    print("")
    print("UNUSED:")
    bank = 0
    multiplier = index_end
    if index_start == 0:
        multiplier = index_end + 1

    print(len(list_unused))
    if len(list_unused) == 0:
        print("none unused... exiting")
    else:
        prev_ID_letter = ''.join(i for i in list_unused[0] if not i.isdigit())
        for ID in list_unused:
            ID_letter = ''.join(i for i in ID if not i.isdigit())
            ID_number = int(''.join(i for i in ID if i.isdigit()))
            bank = list_of_letters.index(ID_letter)
            string = "( index == {}+".format(str(multiplier * bank))
            string += "{}".format(''.join(i for i in ID if i.isdigit()))
            # wilba's code is index 0 duh
            if index_start == 1:
                string += "-1"
            string +=  ") || //"
            string += ID
            print(string)
        print(list_unused)

    ### plot on a graph
    x = []
    y = []

    for keysw in contents_list:
        x.append(keysw[3])
        y.append(keysw[4]*-1)
    plt.plot(x,y,'ro')
    plt.show()

if __name__ == "__main__":
    main(sys.argv)