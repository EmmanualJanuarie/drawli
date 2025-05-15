# Import necessary libraries
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import sys
import ctypes
import cv2
import numpy as np
import requests
import base64
from tkinter import filedialog, messagebox

# Set initial appearance theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CartoonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Basic window setup
        self.title("Cartoonify App")
        self.geometry("1300x700")
        self.overrideredirect(True)  # Removes window borders and title bar

        self.after(10, self.set_rounded_corners, 30)  # Apply rounded corners

        # Offsets for window dragging
        self._offsetx = 0
        self._offsety = 0

        # Main container frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Header section (top bar with logo and navigation)
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Enable dragging of the window by clicking the header
        self.header_frame.bind("<ButtonPress-1>", self.start_move)
        self.header_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.header_frame.bind("<B1-Motion>", self.do_move)

        # App logo
        self.logo_label = ctk.CTkLabel(self.header_frame, text="Drawli", font=("Arial", 20, "bold"))
        self.logo_label.grid(row=0, column=0, padx=(30, 0), pady=10, sticky="w")

        # Navigation items
        self.nav_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.nav_frame.grid(row=0, column=1)
        nav_items = ["Home", "Demo", "About", "Guide"]
        self.nav_labels = []
        for i, nav_item in enumerate(nav_items):
            nav_label = ctk.CTkLabel(self.nav_frame, text=nav_item, font=("Arial", 16))
            nav_label.grid(row=0, column=i, padx=20)
            self.nav_labels.append(nav_label)

        # Dark mode switch
        self.dark_mode_switch = ctk.CTkSwitch(self.header_frame, text="Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_switch.grid(row=0, column=2, padx=20, pady=10, sticky="e")
        if ctk.get_appearance_mode() == "dark":
            self.dark_mode_switch.select()

        # Exit button
        self.exit_button = ctk.CTkButton(
            self.header_frame,
            text="Exit",
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.on_exit
        )
        self.exit_button.grid(row=0, column=3, padx=(0, 30), pady=10, sticky="e")

        # Scrollable main content area
        self.scrollable_body = ctk.CTkScrollableFrame(self.main_frame, corner_radius=0)
        self.scrollable_body.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Main heading
        self.main_heading = ctk.CTkLabel(
            self.scrollable_body,
            text="Cartoon Generator (Free & No Login)",
            font=("Arial", 50, "bold"),
            wraplength=800
        )
        self.main_heading.pack(anchor="w", padx=(270, 0))

        # Subheading
        self.main_heading_sub_text = ctk.CTkLabel(
            self.scrollable_body,
            text="Welcome to Drawli — your free cartoon image generator. Instantly transform any photo into your desired cartoon style.",
            font=("Arial", 18),
            wraplength=700
        )
        self.main_heading_sub_text.pack(anchor="w", pady=(20, 0), padx=(290, 0))

        # Image upload demo section
        self.demo_frame = ctk.CTkFrame(self.scrollable_body, width=720, border_color="white", border_width=0)
        self.demo_frame.pack(padx=10, pady=(40, 0))

        self.demo_label = ctk.CTkLabel(self.demo_frame, text="Upload Image", font=("Arial", 20, "bold"))
        self.demo_label.pack(pady=(20, 10))

        # Upload canvas area with dotted border
        bg_color = "#2a2a2a" if ctk.get_appearance_mode() == "dark" else "white"
        text_color = "#888888"
        self.upload_canvas = tk.Canvas(self.demo_frame, width=720, height=250, bg=bg_color, highlightthickness=0)
        self.upload_canvas.pack(pady=10)

        # Dotted border box
        self.dotted_border = self.upload_canvas.create_rectangle(
            10, 10, 700, 240, dash=(5, 5), outline=text_color, width=2
        )

        # Upload instruction label
        self.upload_text_label = tk.Label(
            self.upload_canvas,
            text="📷\nClick or drag an image to upload",
            font=("Arial", 16),
            justify="center",
            fg=text_color,
            bg=bg_color
        )
        self.upload_text_label.place(relx=0.5, rely=0.5, anchor="center")

        # Hover effects on upload area
        def on_enter(event):
            self.upload_canvas.itemconfig(self.dotted_border, outline="#3b82f6")
            self.upload_text_label.config(fg="#3b82f6")

        def on_leave(event):
            self.upload_canvas.itemconfig(self.dotted_border, outline=text_color)
            self.upload_text_label.config(fg=text_color)

        self.upload_canvas.bind("<Enter>", on_enter)
        self.upload_canvas.bind("<Leave>", on_leave)
        self.upload_canvas.bind("<Button-1>", self.open_file_dialog)

        # Image display label (shows uploaded image)
        self.image_display_label = ctk.CTkLabel(self.demo_frame, text="")
        self.image_display_label.pack(pady=20)

        # Cartoon style selection section
        self.style_section_frame = ctk.CTkFrame(self.demo_frame, fg_color="transparent")
        self.style_section_frame.pack(pady=(20, 10), fill="x")

        self.style_header = ctk.CTkLabel(
            self.style_section_frame, text="Choose a Cartoon Style", font=("Arial", 24, "bold")
        )
        self.style_header.pack(anchor="w", padx=20)

        self.style_subtext = ctk.CTkLabel(
            self.style_section_frame,
            text="Click one of the styles below to apply it to your image.",
            font=("Arial", 16)
        )
        self.style_subtext.pack(anchor="w", padx=20, pady=(0, 10))

        self.style_row_frame = ctk.CTkFrame(self.style_section_frame, fg_color="transparent")
        self.style_row_frame.pack(anchor="w", padx=20)

        # Generate Cartoon Button
        self.generate_button = ctk.CTkButton(
            self.style_section_frame,
            text="Generate Cartoon",
            font=("Arial", 18),
            command=self.generate_cartoon
        )
        self.generate_button.pack(pady=20)

         # Define your style image paths and unique text labels
        self.style_data = [
            ("style_images/style1.png", "Detailed Style"),
            ("style_images/style2.png", "Watercolor Sketch"),
            ("style_images/style3.png", "Disney Look"),
            ("style_images/style4.jfif", "Comic Pop"),
            ("style_images/style5.jpg", "Pastel Art"),
            ("style_images/style6.jpg", "Anime Glow")
        ]

        # Define functions to be called on style selection
        def apply_style_1():
            if not hasattr(self, "original_pil_image"):
                print("No image uploaded to apply style.")
                return

            # Convert PIL to OpenCV (NumPy array)
            img = np.array(self.original_pil_image.convert("RGB"))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # Apply style
            cartoon = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)

            # Convert back to PIL
            cartoon_rgb = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
            cartoon_pil = Image.fromarray(cartoon_rgb)

            self.generated_cartoon_image = cartoon_pil  # Store result (don't update label yet)

        def apply_style_2():
            print("Applied Watercolor Sketch")
        def apply_style_3():
            print("Applied Disney Look")
        def apply_style_4():
            print("Applied Comic Pop")
        def apply_style_5():
            print("Applied Pastel Art")
        def apply_style_6():
            print("Applied Anime Glow")

        self.style_functions = [
            apply_style_1, apply_style_2, apply_style_3,
            apply_style_4, apply_style_5, apply_style_6
        ]

        # Helper to get background color based on theme
        def get_bg_color():
            return "#1f2937" if ctk.get_appearance_mode() == "dark" else "white"

        bg_color = get_bg_color()
        fg_text_color = "white" if ctk.get_appearance_mode() == "dark" else "black"

        self.style_image_labels = []

        for i, (image_path, label_text) in enumerate(self.style_data):
            try:
                img = Image.open(image_path).convert("RGBA")
                img = img.resize((100, 100), Image.Resampling.LANCZOS)

                # Rounded corners radius 5 mask
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, 100, 100), radius=5, fill=300)
                img.putalpha(mask)

                photo = ImageTk.PhotoImage(img)

                container = tk.Frame(self.style_row_frame, bg=bg_color)
                container.grid(row=0, column=i, padx=8, pady=5)
                container.bind("<Button-1>", lambda e, idx=i: self.style_selected(idx))

                label = tk.Label(container, image=photo, bg=bg_color, cursor="hand2")
                label.image = photo
                label.pack()
                label.bind("<Button-1>", lambda e, idx=i: self.style_selected(idx))

                text_label = tk.Label(container, text=label_text, bg=bg_color,
                                      fg=fg_text_color, font=("Arial", 10, "bold"))
                text_label.pack(pady=4)
                text_label.bind("<Button-1>", lambda e, idx=i: self.style_selected(idx))

                self.style_image_labels.append((container, label, text_label))

            except Exception as e:
                print(f"Error loading style image {image_path}: {e}")

         # Grid configuration for layout resizing
            self.main_frame.grid_rowconfigure(1, weight=1)
            self.main_frame.grid_columnconfigure(0, weight=1)
            self.update_theme()  # Apply initial theme
            self.uploaded_image = None  # Placeholder for uploaded image
            self.selected_style_index = None  # Track selected style index


    def generate_cartoon(self):
        self.outer_result_frame = ctk.CTkFrame(self.scrollable_body, width=780, height=550, border_color="white", border_width=0)
        self.outer_result_frame.pack(padx=10, pady=(40, 0))
        
        # Prevent frame from shrinking to fit contents
        self.outer_result_frame.pack_propagate(False)
        self.result_title = ctk.CTkLabel(self.outer_result_frame, text="Your Cartoon", font=("Arial", 20, "bold"))
        self.result_title.pack(pady=(20, 10))
        
        if not hasattr(self, "generated_cartoon_image") or self.generated_cartoon_image is None:
            print("Please upload an image and select a style first.")
            return
        
        # Clear old outer_result_frame if it exists
        if hasattr(self, "result_frame") and self.outer_result_frame.winfo_exists():
            self.outer_result_frame.destroy()
            
         # Prepare and show cartoon image
        cartoon = self.generated_cartoon_image.copy()
        cartoon.thumbnail((600, 600))
        cartoon_tk = ImageTk.PhotoImage(cartoon)
        self.cartoon_result_label = ctk.CTkLabel(self.outer_result_frame, image=cartoon_tk, text="")
        self.cartoon_result_label.image = cartoon_tk
        self.cartoon_result_label.pack(pady=10)
        # Download button
        download_btn = ctk.CTkButton(
            self.outer_result_frame,
            text="Download Cartoon Image",
            font=("Arial", 16),
            command=self.download_cartoon
        )
        download_btn.pack(pady=(10, 20))


    def download_cartoon(self):
        if not hasattr(self, "generated_cartoon_image") or self.generated_cartoon_image is None:
            print("No image to save.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Cartoon Image"
        )
        if filepath:
            try:
                self.generated_cartoon_image.save(filepath)
                print(f"Cartoon image saved to: {filepath}")
            except Exception as e:
                print(f"Failed to save image: {e}")

    def style_selected(self, index):
        self.select_style(index)  # Update highlight/selection
        if 0 <= index < len(self.style_functions):
            self.style_functions[index]()  # Call corresponding cartoon style function

    # Utility: Get background color depending on theme
    def get_bg_color(self):
        return "#2a2a2a" if ctk.get_appearance_mode() == "dark" else "white"

    # Handle selection of cartoon style
    def select_style(self, index):
        if self.selected_style_index is not None:
            _, prev_image_label, _ = self.style_image_labels[self.selected_style_index]
            prev_image_label.configure(highlightthickness=0)

        container, image_label, _ = self.style_image_labels[index]
        image_label.configure(highlightthickness=3, highlightbackground="#3b82f6", bd=1)
        self.selected_style_index = index
        print(f"Selected Style {index + 1}")

    # Open file dialog to choose image
    def open_file_dialog(self, event=None):
        filetypes = (("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*"))
        filepath = filedialog.askopenfilename(title="Select Image", filetypes=filetypes)
        if filepath:
            self.display_image(filepath)

    def load_image(self, path):
        """Load and display the uploaded image."""
        try:
            img = Image.open(path)
            img.thumbnail((600, 600))
            photo = ImageTk.PhotoImage(img)
            self.image_display_label.configure(image=photo)
            self.image_display_label.image = photo
        except Exception as e:
            print(f"Error loading image: {e}")

    # Display uploaded image on the canvas
    def display_image(self, filepath):
        image = Image.open(filepath)
        max_width, max_height = 700, 400
        img_width, img_height = image.size
        ratio = min(max_width / img_width, max_height / img_height, 1)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        self.image_display_label.configure(image=photo, text="")
        self.uploaded_image = photo
        self.original_pil_image = image  # Store for saving later
        self.generated_cartoon_image = None

    # Apply rounded corners to the window (Windows-specific)
    def set_rounded_corners(self, radius):
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        hrgn = ctypes.windll.gdi32.CreateRoundRectRgn(
            0, 0, self.winfo_width() + 1, self.winfo_height() + 1, radius, radius
        )
        ctypes.windll.user32.SetWindowRgn(hwnd, hrgn, True)

    # Window drag functions
    def start_move(self, event):
        self._offsetx = event.x_root - self.winfo_x()
        self._offsety = event.y_root - self.winfo_y()

    def stop_move(self, event):
        self._offsetx = 0
        self._offsety = 0

    def do_move(self, event):
        x = event.x_root - self._offsetx
        y = event.y_root - self._offsety
        self.geometry(f'+{x}+{y}')

    def toggle_dark_mode(self):
        """Toggle between light and dark themes and update colors."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)

        # Update style card colors on theme switch
        bg_color = self.get_bg_color()
        fg_text_color = "white" if new_mode == "dark" else "black"
        for container, label, text_label in getattr(self, 'style_image_labels', []):
            container.config(bg=bg_color)
            label.config(bg=bg_color)
            text_label.config(bg=bg_color, fg=fg_text_color)

        # Update upload canvas and labels colors accordingly
        upload_bg = "#2a2a2a" if new_mode == "dark" else "white"
        text_color = "#888888"
        self.upload_canvas.config(bg=upload_bg)
        self.upload_text_label.config(bg=upload_bg, fg=text_color)
        self.upload_canvas.itemconfig(self.dotted_border, outline=text_color)

    # Update UI theme based on current mode
    def update_theme(self):
        mode = ctk.get_appearance_mode()
        if mode == "light":
            bg_color, header_color, demo_color = "#f0f2f5", "white", "white"
            text_color, border, upload_bg = "#111827", "#cccccc", "white"
            upload_text_color = "#888888"
        else:
            bg_color, header_color, demo_color = "#1a1a1a", "#333333", "#2a2a2a"
            text_color, border, upload_bg = "#ffffff", "#444444", "#2a2a2a"
            upload_text_color = "#888888"

        # Apply updated colors to widgets
        self.main_frame.configure(fg_color=bg_color)
        self.header_frame.configure(fg_color=header_color)
        self.scrollable_body.configure(fg_color=bg_color)
        self.logo_label.configure(text_color=text_color)
        for nav_label in self.nav_labels:
            nav_label.configure(text_color=text_color)
        self.main_heading.configure(text_color=text_color)
        self.main_heading_sub_text.configure(text_color=text_color)
        self.demo_frame.configure(fg_color=demo_color, border_color=border)
        self.dark_mode_switch.configure(text_color=text_color, fg_color=border, progress_color="#3b82f6")
        self.exit_button.configure(
            text_color="white",
            fg_color="#ef4444" if mode == "light" else "#b91c1c",
            hover_color="#dc2626" if mode == "light" else "#991b1b"
        )
        self.upload_canvas.configure(bg=upload_bg)
        self.upload_canvas.itemconfig(self.dotted_border, outline=upload_text_color)
        self.upload_text_label.config(bg=upload_bg, fg=upload_text_color)

    # Exit the app
    def on_exit(self):
        self.destroy()
        sys.exit(0)


# Start the application
if __name__ == "__main__":
    app = CartoonApp()
    app.mainloop()
