import cv2
import numpy as np
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
import base64

# Define cartoonify effects (your existing functions)
def basic_cartoonify(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    return cv2.bitwise_and(color, color, mask=edges)

def canny_cartoonify(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    return cv2.bitwise_and(color, edges_colored)

def color_quantization(img, k=8):
    data = np.float32(img).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    return quantized.reshape(img.shape)

def combined_cartoonify(img):
    quantized = color_quantization(img, k=8)
    gray = cv2.cvtColor(quantized, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(quantized, 9, 300, 300)
    return cv2.bitwise_and(color, color, mask=edges)

def pencil_sketch(img):
    gray, color = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
    return gray, color

def detail_enhance(img):
    return cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)

def edge_preserving(img):
    return cv2.edgePreservingFilter(img, flags=1, sigma_s=60, sigma_r=0.4)

def watercolor_effect(img):
    color = cv2.bilateralFilter(img, 9, 300, 300)
    gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    return cv2.bitwise_and(color, color, mask=edges)

def oil_painting(img):
    return cv2.xphoto.oilPainting(img, 7, 1)

def emboss_effect(img):
    kernel = np.array([[0, 0, 0], [0, 1, 0], [0, 0, -1]])
    return cv2.filter2D(img, -1, kernel)

def sketch_effect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    inverted_blurred = cv2.bitwise_not(blurred)
    return cv2.divide(gray, inverted_blurred, scale=256.0)

def sepia(img):
    kernel = np.array([[0.393, 0.769, 0.189],
                       [0.349, 0.686, 0.168],
                       [0.272, 0.534, 0.131]])
    return cv2.transform(img, kernel)

def hdr_effect(img):
    return cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)

def summer_effect(img):
    increase = np.array([0, 80, 160, 256])
    decrease = np.array([0, 50, 100, 256])
    red, green, blue = cv2.split(img)
    red = cv2.LUT(red, increase)
    blue = cv2.LUT(blue, decrease)
    return cv2.merge((blue, green, red))

def winter_effect(img):
    increase = np.array([0, 50, 100, 256])
    decrease = np.array([0, 80, 160, 256])
    red, green, blue = cv2.split(img)
    red = cv2.LUT(red, decrease)
    blue = cv2.LUT(blue, increase)
    return cv2.merge((blue, green, red))

def gaussian_blur(img, ksize=(5, 5)):
    return cv2.GaussianBlur(img, ksize, 0)

def solarize(img, threshold=128):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.bitwise_not(img)
    _, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def vignette(img):
    rows, cols = img.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols/3)
    kernel_y = cv2.getGaussianKernel(rows, rows/3)
    kernel = kernel_y * kernel_x.T
    mask = kernel / kernel.max()
    masked = np.copy(img)
    for i in range(3):
        masked[:, :, i] = img[:, :, i] * mask
    return masked

