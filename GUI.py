import tkinter as tk
import Facal_recgnition
from tkinter import filedialog
from tkinter import ttk 
from tkinter import messagebox

no_bitches= """
   ⢘⣾⣾⣿⣾⣽⣯⣼⣿⣿⣴⣽⣿⣽⣭⣿⣿⣿⣿⣿⣧
⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⣰⣯⣾⣿⣿⡼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿
⠀⠀⠛⠛⠋⠁⣠⡼⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁
⠀⠀⠀⠤⣶⣾⣿⣿⣿⣦⡈⠉⠉⠉⠙⠻⣿⣿⣿⣿⣿⠿⠁⠀
⠀⠀⠀⠀⠈⠟⠻⢛⣿⣿⣿⣷⣶⣦⣄⠀⠸⣿⣿⣿⠗⠀⠀⠀
⠀⠀⠀⠀⠀⣼⠀⠄⣿⡿⠋⣉⠈⠙⢿⣿⣦⣿⠏⡠⠂⠀⠀⠀
⠀⠀⠀⠀⢰⡌⠀⢠⠏⠇⢸⡇⠐⠀⡄⣿⣿⣃⠈⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⣻⣿⢫⢻⡆⡀⠁⠀⢈⣾⣿⠏⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣿⣻⣷⣾⣿⣿⣷⢾⣽⢭⣍⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣼⣿⣿⣿⣿⡿⠈⣹⣾⣿⡞⠐⠁⠀⠀⠀⠁⠀⠀⠀
⠀⠀⠀⠨⣟⣿⢟⣯⣶⣿⣆⣘⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡆⠀⠐⠶⠮⡹⣸⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""



def browse_input_files():
    files = filedialog.askopenfilenames(
        title="Select Input Files",
        filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
    )
    if files:
        input_paths_text.delete(1.0, tk.END)
        input_paths_text.insert(tk.END, "\n".join(files))
        
        for item in table.get_children():
            table.delete(item)
            
        for file in files:
            filename = file.split('/')[-1]  
            if '\\' in file:  
                filename = file.split('\\')[-1]
            table.insert('', tk.END, values=(filename, 'Not Cropped'))

def browse_output_location():
    folder = filedialog.askdirectory(title="Select Output Location")
    if folder:
        output_path.set(folder) 
def save_image():
    return "a"

def crop_all_images():
    # Get all file paths from the text widget
    file_paths = input_paths_text.get(1.0, tk.END).strip().split('\n')
    output_directory = output_path.get()
    
    if not output_directory:
        tk.messagebox.showerror("Error", "Please select an output directory first")
        return
    
    if not file_paths or file_paths[0] == '':
        tk.messagebox.showerror("Error", "Please select input files first")
        return

    for file_path in file_paths:
        if file_path:  # Skip empty strings
            try:
                # Crop the image
                cropped_image = Facal_recgnition.crop_image(file_path)
                if cropped_image:
                    # Get filename from path
                    filename = file_path.split('/')[-1]
                    if '\\' in file_path:
                        filename = file_path.split('\\')[-1]
                    
                    # Save to output directory
                    save_path = f"{output_directory}/{filename}"
                    cropped_image.save(save_path)
                    
                    # Update status in table
                    for item in table.get_children():
                        if table.item(item)['values'][0] == filename:
                            table.item(item, values=(filename, 'Cropped'))
                            
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

root = tk.Tk()
root.title("Face Recognition System")
root.geometry("2000x1000")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)

root.rowconfigure(4, weight=1)

title = tk.Label(root, text="Face Recognition System", font=("times new roman", 35, "bold"), bg="white", fg="blue")
title.grid(row=0, column=0, columnspan=3, pady=30)


input_paths = tk.StringVar()
Imput_label = tk.Label(root, text="Please put input files here")
Imput_label.grid(row=1, column=0)
input_browse = tk.Button(root, text="Browse Input Files", command=browse_input_files)
input_browse.grid(row=1, column=1)
input_paths_text = tk.Text(root, height=5, width=40)
input_paths_text.grid(row=1, column=2, padx=10, pady=5)


output_label = tk.Label(root, text="Show output text")
output_label.grid(row=2, column=0)
output_path = tk.StringVar()
output_browse = tk.Button(root, text="Select Output Location", command=browse_output_location)
output_browse.grid(row=2, column=1)
output_path_entry = tk.Entry(root, textvariable=output_path, width=40)
output_path_entry.grid(row=2, column=2, padx=10, pady=5)


table_frame = ttk.Frame(root)
table_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

columns = ('Image Name', 'Status')
table = ttk.Treeview(table_frame, columns=columns, show='headings')


table.heading('Image Name', text='Image Name')
table.heading('Status', text='Status')


table.column('Image Name', width=300)
table.column('Status', width=100)


scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
table.configure(yscrollcommand=scrollbar.set)


table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

crop_button = tk.Button(root, text="Crop All", command=crop_all_images)
crop_button.grid(row=4, column=1, pady=20)

root.mainloop()