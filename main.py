import tkinter as tk
import os
import tempfile
import asyncio
import re
from urllib.parse import urlparse
import sys
import subprocess

def ensure_playwright_browser():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            _ = p.chromium.launch()
    except Exception:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])

ensure_playwright_browser()

from playwright.async_api import async_playwright

from tkinter import filedialog, messagebox
from bs4 import BeautifulSoup


# Async function to save rendered HTML with local resource links
async def save_html_with_local_links_only(url: str, output_file: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    resource_tags = [
        ("link", "href"), ("script", "src"), ("img", "src"),
        ("iframe", "src"), ("source", "src"), ("video", "src"),
        ("audio", "src"), ("embed", "src"), ("object", "data")
    ]

    for tag, attr in resource_tags:
        for element in soup.find_all(tag):
            if element.has_attr(attr):
                parsed_url = urlparse(element[attr])
                if parsed_url.scheme in ["http", "https"]:
                    path = parsed_url.path.lstrip("/") or "index"
                    element[attr] = path

    for element in soup.find_all(style=True):
        style = element["style"]
        updated_style = style
        for match in re.findall(r'url\\(([^)]+)\\)', style):
            cleaned_url = match.strip("'\"")
            parsed_url = urlparse(cleaned_url)
            if parsed_url.scheme in ["http", "https"]:
                path = parsed_url.path.lstrip("/") or "index"
                updated_style = updated_style.replace(match, path)
        element["style"] = updated_style

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(str(soup))

# Wrapper to run async function from sync context
def download_html_from_url(url):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8')
    asyncio.run(save_html_with_local_links_only(url, temp_file.name))
    return temp_file.name

# Trimming and replacement logic
def trim_and_replace_multiple(file_path, output_path):
    start_string = '</th></tr></thead><tbody><tr><td>0</td><td></td><td></td></tr><tr><td>'
    end_string = '</td></tr></tbody></table></div></div></div>'
    replacements = [
        ('</td><td>80</td><td>', '\t'),
        ('</td></tr><tr><td>', '\n')
    ]

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        start_index = content.find(start_string)
        end_index = content.find(end_string)

        if start_index != -1 and end_index != -1 and end_index > start_index:
            trimmed_content = content[start_index + len(start_string):end_index]

            for find_str, replace_str in replacements:
                trimmed_content = trimmed_content.replace(find_str, replace_str)

            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(trimmed_content)

            messagebox.showinfo("Success", f"Data cleaned and saved to '{output_path}'")
        else:
            messagebox.showerror("Error", "Start or end string not found, or in incorrect order.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI logic
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
    url = entry_url.get()

    if not output_path:
        messagebox.showerror("Error", "Please specify an output file.")
        return

    try:
        if url:

            if "?disabled=tests" in url:
                url = url[:url.find("?disabled=tests")]
            url = url + "?disabled=tests:0:,0:1:"

            downloaded_file = download_html_from_url(url)
            trim_and_replace_multiple(downloaded_file, output_path)
            os.remove(downloaded_file)
        elif file_path:
            trim_and_replace_multiple(file_path, output_path)
        else:
            messagebox.showerror("Error", "Please provide either a file or a URL.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_instructions():
    instructions_window = tk.Toplevel(root)
    instructions_window.title("Instructions")
    instructions_window.geometry("500x300")

    text = tk.Text(instructions_window, wrap="word")
    text.insert("1.0",
                "Instructions:\n\n"
                "Either input the URL of the rtings graph directly\n\n"
                "OR\n\n"
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

tk.Label(root, text="or URL:").grid(row=1, column=0, sticky="e")
entry_url = tk.Entry(root, width=50)
entry_url.grid(row=1, column=1)

tk.Label(root, text="Output File:").grid(row=2, column=0, sticky="e")
entry_save_as = tk.Entry(root, width=50)
entry_save_as.grid(row=2, column=1)
tk.Button(root, text="Save As", command=browse_save_file).grid(row=2, column=2)
entry_save_as.insert(0, os.path.join(os.path.expanduser("~"), "Desktop", "output.txt"))

tk.Button(root, text="Process File", command=process_file).grid(row=3, column=1, pady=10)
tk.Button(root, text="Instructions", command=show_instructions).grid(row=4, column=1, pady=5)

root.mainloop()
