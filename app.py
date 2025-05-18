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
import cv2


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
        
        def camera_to_cartoon_function():
            # Open webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Cannot open webcam")
                return

            print("Press 'c' to capture your photo or 'q' to quit camera.")
            captured = False
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame from webcam")
                    break

                cv2.imshow("Camera - Press 'c' to capture, 'q' to quit", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'):
                    # Capture frame and exit loop
                    captured = True
                    break
                elif key == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

            if not captured:
                print("No photo captured.")
                return

            try:
                # Convert captured frame from BGR to RGB
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Apply cartoon effect - your existing style
                cartoon = cv2.detailEnhance(img_rgb, sigma_s=10, sigma_r=0.15)

                # Convert to PIL Image
                cartoon_pil = Image.fromarray(cartoon)

                # Resize for display if needed
                max_size = (600, 600)
                cartoon_pil.thumbnail(max_size)

                # Update class variables for UI and further processing
                self.original_pil_image = cartoon_pil
                self.generated_cartoon_image = cartoon_pil

                # Convert to ImageTk PhotoImage for Tkinter label
                photo = ImageTk.PhotoImage(cartoon_pil)
                self.image_display_label.configure(image=photo, text="")
                self.image_display_label.image = photo

                print("Camera cartoon image captured and displayed.")

            except Exception as e:
                print(f"Failed to process captured image: {e}")



        def video_to_cartoon_function():
            import cv2
            import numpy as np
            from PIL import Image, ImageTk
            import tempfile
            import os
            import time
            from tkinter import messagebox, filedialog

            max_duration_sec = 120  # max 2 minutes recording
            fps = 20  # target frames per second

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Cannot open webcam")
                messagebox.showerror("Webcam Error", "Cannot open webcam.")
                return

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            temp_file = tempfile.NamedTemporaryFile(suffix=".avi", delete=False)
            temp_filename = temp_file.name
            temp_file.close()

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(temp_filename, fourcc, fps, (width, height))

            start_time = time.time()
            print("Recording video from webcam. Press 'q' to stop early.")

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture frame")
                    break

                elapsed = time.time() - start_time
                if elapsed > max_duration_sec:
                    print("Max recording duration reached.")
                    break

                # Cartoon effect - edges detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.medianBlur(gray, 5)
                edges = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_MEAN_C,
                    cv2.THRESH_BINARY,
                    blockSize=9, C=9
                )
                color = cv2.bilateralFilter(frame, d=9, sigmaColor=250, sigmaSpace=250)
                cartoon = cv2.bitwise_and(color, color, mask=edges)

                out.write(cartoon)

                cv2.imshow("Recording Cartoon Video - Press 'q' to stop", cartoon)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Recording stopped by user.")
                    break

            cap.release()
            out.release()
            cv2.destroyAllWindows()

            # Preview first frame
            cap_preview = cv2.VideoCapture(temp_filename)
            ret, first_frame = cap_preview.read()
            cap_preview.release()

            if not ret:
                messagebox.showerror("Preview Error", "Failed to load cartoon video for preview.")
                return

            first_frame_rgb = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(first_frame_rgb)
            pil_img.thumbnail((600, 600))
            img_tk = ImageTk.PhotoImage(pil_img)

            # Clear previous result frame if exists
            if hasattr(self, "outer_result_frame") and self.outer_result_frame.winfo_exists():
                self.outer_result_frame.destroy()

            self.outer_result_frame = ctk.CTkFrame(self.scrollable_body, width=780, height=600, border_color="white", border_width=0)
            self.outer_result_frame.pack(padx=10, pady=(40, 0))
            self.outer_result_frame.pack_propagate(False)

            self.result_title = ctk.CTkLabel(self.outer_result_frame, text="Your Cartoon Video Preview", font=("Arial", 20, "bold"))
            self.result_title.pack(pady=(20, 10))

            self.cartoon_result_label = ctk.CTkLabel(self.outer_result_frame, image=img_tk, text="")
            self.cartoon_result_label.image = img_tk
            self.cartoon_result_label.pack(pady=10)

            # Store video path for future use
            self.cartoon_video_path = temp_filename

            # Define download function
            def download_cartoon_video():
                save_path = filedialog.asksaveasfilename(defaultextension=".avi",
                                                        filetypes=[("AVI files", "*.avi"), ("All files", "*.*")],
                                                        title="Save Cartoon Video")
                if save_path:
                    try:
                        import shutil
                        shutil.copyfile(temp_filename, save_path)
                        messagebox.showinfo("Saved", f"Cartoon video saved to: {save_path}")
                    except Exception as e:
                        messagebox.showerror("Save Error", f"Failed to save video: {e}")

            # Define play function
            def play_cartoon_video():
                video_cap = cv2.VideoCapture(self.cartoon_video_path)
                if not video_cap.isOpened():
                    messagebox.showerror("Playback Error", "Failed to open cartoon video for playback.")
                    return

                print("Playing cartoon video. Press 'q' to stop.")

                while True:
                    ret, frame = video_cap.read()
                    if not ret:
                        break
                    cv2.imshow("Cartoon Video Playback - Press 'q' to stop", frame)
                    if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
                        break

                video_cap.release()
                cv2.destroyAllWindows()

            # Buttons for download and play
            button_frame = ctk.CTkFrame(self.outer_result_frame, fg_color="transparent")
            button_frame.pack(pady=(10, 20))

            download_btn = ctk.CTkButton(button_frame, text="Download Cartoon Video", font=("Arial", 16), command=download_cartoon_video)
            download_btn.pack(side="left", padx=15)

            play_btn = ctk.CTkButton(button_frame, text="Play Cartoon Video", font=("Arial", 16), command=play_cartoon_video)
            play_btn.pack(side="left", padx=15)

            print(f"Cartoon video recorded, preview shown. File saved at: {temp_filename}")

    
        self.recommendation_frame = ctk.CTkFrame(self.demo_frame, fg_color="transparent")
        self.recommendation_frame.pack(pady=(10, 20), padx=(160,0), fill="x")

        # Common style for the buttons
        button_style = {
            "font": ("Arial", 16),
            "fg_color": "transparent",
            "border_color": "#3b82f6",
            "hover_color": "#3b82f6",
            "border_width": 2,
            "width": 140,
            "height": 40,
        }


        self.camera_to_cartoon_button = ctk.CTkButton(
            self.recommendation_frame,
            text="Camera to Cartoon",
            **button_style,
            command=camera_to_cartoon_function  # Define this method below
        )
        self.camera_to_cartoon_button.pack(side="left", padx=(0, 15))

        self.video_to_cartoon_button = ctk.CTkButton(
            self.recommendation_frame,
            text="Video to Cartoon",
            **button_style,
            command=video_to_cartoon_function  # Define this method below
        )
        self.video_to_cartoon_button.pack(side="left", padx=(0, 15))



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

                container = tk.Frame(self.style_row_frame, bg="#2A2A2A")
                container.grid(row=0, column=i, padx=8, pady=5)
                container.bind("<Button-1>", lambda e, idx=i: self.style_selected(idx))

                label = tk.Label(container, image=photo, bg="#2A2A2A", cursor="hand2")
                label.image = photo
                label.pack()
                label.bind("<Button-1>", lambda e, idx=i: self.style_selected(idx))

                text_label = tk.Label(container, text=label_text, bg="#2A2A2A",
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

    # Horizontal line after the demo section
        self.demo_line = ctk.CTkFrame(self.scrollable_body, height=2, fg_color="#676767" , width=800)
        self.demo_line.pack(padx=20, pady=(90, 30))
        
        self.about()
        self.tips()
        
        self.demo_line_2 = ctk.CTkFrame(self.scrollable_body, height=2, fg_color="#676767" , width=800)
        self.demo_line_2.pack(padx=20, pady=(90, 30))
        
        self.guide()
        
        self.demo_line_3 = ctk.CTkFrame(self.scrollable_body, height=2, fg_color="#676767" , width=800)
        self.demo_line_3.pack(padx=20, pady=(90, 30))
        
        self.FAQs()
        
        self.create_footer()
        
    def about(self):
        # Main heading
        self.information_line_heading = ctk.CTkLabel(
            self.scrollable_body,
            text="More Information: About Drawli",
            font=("Arial", 50, "bold"),
            wraplength=800
        )
        self.information_line_heading.pack(anchor="w", padx=(270, 0))
        
        # Subheading
        self.information = ctk.CTkLabel(
            self.scrollable_body,
            text="Drawli is a user-friendly application that allows you to transform your photos and videos into cartoon-style images. With a variety of cartoon styles to choose from, you can easily create fun and unique images to share with friends and family. Whether you want to give your selfies a whimsical twist or create a cartoon version of your favorite moments, Drawli makes the process simple and enjoyable. The intuitive interface ensures that users of all ages can navigate the app effortlessly, making it a perfect tool for both casual users and creative enthusiasts.In addition to static images, Drawli is continuously evolving to enhance your creative experience. \n\n Upcoming features will allow you to take a picture of yourself using your webcam, instantly turning it into a cartoon image. You will also be able to upload videos and apply cartoon effects, bringing your animated moments to life. Furthermore, the integration of voice-to-image generation will enable you to describe the cartoon you envision, and Drawli will use advanced AI tools to create it for you. With these exciting features on the horizon, Drawli is set to become your go-to application for all things cartoon!",
            font=("Arial", 18),
            wraplength=700,
            justify="left"
            
        )
        self.information.pack(anchor="w", pady=(20, 0), padx=(270, 0))
        
        # Q1 - Heading
        self.question1_heading = ctk.CTkLabel(
            self.scrollable_body,
            text="Why Choose Drawli?",
            font=("Arial", 30, "bold"),
            wraplength=700,
            justify="left"
            
        )
        self.question1_heading.pack(anchor="w", pady=(30, 0), padx=(270, 0))
        
        # ----- [Reasons] ---- - here they are
        
        #REASON1
        # Create container frame
        self.line_frame_1 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.line_frame_1.pack(anchor="w",pady=(30, 0), padx=(270, 0))
            
        # Colored symbol label
        self.symbol_label_r1 = ctk.CTkLabel(self.line_frame_1, text="✓", font=("Arial", 18), text_color="#3b82f6")
        self.symbol_label_r1.pack(side="left", padx=(25,0))
        
        # Text label
        self.text_label_r1 = ctk.CTkLabel(self.line_frame_1, text="Instant Results - ", font=("Arial", 18, "bold"))
        self.text_label_r1.pack(side="left",  padx=(29,0))
        
        self.text_sub_r1 = ctk.CTkLabel(self.line_frame_1, text="Image to cartoon in a matter of seconds-no more editing", font=("Arial", 18, "italic"))
        self.text_sub_r1.pack(side="left",  padx=(0,0))
        
        #REASON2
        # Create container frame
        self.line_frame_2 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.line_frame_2.pack(anchor="w",pady=(30, 0), padx=(270, 0))
            
        # Colored symbol label
        self.symbol_label_r1 = ctk.CTkLabel(self.line_frame_2, text="✓", font=("Arial", 18), text_color="#3b82f6")
        self.symbol_label_r1.pack(side="left", padx=(25,0))
        
        # Text label
        self.text_label_r1 = ctk.CTkLabel(self.line_frame_2, text="No Design Skills - ", font=("Arial", 18, "bold"))
        self.text_label_r1.pack(side="left",  padx=(29,0))
        
        self.text_sub_r1 = ctk.CTkLabel(self.line_frame_2, text="No Pricey software needed, just upload and CARTOONIFY!", font=("Arial", 18, "italic"))
        self.text_sub_r1.pack(side="left",  padx=(0,0))
        
        #REASON3
        # Create container frame
        self.line_frame_3 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.line_frame_3.pack(anchor="w",pady=(30, 0), padx=(270, 0))
            
        # Colored symbol label
        self.symbol_label_r1 = ctk.CTkLabel(self.line_frame_3, text="✓", font=("Arial", 18), text_color="#3b82f6")
        self.symbol_label_r1.pack(side="left", padx=(25,0))
        
        # Text label
        self.text_label_r1 = ctk.CTkLabel(self.line_frame_3, text="It's Fun & Engaging - ", font=("Arial", 18, "bold"))
        self.text_label_r1.pack(side="left",  padx=(29,0))
        
        self.text_sub_r1 = ctk.CTkLabel(self.line_frame_3, text="Choose a fun style and download, and share with others", font=("Arial", 18, "italic"))
        self.text_sub_r1.pack(side="left",  padx=(0,0))
        
        # Subheading
        self.end_sentence_1 = ctk.CTkLabel(
            self.scrollable_body,
            text="People are drawn to cartoons for their playful charm and distinctive flair. In a sea of ordinary photos, cartoon-style images stand out, making them perfect for enhancing your personal blog or social media profiles. With Drawli, you can effortlessly transform your photos and videos into vibrant cartoon masterpieces, ensuring your content captures attention and leaves a lasting impression.",
            font=("Arial", 18),
            wraplength=700,
            justify="left"
        )
        self.end_sentence_1.pack(anchor="w", pady=(20, 0), padx=(270, 0))
    
    def tips(self):
         # Q2 - Heading
        self.question2_heading = ctk.CTkLabel(
            self.scrollable_body,
            text="Tips for using Drawli",
            font=("Arial", 30, "bold"),
            wraplength=700,
            justify="left"
            
        )
        self.question2_heading.pack(anchor="w", pady=(30, 0), padx=(270, 0))
        
        # ----- [Tips] ---- - here they are
        
        #TIP 1
        # Create container frame
        self.tip_line_frame_1 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.tip_line_frame_1.pack(anchor="w",pady=(30, 0), padx=(270, 0))
            
        # Colored symbol label
        self.tip_symbol_1 = ctk.CTkLabel(self.tip_line_frame_1, text="✓", font=("Arial", 18), text_color="#3b82f6")
        self.tip_symbol_1.pack(side="left", padx=(25,0))
        
        # Text label
        self.tip_label_1 = ctk.CTkLabel(self.tip_line_frame_1, text="High Quality Images - ", font=("Arial", 18, "bold"))
        self.tip_label_1.pack(side="left",  padx=(29,0))
        
        self.tip_sub_text_1 = ctk.CTkLabel(self.tip_line_frame_1, text="Clear images, for better output", font=("Arial", 18, "italic"))
        self.tip_sub_text_1.pack(side="left",  padx=(0,0))
        
        #TIP 2
        # Create container frame
        self.tip_line_frame_2 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.tip_line_frame_2.pack(anchor="w",pady=(30, 0), padx=(270, 0))
            
        # Colored symbol label
        self.tip_symbol_2 = ctk.CTkLabel(self.tip_line_frame_2, text="✓", font=("Arial", 18), text_color="#3b82f6")
        self.tip_symbol_2.pack(side="left", padx=(25,0))
        
        # Text label
        self.tip_label_2 = ctk.CTkLabel(self.tip_line_frame_2, text="Good Lighting - ", font=("Arial", 18, "bold"))
        self.tip_label_2.pack(side="left",  padx=(29,0))
        
        self.tip_sub_text_2 = ctk.CTkLabel(self.tip_line_frame_2, text="highlights facial features and colors", font=("Arial", 18, "italic"))
        self.tip_sub_text_2.pack(side="left",  padx=(0,0))
        
         #TIP 3
        # Create container frame
        self.tip_line_frame_3 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.tip_line_frame_3.pack(anchor="w",pady=(30, 0), padx=(270, 0))
            
        # Colored symbol label
        self.tip_symbol_3 = ctk.CTkLabel(self.tip_line_frame_3, text="✓", font=("Arial", 18), text_color="#3b82f6")
        self.tip_symbol_3.pack(side="left", padx=(25,0))
        
        # Text label
        self.tip_label_3 = ctk.CTkLabel(self.tip_line_frame_3, text="Clear Voice Instructions - ", font=("Arial", 18, "bold"))
        self.tip_label_3.pack(side="left",  padx=(29,0))
        
        self.tip_sub_text_3 = ctk.CTkLabel(self.tip_line_frame_3, text="Be clear and descriptive when using voice-to-image", font=("Arial", 18, "italic"))
        self.tip_sub_text_3.pack(side="left",  padx=(0,0))
        
        # Subheading
        self.end_sentence_2 = ctk.CTkLabel(
            self.scrollable_body,
            text="Experimentation is essential; the AI's vast capabilities can reveal unexpected and delightful styles when you mix different image types—portraits, landscapes, pets, and group photos—each offering a unique interpretation of 'cartoon-like.'",
            font=("Arial", 18),
            wraplength=700,
            justify="left"
        )
        self.end_sentence_2.pack(anchor="w", pady=(20, 0), padx=(270, 0))
   
   
    def guide(self):
        # Main heading
        self.guide_heading = ctk.CTkLabel(
            self.scrollable_body,
            text="Complete Guide: How to use Drawli",
            font=("Arial", 50, "bold"),
            wraplength=800
        )
        self.guide_heading.pack(anchor="w", padx=(270, 0))      
        
        # ---- guide steps
        #guide 1
        self.sub_heading_1= ctk.CTkLabel(
            self.scrollable_body,
            text="Uploading an Image",
            font=("Arial", 20, "bold")
        )   
        self.sub_heading_1.pack(anchor="w", padx=(270, 0), pady=(20, 0))
        
        
        self.sub_heading_text_1= ctk.CTkLabel(
            self.scrollable_body,
            text='''1. Click on the "Upload Image" area or drag and drop an image file into the designated area. \n2. Supported image formats include PNG, JPG, JPEG, BMP, and GIF.''',
            font=("Arial", 18), justify="left"
        )   
        self.sub_heading_text_1.pack(anchor="w", padx=(290, 0), pady=(20, 0))
        
        #guide 2
        self.sub_heading_2= ctk.CTkLabel(
            self.scrollable_body,
            text="Selecting a Cartoon Style",
            font=("Arial", 20, "bold")
        )   
        self.sub_heading_2.pack(anchor="w", padx=(270, 0), pady=(20, 0))
        
        
        self.sub_heading_text_2= ctk.CTkLabel(
            self.scrollable_body,
            text='''1. After uploading an image, you will see a selection of cartoon styles. \n2. Click on one of the styles to apply it to your uploaded image.''',
            font=("Arial", 18), justify="left"
        )   
        self.sub_heading_text_2.pack(anchor="w", padx=(290, 0), pady=(20, 0))
        
        #guide 3
        self.sub_heading_3= ctk.CTkLabel(
            self.scrollable_body,
            text="Generating a Cartoon Image",
            font=("Arial", 20, "bold")
        )   
        self.sub_heading_3.pack(anchor="w", padx=(270, 0), pady=(20, 0))
        
        
        self.sub_heading_text_3= ctk.CTkLabel(
            self.scrollable_body,
            text='''1. Once you have selected a style, click the "Generate Cartoon" button. \n2. The application will process your image and display the cartoon version.''',
            font=("Arial", 18), justify="left"
        )   
        self.sub_heading_text_3.pack(anchor="w", padx=(290, 0), pady=(20, 0))
        
        #guide 4
        self.sub_heading_4= ctk.CTkLabel(
            self.scrollable_body,
            text="Downloading the Cartoon Image",
            font=("Arial", 20, "bold")
        )   
        self.sub_heading_4.pack(anchor="w", padx=(270, 0), pady=(20, 0))
        
        
        self.sub_heading_text_4= ctk.CTkLabel(
            self.scrollable_body,
            text='''1. After the cartoon image is generated, you will see a "Download Cartoon Image" button.\n2. Click the button to save the cartoon image to your device.''',
            font=("Arial", 18), justify="left"
        )   
        self.sub_heading_text_4.pack(anchor="w", padx=(290, 0), pady=(20, 0))
        
        
        #new added features:
         # Q1 - Features Heading
        self.features_heading = ctk.CTkLabel(
            self.scrollable_body,
            text="New added features",
            font=("Arial", 30, "underline"),
            wraplength=700,
            justify="left"
            
        )
        self.features_heading.pack(anchor="w", pady=(40, 0), padx=(270, 0))
        
        # ----- [New added Features] ---- - here they are
        
        #Feature 1
        # Create container frame
        self.feature_frame_1 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.feature_frame_1.pack(anchor="w",pady=(30, 0), padx=(270, 0))
        
        # Text label
        self.feature_text_label_r1 = ctk.CTkLabel(self.feature_frame_1, text="Cartoonize Image: ", font=("Arial", 18, "bold"))
        self.feature_text_label_r1.pack(side="left",  padx=(15,0))
        
        self.feature_text_sub_r1 = ctk.CTkLabel(self.feature_frame_1, text="Take a picture of yourself using your webcam, we'll convert it to cartoon.", font=("Arial", 18, "italic"))
        self.feature_text_sub_r1.pack(side="left",  padx=(0,0))
        
        #Feature 2
        # Create container frame
        self.feature_frame_2 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.feature_frame_2.pack(anchor="w",pady=(30, 0), padx=(270, 0))
            
        
        # Text label
        self.feature_text_label_r2 = ctk.CTkLabel(self.feature_frame_2, text="Cartoonize Video: ", font=("Arial", 18, "bold"))
        self.feature_text_label_r2.pack(side="left",  padx=(15,0))
        
        self.feature_text_sub_r2 = ctk.CTkLabel(self.feature_frame_2, text="Record a video with your webcam, and we'll turn each frame into a cartoon.", font=("Arial", 18, "italic"))
        self.feature_text_sub_r2.pack(side="left",  padx=(0,0))
        
        #Feature 3
        # Create container frame
        self.feature_frame_3 = ctk.CTkFrame(self.scrollable_body, fg_color="#1A1A1A")
        self.feature_frame_3.pack(anchor="w",pady=(30, 0), padx=(270, 0))
        
        # Text label
        self.feature_text_label_r3 = ctk.CTkLabel(self.feature_frame_3, text="Voice Gen: ", font=("Arial", 18, "bold"))
        self.feature_text_label_r3.pack(side="left",  padx=(15,0))
        
        self.feature_text_sub_r3 = ctk.CTkLabel(self.feature_frame_3, text="Use voice commands to describe your cartoon image, and the we'll generate it.", font=("Arial", 18, "italic"))
        self.feature_text_sub_r3.pack(side="left",  padx=(0,0))
      
      
    def FAQs(self): 
        
        # Main heading
        self.main_heading_FAQS = ctk.CTkLabel(
            self.scrollable_body,
            text="Frequently Asked Questions (FAQs):",
            font=("Arial", 50, "bold"),
            wraplength=800
            
        )
        self.main_heading_FAQS.pack(anchor="w", padx=(270, 0))  
        
        
        # Subheading
        self.FAQs_Questions = ctk.CTkLabel(
            self.scrollable_body,
            text='''Q:What image formats does Drawli support?\nA:Drawli supports the following image formats: PNG, JPG, JPEG, BMP and GIF.\n\nQ:What is the maximum video length for cartoon videos?\nA:Currently, the maximun video length is set to 2 minutes for processing.\n\nQ:How do I troubleshoot if my image doesn't upload?\nA:Ensure that your internet connection is stable and that the image meets the size requirements. If problem persists, try restarting the app.\n\nQ:Can I edit the cartton effects after applying them?\nA:Yes, you can select a different style and regenerate the cartoon image at any time.\n\nQ:Is there a limit to the number of images I can create?\nA:There is no limit to the number of images you can create, however, there is a limit on some features, since it use Co-pilot- there will be a cool down period.\n\n''',
            font=("Arial", 20),
            wraplength=700,
            justify="left"
        )
        self.FAQs_Questions.pack(anchor="w", pady=(20, 0), padx=(290, 0))



    def hide_existing_content(self):
        # Hide all content that should not be displayed after generating the cartoon
        if hasattr(self, "demo_line") and self.demo_line.winfo_exists():
            self.demo_line.pack_forget()
        if hasattr(self, "demo_line_2") and self.demo_line_2.winfo_exists():
            self.demo_line_2.pack_forget()
        if hasattr(self, "demo_line_3") and self.demo_line_3.winfo_exists():
            self.demo_line_3.pack_forget()
        if hasattr(self, "information") and self.information.winfo_exists():
            self.information.pack_forget()
        if hasattr(self, "information_line_heading") and self.information_line_heading.winfo_exists():
            self.information_line_heading.pack_forget()
        if hasattr(self, "question1_heading") and self.question1_heading.winfo_exists():
            self.question1_heading.pack_forget()
        if hasattr(self, "question2_heading") and self.question2_heading.winfo_exists():
            self.question2_heading.pack_forget()
        if hasattr(self, "line_frame_1") and self.line_frame_1.winfo_exists():
            self.line_frame_1.pack_forget()
        if hasattr(self, "line_frame_2") and self.line_frame_2.winfo_exists():
            self.line_frame_2.pack_forget()
        if hasattr(self, "line_frame_3") and self.line_frame_3.winfo_exists():
            self.line_frame_3.pack_forget()
        if hasattr(self, "tip_line_frame_1") and self.tip_line_frame_1.winfo_exists():
            self.tip_line_frame_1.pack_forget()
        if hasattr(self, "tip_line_frame_2") and self.tip_line_frame_2.winfo_exists():
            self.tip_line_frame_2.pack_forget()
        if hasattr(self, "tip_line_frame_3") and self.tip_line_frame_3.winfo_exists():
            self.tip_line_frame_3.pack_forget()
        if hasattr(self, "end_sentence_1") and self.end_sentence_1.winfo_exists():
            self.end_sentence_1.pack_forget()
        if hasattr(self, "end_sentence_2") and self.end_sentence_2.winfo_exists():
            self.end_sentence_2.pack_forget()
        if hasattr(self, "guide_heading") and self.guide_heading.winfo_exists():
            self.guide_heading.pack_forget()
        if hasattr(self, "sub_heading_1") and self.sub_heading_1.winfo_exists():
            self.sub_heading_1.pack_forget()
        if hasattr(self, "sub_heading_2") and self.sub_heading_2.winfo_exists():
            self.sub_heading_2.pack_forget()
        if hasattr(self, "sub_heading_3") and self.sub_heading_3.winfo_exists():
            self.sub_heading_3.pack_forget()
        if hasattr(self, "sub_heading_4") and self.sub_heading_4.winfo_exists():
            self.sub_heading_4.pack_forget()
        if hasattr(self, "sub_heading_text_1") and self.sub_heading_text_1.winfo_exists():
            self.sub_heading_text_1.pack_forget()
        if hasattr(self, "sub_heading_text_2") and self.sub_heading_text_2.winfo_exists():
            self.sub_heading_text_2.pack_forget()
        if hasattr(self, "sub_heading_text_3") and self.sub_heading_text_3.winfo_exists():
            self.sub_heading_text_3.pack_forget()
        if hasattr(self, "sub_heading_text_4") and self.sub_heading_text_4.winfo_exists():
            self.sub_heading_text_4.pack_forget()
        if hasattr(self, "features_heading") and self.features_heading.winfo_exists():
            self.features_heading.pack_forget()
        if hasattr(self, "feature_frame_1") and self.feature_frame_1.winfo_exists():
            self.feature_frame_1.pack_forget()
        if hasattr(self, "feature_frame_2") and self.feature_frame_2.winfo_exists():
            self.feature_frame_2.pack_forget()
        if hasattr(self, "feature_frame_3") and self.feature_frame_3.winfo_exists():
            self.feature_frame_3.pack_forget()
        if hasattr(self, "main_heading_FAQS") and self.main_heading_FAQS.winfo_exists():
            self.main_heading_FAQS.pack_forget()
        if hasattr(self, "FAQs_Questions") and self.FAQs_Questions.winfo_exists():
            self.FAQs_Questions.pack_forget()
        if hasattr(self, "footer_frame") and self.footer_frame.winfo_exists():
            self.footer_frame.pack_forget()
        if hasattr(self, "footer_spacer") and self.footer_spacer.winfo_exists():
            self.footer_spacer.pack_forget()

    def generate_cartoon(self):
        
         # Check if an image is uploaded
        if not hasattr(self, "original_pil_image") or self.original_pil_image is None:
            messagebox.showwarning("No Image", "Please upload an image before generating a cartoon.")
            return
        # Check if a style is selected
        if self.selected_style_index is None or not hasattr(self, "generated_cartoon_image") or self.generated_cartoon_image is None:
            messagebox.showwarning("No Style Selected", "Please select a cartoon style before generating the cartoon.")
            return
        

        # Hide existing content instead of destroying it
        self.hide_existing_content()
        
        # Check if the outer_result_frame already exists and destroy it
        if hasattr(self, "outer_result_frame") and self.outer_result_frame.winfo_exists():
            self.outer_result_frame.destroy()
        # Create a new outer_result_frame
        self.outer_result_frame = ctk.CTkFrame(self.scrollable_body, width=780, height=550, border_color="white", border_width=0)
        self.outer_result_frame.pack(padx=10, pady=(40, 0))
        
        # Prevent frame from shrinking to fit contents
        self.outer_result_frame.pack_propagate(False)
        self.result_title = ctk.CTkLabel(self.outer_result_frame, text="Your Cartoon", font=("Arial", 20, "bold"))
        self.result_title.pack(pady=(20, 10))
        
        if not hasattr(self, "generated_cartoon_image") or self.generated_cartoon_image is None:
            print("Please upload an image and select a style first.")
            return
        
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
        
        # Destroy old line if existed
        if hasattr(self, "result_line") and self.result_line.winfo_exists():
            self.result_line.destroy()
        self.result_line = ctk.CTkFrame(self.scrollable_body, height=2, fg_color="#676767" , width=800)
        self.result_line.pack(padx=20, pady=(90, 30))
        
        self.about()
        
        self.tips()
        
        self.demo_line_2 = ctk.CTkFrame(self.scrollable_body, height=2, fg_color="#676767" , width=800)
        self.demo_line_2.pack(padx=20, pady=(90, 30))
        
        self.guide()
        
        self.demo_line_3 = ctk.CTkFrame(self.scrollable_body, height=2, fg_color="#676767" , width=800)
        self.demo_line_3.pack(padx=20, pady=(90, 30))
        
        self.FAQs()
        
        self.create_footer()

    def create_footer(self):
        mode = ctk.get_appearance_mode()
        if mode == "dark":
            footer_bg = "#374151"
            text_color = "#d1d5db"
        else:
            footer_bg = "#e0e7ff"
            text_color = "#374151"

        # Invisible spacer frame to fill remaining vertical space pushing footer down
        self.footer_spacer = ctk.CTkFrame(self.scrollable_body, fg_color="transparent")
        self.footer_spacer.pack(expand=True, fill="both")  # takes all extra vertical space

        # Footer frame with rounded corners, full width, no vertical padding to avoid gap
        self.footer_frame = ctk.CTkFrame(
            self.scrollable_body,
            fg_color=footer_bg,
            corner_radius=15
        )
        self.footer_frame.pack(fill="x", padx=0, pady=(0, 0))  # no padding below ensures no gap

        footer_text = "© 2025 Drawli. All rights reserved.   |   Follow us on: Facebook  Twitter  Instagram"
        self.footer_label = ctk.CTkLabel(
            self.footer_frame,
            text=footer_text,
            font=("Arial", 14),
            text_color=text_color,
            wraplength=1100,
            justify="center"
        )
        self.footer_label.pack(padx=40, pady=20, anchor="center")



        
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
        image_label.configure(highlightthickness=1, highlightbackground="#3b82f6", bd=1)
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
