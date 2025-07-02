import tkinter as tk
import os
from tkinter import filedialog, messagebox

def trim_and_replace_multiple(file_path, output_path):
    # Hardcoded strings
    start_string = '</th></tr></thead><tbody><tr><td>0</td><td></td><td></td></tr><tr><td>'
    end_string = '</td></tr></tbody></table></div></div></div>'
    replacements = [
        ('</td><td>80</td><td>', '\t'),
        ('</td></tr><tr><td>', '\n')
    ]

    try:
        with open(file_path, 'r') as file:
            content = file.read()

        start_index = content.find(start_string)
        end_index = content.find(end_string)

        if start_index != -1 and end_index != -1 and end_index > start_index:
            trimmed_content = content[start_index + len(start_string):end_index]

            for find_str, replace_str in replacements:
                trimmed_content = trimmed_content.replace(find_str, replace_str)

            with open(output_path, 'w') as file:
                file.write(trimmed_content)

            messagebox.showinfo("Success", f"Data cleaned and saved to '{output_path}'")
        else:
            messagebox.showerror("Error", "Start or end string not found, or in incorrect order.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_file():
    filename = filedialog.askopenfilename()
    entry_file.delete(0, tk.END)
    entry_file.insert(0, filename)

def browse_save_file():
    default_filename = os.path.join(os.path.expanduser("~"), "Desktop", "output.txt")
    filename = filedialog.asksaveasfilename(
        initialfile="output.txt",
        initialdir=os.path.dirname(default_filename),
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if filename:
        entry_save_as.delete(0, tk.END)
        entry_save_as.insert(0, filename)

def process_file():
    file_path = entry_file.get()
    output_path = entry_save_as.get()
    if not file_path or not output_path:
        messagebox.showerror("Error", "Please select both input and output files.")
        return
    trim_and_replace_multiple(file_path, output_path)

def show_instructions():
    instructions_window = tk.Toplevel(root)
    instructions_window.title("Instructions")
    instructions_window.geometry("500x300")

    text = tk.Text(instructions_window, wrap="word")
    text.insert("1.0",
                "Instructions:\n\n"
                "Download the rtings page with these parameters: \n\n"
                "Average response ON\n"
                "Tests OFF\n"
                "Target OFF\n\n"
                "Make sure to select the \"webpage - Complete\" option when saving.\n"
                "This ensures the script that fetches the data is ran the data is inserted locally into your html file.\n"
                "Once you have your output data you may delete the original files you downloaded."
                )
    text.config(state="disabled")
    text.pack(expand=True, fill="both", padx=10, pady=10)


# GUI setup
root = tk.Tk()
root.title("RTings Data Extractor")

tk.Label(root, text="Input File:").grid(row=0, column=0, sticky="e")
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

tk.Label(root, text="Output File:").grid(row=1, column=0, sticky="e")
entry_save_as = tk.Entry(root, width=50)
entry_save_as.grid(row=1, column=1)
tk.Button(root, text="Save As", command=browse_save_file).grid(row=1, column=2)
entry_save_as.insert(0, os.path.join(os.path.expanduser("~"), "Desktop", "output.txt"))

tk.Button(root, text="Instructions", command=show_instructions).grid(row=3, column=1, pady=5)

tk.Button(root, text="Process File", command=process_file).grid(row=2, column=1, pady=10)

root.mainloop()
