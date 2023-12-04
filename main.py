from tkinter import Tk, Frame, Scale, Button, Label, IntVar, DoubleVar, Text, LabelFrame, Canvas, NW
from tkinter import filedialog as fd
import PIL.ImageTk
import PIL.Image
import PIL.ImageTransform
import image_processing as imp
import pytesseract_calling as pytess
import win32clipboard
import io
from edge import Edge


class DocScanner:
    def __init__(self, root) -> None:
        self.image = None
        self.bw_image = None
        self.buckets = IntVar()
        self.smoothness_radius = DoubleVar(value=0.)

        # key and mouse binding
        root.bind_all('<Control-v>', self.handle_paste)
        root.bind_all('<Control-c>', self.handle_copy)

        # init the crop point
        self.point1 = None
        self.point2 = None
        self.point3 = None
        self.point4 = None
        self.transform_in_progress = False
        self.dots = []

        self.option_frame = LabelFrame(root)
        self.text_frame = LabelFrame(root)

        self.option_frame.pack(side="left", padx=10)
        self.text_frame.pack(side="right")


        # option frame, showing image
        # image
        self.img_frame = LabelFrame(self.option_frame, 
                        width=850, 
                        height=850)
        self.canvas = Canvas(self.img_frame, width=850, height=850)
        self.img_frame.pack()
        self.canvas.pack()
        

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
            self.image = PIL.Image.open(opened_image)
            self.reset_crop_point()
            self.update_image()

    def handle_paste(self, event=None):
        image_data = self.get_clipboard_image()
        if image_data:
            try:
                self.image = PIL.Image.open(io.BytesIO(image_data)) # type: ignore
            except Exception as e:
                print("The data in Clipboard is not an Image.", e)
                return
            self.reset_crop_point()
            self.update_image()

    def handle_copy(self, event=None):
        # copy text from textfield
        text = self.text_field.get("1.0", "end")
        win32clipboard.OpenClipboard(0)
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        except Exception as e:
            print(f"Error setting clipboard data: {e}")
        finally:
            win32clipboard.CloseClipboard()

    def get_clipboard_image(self):
        win32clipboard.OpenClipboard(0)
        try:
            # Attempt to get data in different formats
            data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
            if data:
                return data
            data = win32clipboard.GetClipboardData(win32clipboard.CF_BITMAP)
            if data:
                return data
        except Exception as e:
            print(f"Error getting clipboard data: {e}")
        finally:
            win32clipboard.CloseClipboard()

    def update_image(self):
        # if you think that clicking this button revert your crop is a bug, you are wrong
        # it is a feature
        if self.image != None:
            self.bw_image = imp.convert_to_black_and_white(self.image, self.buckets.get(), self.smoothness_radius.get())
            self.show()

    def show(self):
        display_photo = PIL.ImageTk.PhotoImage(imp.resize(self.bw_image, 850))
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=NW, image=display_photo)
        self.canvas.image = display_photo # type: ignore

    def convert(self):
        text = pytess.convert_img2text(self.bw_image)
        self.text_field.delete("1.0", "end")
        self.text_field.insert("1.0", text)

    def crop_image(self):
        if self.image == None:
            return
        width, height = self.get_resize_width_height(self.image.width, self.image.height)
        self.point1 = (0, 0) if self.point1 == None else self.point1
        self.point2 = (width, 0) if self.point2 == None else self.point2
        self.point3 = (0, height) if self.point3 == None else self.point3
        self.point4 = (width, height) if self.point4 == None else self.point4
        self.start_stop_transform_loop()
    
    def reset_crop_point(self):
        self.point1 = None
        self.point2 = None
        self.point3 = None
        self.point4 = None

    def start_stop_transform_loop(self):
        if self.transform_in_progress:
            self.hide_dots_and_update()
            return
        self.show_dots()
        self.update_canvas()

    def create_dots(self):
        if self.image == None:
            return
        resized_width, resized_height = self.get_resize_width_height(self.image.width, self.image.height)
        for point in [self.point1, self.point2, self.point4, self.point3]:
            self.dots.append(Edge(self.canvas, point[0], point[1], resized_width, resized_height))

    def update_coordinates(self):
        if len(self.dots) != 4:
            return
        self.point1 = self.dots[0].get_position()
        self.point2 = self.dots[1].get_position()
        self.point3 = self.dots[3].get_position()
        self.point4 = self.dots[2].get_position()
        self.point1_coordiante["text"] = f"{self.point1[0]}, {self.point1[1]}"
        self.point2_coordiante["text"] = f"{self.point2[0]}, {self.point2[1]}"
        self.point3_coordiante["text"] = f"{self.point3[0]}, {self.point3[1]}"
        self.point4_coordiante["text"] = f"{self.point4[0]}, {self.point4[1]}"

    def show_dots(self):
        if not self.transform_in_progress:
            self.create_dots()
            self.transform_in_progress = True

    def hide_dots_and_update(self):
        self.canvas.delete("dot")
        self.canvas.delete("line")
        self.dots = []
        self.transform_in_progress = False

    def update_canvas(self):
        if self.transform_in_progress:
            self.connect_dots()
            self.update_coordinates()
            root.after(100, self.update_canvas)  # Update every 100 milliseconds

    def connect_dots(self):
        self.canvas.delete("line")
        for i in range(len(self.dots)-1, -2, -1):
            x1, y1 = self.dots[i].get_position()
            x2, y2 = self.dots[i-1].get_position() if i > 0 else self.dots[-1].get_position()
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1, tags="line")

    def transform_image(self):
        if self.image == None:
            return
        if len(self.dots) != 4:
            return
        self.point1 = self.dots[0].get_position()
        self.point2 = self.dots[1].get_position()
        self.point3 = self.dots[3].get_position()
        self.point4 = self.dots[2].get_position()

        self.bw_image = imp.transform_image(self.bw_image, 
                                            self.get_real_coordinates(self.point1, self.image.width, self.image.height), 
                                            self.get_real_coordinates(self.point2, self.image.width, self.image.height), 
                                            self.get_real_coordinates(self.point3, self.image.width, self.image.height), 
                                            self.get_real_coordinates(self.point4, self.image.width, self.image.height))
        self.hide_dots_and_update()
        self.show()

    def get_real_coordinates(self, coord, original_width, original_height):
        x, y = coord
        resized_width, resized_height = self.get_resize_width_height(original_width, original_height)
        width_ratio = original_width / resized_width
        height_ratio = original_height / resized_height
        return round(x * width_ratio), round(y * height_ratio)
    
    def get_resize_width_height(self, original_width, original_height):
        ratio = max(original_width, original_height) / 850
        resized_width, resized_height = original_width / ratio, original_height / ratio
        return round(resized_width), round(resized_height)

    def undo_crop(self):
        if self.image == None:
            return
        self.bw_image = imp.convert_to_black_and_white(self.image, self.buckets.get(), self.smoothness_radius.get())
        self.show()
    

if __name__ == "__main__":
    root = Tk()
    root.title("Document Scanner")
    root.minsize(1000, 555)
    app = DocScanner(root)
    root.mainloop()