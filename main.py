import tkinter as tk
from tkinter import filedialog
import subprocess, os, platform
import cv2


def image_detection(pic, threshold_value, opening=True, dilation=True):
    global contained_area_ratio_percent
    ## Convert image into openCV format and make it a grayscale
    pic_gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)

    ## Filtering...
    # Apply thresholding to create a binary image
    ret, binary_img = cv2.threshold(pic_gray, threshold_value, 255, cv2.THRESH_BINARY_INV)

    # Apply morphological closing to fill small holes and gaps in the image
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)

    # Apply morphological opening to remove small objects and smooth the edges
    if opening == True:
        opened_img = cv2.morphologyEx(closed_img, cv2.MORPH_OPEN, kernel)
    else:
        opened_img = closed_img

    # Apply morphological dilation to expand the remaining objects and make the edges more distinct
    if dilation == True:
        dilated_img = cv2.dilate(opened_img, kernel, iterations=1)
    else:
        dilated_img = opened_img

    ## Contours...
    # Find the contours of the objects in the image
    contours, hierarchy = cv2.findContours(dilated_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    ##Draw...
    # Convert picture from black&white to RGB to plot color
    # Draw contours on image
    contour_pic = cv2.drawContours(pic.copy(), contours, -1, (0, 255, 0), 2)

    # Calculate the area of the detected contours
    contour_area = 0
    for contour in contours:
        contour_area += cv2.contourArea(contour)
    # Calculate the ratio of the area of contained contours to the overall area
    total_area = contour_pic.shape[0] * contour_pic.shape[1]  # Get the total area of the image
    contained_area_ratio = contour_area / total_area
    contained_area_ratio_percent = contained_area_ratio * 100

    # define text to be printed on picture
    text1 = "Porenanteil:"
    text2 = str(round(contained_area_ratio_percent, 3)) + " %"
    text3 = "KimmleEngineering - only for testing purposes"
    print("void area: " + str(round(contained_area_ratio_percent, 3)) + " %")

    # add print to picture
    font = cv2.FONT_HERSHEY_SIMPLEX#x   y-pos           scale5 color thickness10
    cv2.putText(contour_pic, text1, (10, 70), font, 2, (0, 0, 255), 4, cv2.LINE_AA)
    cv2.putText(contour_pic, text2, (10, 140), font, 2, (0, 0, 255), 4, cv2.LINE_AA)
    cv2.putText(contour_pic, text3, (10, 210), font, 2/2, (0, 0, 255), 4/2, cv2.LINE_AA)

    return contour_pic

## graphical user interface

class PictureImporter:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        self.label = tk.Label(self.frame, text="[von oben nach unten vorgehen]")
        self.label.pack()

        self.button_load = tk.Button(self.frame, text="Bild auswählen", command=self.load_pictures)
        self.button_load.pack()

        self.button_save = tk.Button(self.frame, text="Speicherort festlegen", command=self.save_pictures)
        self.button_save.pack()

        self.label = tk.Label(self.frame, text="manipuliere grau-Grenzwert:")
        self.label.pack()

        self.threshold_slider = tk.Scale(self.frame, from_=20, to=180, orient="horizontal", length=160,
                                         command=self.update_threshold)
        self.threshold_slider.set(100)
        self.threshold_slider.pack()

        self.opening_var = tk.BooleanVar()
        self.check_box_opening = tk.Checkbutton(self.frame, text="kleine Poren filtern (kleinereFehlerrate)",
                                                variable=self.opening_var)
        self.check_box_opening.pack()

        self.dilation_var = tk.BooleanVar()
        self.check_box_dilation = tk.Checkbutton(self.frame, text="Porenkanten glätten (höhereFehlerrate)",
                                                 variable=self.dilation_var)
        self.check_box_dilation.pack()

        self.button_process = tk.Button(self.frame, text="Berechnen...", command=self.process)
        self.button_process.pack()

    def load_pictures(self):
        global open_file_path
        open_file_path = filedialog.askopenfilename()

    def save_pictures(self):
        global safe_file_path
        if open_file_path:
            safe_file_path = filedialog.askdirectory()

    def update_threshold(self, value):
        global threshold
        # Convert slider value to integer
        threshold = int(value)

    def process(self):
        picture = cv2.imread(open_file_path)
        picture = image_detection(picture, threshold, opening=self.opening_var.get(), dilation=self.dilation_var.get())
        print("pics detected")
        voiding = round(contained_area_ratio_percent, 2)

        # Extract file name and safe image:
        directories = open_file_path.split('/')
        filename = directories[len(directories) - 1]
        filename = filename.split('.')[0]
        filepathname = safe_file_path + '/' + filename + '[' + str(voiding) + ']' + '.JPG'
        print(filepathname)
        cv2.imwrite(filepathname, picture)
        # Auto opening image:
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', filepathname))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(filepathname)
        else:  # linux variants
            subprocess.call(('xdg-open', filepathname))


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Porenerkennung')
    app = PictureImporter(root)
    root.mainloop()
