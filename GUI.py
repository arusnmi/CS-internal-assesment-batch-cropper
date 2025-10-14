import tkinter as tk
import Facal_recgnition
from tkinter import filedialog
from tkinter import ttk 
from tkinter import messagebox


file_paths_store = []

def browse_input_files():
    global file_paths_store
    files = filedialog.askopenfilenames(
        title="Select Input Files",
        filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
    )
    if files:
        file_paths_store = list(files)  
        
        for item in table.get_children():
            table.delete(item)
            
        for file in files:
            filename = file.split('/')[-1]  
            if '\\' in file:  
                filename = file.split('\\')[-1]
            table.insert('', tk.END, values=(filename, 'File loaded'))

def browse_output_location():
    folder = filedialog.askdirectory(title="Select Output Location")
    if folder:
        output_path.set(folder) 

def crop_all_images():
    output_directory = output_path.get()
    
    if not output_directory:
        tk.messagebox.showerror("Error", "Please select an output directory first")
        return
    
    if not file_paths_store:
        tk.messagebox.showerror("Error", "Please select input files first")
        return

    for file_path in file_paths_store:
        try:
            
            cropped_image = Facal_recgnition.crop_image(file_path)
            if cropped_image:

                filename = file_path.split('/')[-1]
                if '\\' in file_path:
                    filename = file_path.split('\\')[-1]
                

                save_path = f"{output_directory}/{filename}"
                cropped_image.save(save_path)
                

                for item in table.get_children():
                    if table.item(item)['values'][0] == filename:
                        table.item(item, values=(filename, '✓'))
                        
        except Exception as e:
            filename = file_path.split('/')[-1]
            if '\\' in file_path:
                filename = file_path.split('\\')[-1]
            for item in table.get_children():
                if table.item(item)['values'][0] == filename:
                    table.item(item, values=(filename, '✘'))
            print(f"Error processing {file_path}: {str(e)}")

root = tk.Tk()
root.title("Face Recognition System")
root.resizable(0,0)
root.geometry("600x480")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)


Imput_label = tk.Label(root, text="Please put input files here")
Imput_label.grid(row=1, column=0)
input_browse = tk.Button(root, text="Browse Input Files", command=browse_input_files)
input_browse.grid(row=1, column=1, columnspan=2, sticky='ew', padx=10)


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

table.column('Image Name', width=400)
table.column('Status', width=100)

scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
table.configure(yscrollcommand=scrollbar.set)

table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

crop_button = tk.Button(root, text="Crop All", command=crop_all_images)
crop_button.grid(row=4, column=1, pady=20)

root.mainloop()