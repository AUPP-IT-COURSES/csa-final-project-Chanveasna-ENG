from tkinter import Tk, Frame, Scale, Button, Label, IntVar, DoubleVar, Text, LabelFrame
from tkinter import filedialog as fd
import PIL.ImageTk
import PIL.Image
import PIL.ImageTransform
import image_processing as imp
import pytesseract_calling as pytess


class DocScanner:
    def __init__(self, root) -> None:
        self.image = None
        self.bw_image = None
        self.has_opened = False
        self.buckets = IntVar()
        self.smoothness_radius = DoubleVar(value=0.)

        # init the crop point
        self.point1 = None
        self.point2 = None
        self.point3 = None
        self.point4 = None

        self.option_frame = LabelFrame(root)
        self.text_frame = LabelFrame(root)

        self.option_frame.pack(side="left", padx=10)
        self.text_frame.pack(side="right")


        # option frame, showing image
        # image
        self.img_frame = LabelFrame(self.option_frame, 
                        width=850, 
                        height=850)
        self.panel = Label(self.img_frame, 
                    bg="white", 
                    width=850, 
                    height=850)
        self.img_frame.pack()
        self.panel.place(x=0, y=0, relwidth=1, relheight=1)

        # button 
        self.button_frame = Frame(self.option_frame)
        self.button_main = LabelFrame(self.button_frame)
        self.button_crop = LabelFrame(self.button_frame)

        self.button_frame.pack(side="left", padx=5, pady=3)
        self.button_main.pack(side="left")
        self.button_crop.pack(side="left")

        # open, update, convert
        self.button_columnA = Frame(self.button_main)
        self.open_button = Button(self.button_columnA, 
                            text="Open Image",
                            font=("Arial", 12), 
                            width=15,
                            command=lambda: self.open_img())
        self.update_image_button = Button(self.button_columnA,
                                    text="Update Image",
                                    font=("Arial", 12),
                                    width=15,
                                    command=lambda: self.update_image())
        self.convert_button = Button(self.button_columnA, 
                                text="Convert to Text", 
                                font=("Arial", 12),
                                width=15,
                                command=lambda: self.convert())
        self.button_columnA.pack(side="left")
        self.open_button.pack(anchor="center", pady=5)
        self.update_image_button.pack(anchor="center", pady=5)
        self.convert_button.pack(anchor="center", pady=5)


        # scale
        self.scale_frame = Frame(self.button_main)
        self.scale_frame.pack(side="left", padx=10, pady=10)

        # contrast
        self.contrast_frame = Frame(self.scale_frame)
        self.contrast_scale = Scale(self.contrast_frame, 
                            label="Contrast", 
                            variable=self.buckets, 
                            orient="horizontal",
                            length=255, 
                            from_=1, 
                            to=255, )
                            #    command=lambda value: update_image(self.buckets.get(), self.smoothness_radius.get()))
        self.contrast_frame.pack()
        self.contrast_scale.set(128)
        self.contrast_scale.pack(side="left")

        #smothness
        self.smooth_frame = Frame(self.scale_frame)
        self.smooth_scale = Scale(self.smooth_frame, 
                            label="Smoothness", 
                            variable=self.smoothness_radius, 
                            resolution=0.05, 
                            orient="horizontal", 
                            length=255, 
                            from_=0.0, 
                            to=10.0, )
                            #  command=lambda value: update_image(self.buckets.get(), self.smoothness_radius.get()))
        self.smooth_scale.set(0)
        self.smooth_frame.pack()
        self.smooth_scale.pack(side="left")

        # crop
        self.button_columnB = Frame(self.button_crop)
        self.crop_button = Button(self.button_columnB, 
                            text="Crop Tool", 
                            font=("Arial", 12),
                            width=15,
                            command=lambda: self.crop_image())
        self.transform_button = Button(self.button_columnB,
                                text="Transform Image",
                                font=("Arial", 12),
                                width=15,
                                command=lambda: self.transform_image())
        self.undo_crop_button = Button(self.button_columnB,
                                text="Undo Crop",
                                font=("Arial", 12),
                                width=15,
                                command=lambda: self.undo_crop())

        self.button_columnB.pack(side="left", padx=5, pady=5)
        self.crop_button.pack(anchor="center", pady=6)
        self.transform_button.pack(anchor="center", pady=5)
        self.undo_crop_button.pack(anchor="center", pady=5)

        # crop point label
        self.point_columnA = Frame(self.button_crop, width=100)
        self.point_columnB = Frame(self.button_crop, width=100)

        self.point1_frame = Frame(self.point_columnA)
        self.point2_frame = Frame(self.point_columnA)
        self.point3_frame = Frame(self.point_columnB)
        self.point4_frame = Frame(self.point_columnB)

        self.point_columnA.pack(side="left", padx=10, pady=5)
        self.point_columnB.pack(side="left", padx=10, pady=5)

        self.point1_frame.pack(padx=5, pady=15)
        self.point2_frame.pack(padx=5, pady=15)
        self.point3_frame.pack(padx=5, pady=15)
        self.point4_frame.pack(padx=5, pady=15)

        self.point1_label = Label(self.point1_frame, text="P1:", font=("Arial", 12))
        self.point1_coordiante = Label(self.point1_frame, text="0, 0", font=("Arial", 12))

        self.point2_label = Label(self.point2_frame, text="P2:", font=("Arial", 12))
        self.point2_coordiante = Label(self.point2_frame, text="0, 850", font=("Arial", 12))

        self.point3_label = Label(self.point3_frame, text="P3:", font=("Arial", 12))
        self.point3_coordiante = Label(self.point3_frame, text="850, 0", font=("Arial", 12))

        self.point4_label = Label(self.point4_frame, text="P4:", font=("Arial", 12))
        self.point4_coordiante = Label(self.point4_frame, text="850, 850", font=("Arial", 12))

        self.point1_label.pack(side="left")
        self.point1_coordiante.pack(side="left")

        self.point2_label.pack(side="left")
        self.point2_coordiante.pack(side="left")

        self.point3_label.pack(side="left", anchor="w")
        self.point3_coordiante.pack(side="left", anchor="w")

        self.point4_label.pack(side="left", anchor="w")
        self.point4_coordiante.pack(side="left", anchor="w")

        # text field
        self.text_field = Text(self.text_frame, width=120, height=62)
        self.text_field.pack(anchor="center", padx=10)

    def open_img(self):
        opened_image = fd.askopenfilename()
        if opened_image:
            self.has_opened = True
            self.image = PIL.Image.open(opened_image)
            self.update_image()
    
    def update_image(self):
        if self.has_opened:
            self.bw_image = imp.convert_to_black_and_white(self.image, self.buckets.get(), self.smoothness_radius.get())
            self.show()

    def show(self):
        # # display_photo = PIL.ImageTk.PhotoImage(resize(image))
        # self.panel.configure(image=self.bw_image)
        # self.panel.image = self.bw_image
        display_photo = PIL.ImageTk.PhotoImage(imp.resize(self.bw_image, new_width=self.panel.winfo_width(), new_height=self.panel.winfo_height()))
        self.panel.configure(image=display_photo)
        self.panel.image = display_photo

    def convert(self):
        # display the text in text field
        text = pytess.convert_img2text(self.bw_image)
        # text = pytess.img2boxes(self.image)
        # text = pytess.img2data(self.bw_image)
        self.text_field.delete("1.0", "end")
        self.text_field.insert("1.0", text)

    def crop_image(self):
        """
        This function is use to enable the user to crop the image
        After clicking the button, the user will be able to see 4 
        dots represent the 4 edge point of the image. The user can
        drag the dots to resize the image. After the user is done
        user need to press transform button to transform the image.

        After clicking the button, user can cancel by clicking the
        button again.
        """ 
        self.point1 = (0, 0)
        self.point2 = (0, self.image.height)
        self.point3 = (self.image.width, 0)
        self.point4 = (self.image.width, self.image.height)

        self.image.transform((self.image.width, self.image.height), PIL.Image.QUAD, (self.point1, self.point2, self.point3, self.point4))


        pass

    def transform_image(self):
        pass

    def undo_crop(self):
        pass
    

if __name__ == "__main__":
    root = Tk()
    root.title("Document Scanner")
    root.minsize(1000, 555)
    app = DocScanner(root)
    root.mainloop()