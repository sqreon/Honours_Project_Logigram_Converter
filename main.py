# imports
import easyocr
import cv2
import PIL
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
from prettytable import PrettyTable


# function handles extraction and conversion of drawings
def combinedExtraction(current_drawing):
    print("")
    print("[Starting Line Detection]")
    iolist = [[], []]
    relationships = []
    input_list = []
    output_list = []

    # opens drawing image file and converts to grayscale
    img = cv2.imread(current_drawing)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # find edges in the drawing
    edges = cv2.Canny(gray, 150, 300)

    # houghman method finds lines in the drawing
    lines = cv2.HoughLinesP(edges, rho=1.0, theta=np.pi / 180, threshold=50, minLineLength=50
                            )
    # parameters for drawing overlay
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    line_color = [0, 255, 0]
    line_thickness = 1
    dot_color = [0, 255, 0]
    dot_size = 1

    # overlays detected lines on drawing
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(line_img, (x1, y1), (x2, y2), line_color, line_thickness)
            cv2.circle(line_img, (x1, y1), dot_size, dot_color, -1)
            cv2.circle(line_img, (x2, y2), dot_size, dot_color, -1)

    overlay = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)

    # writes overlayed image to file
    cv2.imwrite('houghlines.jpg', overlay)

    print("[Completed Line Detection]")
    print("[Starting Text Detection (this may take a while)]")

    # displays overlayed drawing
    img = cv2.imread('houghlines.jpg')

    # creates an english charset OCR reader
    reader = easyocr.Reader(['en'])

    # reads drawing into OCR reader
    output = reader.readtext(current_drawing)

    print("[Completed Text Detection]")
    print("[Printing Results]")

    # opens drawing ready to have extracted text highlighted on
    img = PIL.Image.open("houghlines.jpg")
    draw = ImageDraw.Draw(img)

    # lists all the extracted text with confidence values
    print("")
    print(output)
    print(lines)
    t = PrettyTable(['Text', 'Confidence'])

    for x in output:
        # t.add_row([x[1],  (str(round(float(x[2] * 100), 0)) + "%")])
        t.add_row([x[1], (str(round(int(x[2] * 100))) + "%")])

    print(t)
    print("")
    print(lines)
    print("[Visualizing Results]")

    # draws boxes around extracted text on drawing
    for x in output:
        p0, p1, p2, p3 = x[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=(255, 0, 0), width=1)

    print("[Results Visualized]")

    # displays drawing with the extracted text highlighted
    plt.imshow(img)
    plt.title(current_drawing)
    plt.show()

    # io assignment
    for x in output:

        # text boundary box coordinates
        (tl, tr, br, bl) = x[0]
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))

        # loop through all detected lines
        for line in lines:
            for x1, y1, x2, y2 in line:

                # looks for line indicating output
                if x1 <= tl[0] and tl[0] >= x2 >= (tl[0] - 20) and tl[1] <= y1 <= bl[1] and tl[1] <= y2 <= bl[1]:
                    # saves tag as output
                    if str(x[1]) not in iolist[1]:
                        iolist[1].append(str(x[1]))
                        output_list.append([str(x[1]), x1, y1])

                # looks for line indicating input
                elif tr[0] <= x1 <= (tr[0] + 20) and x2 >= tr[0] and tl[1] <= y1 <= bl[1] and tl[1] <= y2 <= bl[1]:
                    if str(x[1]) not in iolist[0]:
                        iolist[0].append(str(x[1]))
                        input_list.append([str(x[1]), x2, y2])

    # traces intersects one safety bar deep
    for input_line in input_list:

        # gets detected inputs tag and x/y coordinates
        (i_tag, i_x2, i_y2) = input_line
        output_tags = []

        # loops through all detected lines
        for line in lines:
            for s_x1, s_y1, s_x2, s_y2 in line:

                # looks for input line intersecting with safety bar
                if i_x2 != s_x2 and i_y2 != s_y2 and (s_x2 - 5) <= i_x2 <= (s_x2 + 5) and s_y1 >= i_y2 >= s_y2:

                    # loops through output lines
                    for output_line in output_list:

                        # gets detected outputs tag and x/y coordinates
                        (o_tag, o_x1, o_y1) = output_line

                        # checks for output line intersecting with safety bar
                        if (s_x2 + 5) >= o_x1 >= (s_x2 - 5) and s_y2 <= o_y1 <= s_y1:
                            # appends relationship to array
                            output_tags.append(o_tag)
                            relationships.append(["x", str(i_tag), str(o_tag)])

    # generates empty c&e matrix
    matrix = [[" " for col in range(len(iolist[1]))] for row in range(len(iolist[0]))]
    column_lbls = iolist[1]
    row_lbls = iolist[0]

    # populates c&e matrix with intersects
    for x in relationships:
        matrix[iolist[0].index(x[1])][iolist[1].index(x[2])] = str(x[0])

    fig, ax = plt.subplots()

    # hide axes
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    # generates c&e matrix plot
    ax.table = ax.table(
        cellText=matrix,
        rowLabels=row_lbls,
        colLabels=column_lbls,
        cellLoc='center',
        loc='center')

    plt.title("C&E Matrix")
    fig.tight_layout()
    plt.show()


# main menu function
def menu():
    # menu options printed
    print("")
    print("Logigram to Cause and Effect Converter")
    print("######################################")
    print("")
    print("1. Converter")
    print("2. Exit")

    # gets menu selection from user
    menu_input = input("Enter Selection: ")
    menu_input = str(menu_input)

    # handles users menu selection
    if menu_input == "1":
        combinedExtraction(getdrawing())
    elif menu_input == "2":
        quit()
    else:
        menu()

    menu()


# gets logigram path from user
def getdrawing():
    drawing_path = input("Enter drawing path: ")
    print("")
    return drawing_path


# main program
if __name__ == '__main__':
    menu()