def lomo(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img[:, :, 1] = cv2.add(img[:, :, 1], 50)
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    return cv2.GaussianBlur(img, (15, 15), 0)

def tilt_shift(img):
    rows, cols = img.shape[:2]
    mask = np.zeros((rows, cols), dtype=np.uint8)
    mask[rows//3:2*rows//3, :] = 255
    mask = cv2.GaussianBlur(mask, (15, 15), 0)
    mask = cv2.merge([mask, mask, mask])
    return cv2.addWeighted(img, 1, mask, -0.5, 0)

def posterize_effect(img, levels=4):
    img_float = np.float32(img)
    img_posterized = np.floor(img_float / (256.0 / levels)) * (256.0 / levels)
    return np.uint8(img_posterized)

def negative_effect(img):
    return cv2.bitwise_not(img)

def pixelate_effect(img, pixel_size=10):
    height, width = img.shape[:2]
    temp = cv2.resize(img, (width // pixel_size, height // pixel_size))
    return cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)


# Main Application
class CartoonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cartoonify App")
        self.geometry("900x700")
        self.original_image = None
        self.display_image = None

        self.load_btn = ctk.CTkButton(self, text="Load Image", command=self.load_image)
        self.load_btn.pack(pady=10)

        self.style_var = ctk.StringVar(value="basic")
        self.dropdown = ctk.CTkOptionMenu(self, values=[
            "basic", "canny", "quantize", "combined", "pencil", "detail", "edge", "watercolor", 
            "oil", "emboss", "sketch", "posterize", "negative", "pixelate", "sepia", "HDR", "summer", 
            "winter", "gaussin blur", "solarize", "vignette", "lomo", "tilt shift", "cartoon image"
        ], variable=self.style_var)
        self.dropdown.pack(pady=10)

        self.cartoon_btn = ctk.CTkButton(self, text="Apply Cartoon Effect", command=self.apply_cartoon)
        self.cartoon_btn.pack(pady=10)

        self.image_canvas = ctk.CTkCanvas(self, width=800, height=450, bg="white")
        self.image_canvas.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if not file_path:
            return
        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("Error", "Failed to load image.")
            return
        img = cv2.resize(img, (800, 450), interpolation=cv2.INTER_AREA)
        self.original_image = img
        self.show_image(img)
        self.status_label.configure(text="Image loaded.")

    def show_image(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        self.display_image = ImageTk.PhotoImage(pil_img)
        self.image_canvas.delete("all")
        self.image_canvas.create_image(0, 0, anchor="nw", image=self.display_image)

    def cartoon_image_api(self, img):
        _, img_encoded = cv2.imencode('.jpg', img)
        img_bytes = img_encoded.tobytes()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        url = "https://cartoon-yourself.p.rapidapi.com/facebody/api/portrait-animation/portrait-animation"

        headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": "cartoon-yourself.p.rapidapi.com",
            "x-rapidapi-key": "ea0d330537mshde06fbc42ff241cp1ee449jsn8861d9f8eb73"
        }

        data = {
            "image": img_base64,
            "type": "portrait-animation"
        }

        try:
            response = requests.post(url, headers=headers, json=data)  # <-- note json=data
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            messagebox.showerror("HTTP Error", f"HTTP error occurred:\n{http_err}\nResponse content:\n{response.text}")
            print("HTTP Error", f"HTTP error occurred:\n{http_err}\nResponse content:\n{response.text}")
            return None

        # The API likely returns the cartoon image base64 string in response JSON, e.g.:
        res_json = response.json()
        if "image" in res_json:
            cartoon_b64 = res_json["image"]
            cartoon_bytes = base64.b64decode(cartoon_b64)
            nparr = np.frombuffer(cartoon_bytes, np.uint8)
            cartoon_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return cartoon_img
        else:
            messagebox.showerror("API Error", "No image returned from API.")
            return None



    def apply_cartoon(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            print("Error", "No image loaded.")
            return
        effect = self.style_var.get()
        effect_map = {
            "basic": basic_cartoonify,
            "canny": canny_cartoonify,
            "quantize": color_quantization,
            "combined": combined_cartoonify,
            "pencil": pencil_sketch,
            "detail": detail_enhance,
            "edge": edge_preserving,
            "watercolor": watercolor_effect,
            "oil": oil_painting,
            "emboss": emboss_effect,
            "sketch": sketch_effect,
            "posterize": posterize_effect,
            "negative": negative_effect,
            "pixelate": pixelate_effect,
            "sepia": sepia,
            "HDR": hdr_effect,
            "summer": summer_effect,
            "winter": winter_effect,
            "gaussin blur": gaussian_blur,
            "solarize": solarize,
            "vignette": vignette,
            "lomo": lomo,
            "tilt shift": tilt_shift,
            "cartoon image": self.cartoon_image_api
        }

        effect_function = effect_map.get(effect)
        if effect_function:
            if effect == "cartoon image":
                result_img = effect_function(self.original_image)
                if result_img is None:
                    return  # API error already shown
            else:
                result_img = effect_function(self.original_image)

                if isinstance(result_img, tuple):
                    result_img = result_img[1]

                if len(result_img.shape) == 2:
                    result_img = cv2.cvtColor(result_img, cv2.COLOR_GRAY2BGR)

            self.show_image(result_img)
            self.status_label.configure(text=f"Applied {effect} effect.")
        else:
            messagebox.showerror("Error", f"Effect '{effect}' is not recognized.")

if __name__ == "__main__":
    app = CartoonApp()
    app.mainloop()
