import pytesseract
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import os
import fitz
import subprocess
import urllib.request
import tempfile
import sys

tesseract_path = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Check for dependency: tesseract
def install_application():
    try:
        tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
        # temporary file to download the installer
        temp_dir = tempfile.mkdtemp()
        tesseract_installer_path = os.path.join(temp_dir, 'tesseract.exe')
        # Download the installer
        urllib.request.urlretrieve(tesseract_url, tesseract_installer_path)
        # tesseract_frozen_env_exe = os.path.join(sys._MEIPASS, 'tesseract.exe')
        # Run the application installer
        subprocess.run(tesseract_installer_path, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        tk.messagebox.showerror(title="Error", message="An error occured. The installation was interrupted. Exiting.")
        sys.exit()
    except OSError as e:
        tk.messagebox.showerror(title="Error", message=e + " Exiting.")
        sys.exit()
    finally:
         # Clean up
        if os.path.exists(temp_dir):
            try:
                os.remove(tesseract_installer_path)
                os.rmdir(temp_dir)
            except OSError:
                pass

    #subprocess.run(tesseract_frozen_env_exe)

# Check if the application is installed
if not os.path.exists(tesseract_path):
    # Ask for the user's permission to install tesseract which is a dependency
    response = tk.messagebox.askokcancel("Dependency", "This app requires Tesseract OCR to be installed in its default directory. Would you like to Proceed with installing Tesseract OCR?")
    if response:
        install_application()
    else:
        tk.messagebox.showinfo("Dependency declined", "Unable to run application. Exiting.")
        sys.exit()


# Initializing pytesseract path
# Windows project release installed from https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Logic for frozen vs python environment
if getattr(sys, 'frozen', False):
    # Running in a frozen, compiled, bundled environment like in a PyInstaller bundle
    # path to the bundled icon file
    icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
else:
    # Running in a normal Python environment
    icon_path = 'icon.ico'



def read_img_text():     
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.pdf")])
    if file_path:
        file_ext = os.path.splitext(file_path)[1]
        if file_ext == ".pdf":
            pdf_file = fitz.open(file_path)
            # Initialize text result
            text_result = ""
            for page_number in range(len(pdf_file)):
                page = pdf_file.load_page(page_number)
                page_image = page.get_pixmap()
                print(page_image)

                # Convert pixmap to PIL Image for pytesseract compatibility
                page_image = Image.frombytes("RGB", [page_image.width, page_image.height], page_image.samples)
                # Perform ocr
                this_page_txt = pytesseract.image_to_string(page_image)
                print(this_page_txt)
                # Append to text_result
                text_result += this_page_txt            
        
        else:
            print(file_path)            
            text_result = pytesseract.image_to_string(file_path)  

        # Clearing text box and populating it with text_result
        text_box.delete(1.0, tk.END) 
        text_box.insert(tk.END, text_result)
       
                    
    
root = tk.Tk()
root.title("Image to text: OCR")
root.iconbitmap(icon_path)

# Create the upload button
upload_button = tk.Button(root, text="Upload Image", command=read_img_text)
upload_button.pack(pady=10)

# Creating the text box
text_box = tk.Text(root, width=50, height=30)
text_box.pack(pady=10)

root.mainloop()


