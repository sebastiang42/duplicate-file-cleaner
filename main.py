import os
import hashlib
from collections import defaultdict
from tqdm import tqdm
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_file_size(file_path):
    return os.path.getsize(file_path)

def find_duplicate_files(directory):
    file_info_dict = defaultdict(list)
    duplicate_files = defaultdict(list)
    folders_with_duplicates = defaultdict(set)

    # Count the total number of files
    total_files = sum([len(files) for _, _, files in os.walk(directory)])

    with tqdm(total=total_files, desc="Searching for Duplicates") as pbar:
        for foldername, subfolders, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                base_name, extension = os.path.splitext(filename)

                # Check for variations in filenames (e.g., ' - Copy')
                variations = [' - Copy', ' - Copy - Copy', '- Copy ', ' - Copy (1)']
                for variation in variations:
                    if variation in base_name:
                        base_name = base_name.replace(variation, '')

                file_info = (base_name, extension)
                file_info_dict[file_info].append(file_path)

                if len(file_info_dict[file_info]) > 1:
                    duplicate_files[file_info] = file_info_dict[file_info]
                    folders_with_duplicates[foldername].update(file_info_dict[file_info])

                pbar.update(1)  # Update progress bar

    # Now, check file content only for files with the same base name and extension
    hash_duplicates = defaultdict(list)
    with tqdm(total=len(duplicate_files), desc="Calculating Hashes") as pbar:
        for file_info, file_paths in duplicate_files.items():
            if len(file_paths) > 1:
                for file_path in file_paths:
                    file_hash = get_file_hash(file_path)
                    hash_duplicates[file_hash].append(file_path)
                    pbar.update(1)

    return hash_duplicates, folders_with_duplicates

class DuplicateFileViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("Duplicate File Viewer")

        self.directory_path = tk.StringVar()
        self.duplicates_listbox = tk.Listbox(self.master, selectmode=tk.EXTENDED)
        self.duplicates_listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        # self.duplicates_listbox.bind("<<ListboxSelect>>", self.show_selected_files)

        self.load_button = tk.Button(self.master, text="Load Directory", command=self.load_directory)
        self.load_button.pack(pady=5)

        self.total_size_label = tk.Label(self.master, text="Total Size of Duplicates: ")
        self.total_size_label.pack(pady=5)

        self.removable_files_listbox = tk.Listbox(self.master, selectmode=tk.EXTENDED)
        self.removable_files_listbox.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.add_to_removal_button = tk.Button(self.master, text="Add to Removal List", command=self.add_to_removal_list)
        self.add_to_removal_button.pack(pady=5)

        self.remove_from_removal_button = tk.Button(self.master, text="Remove from Removal List", command=self.remove_from_removal_list)
        self.remove_from_removal_button.pack(pady=5)

        self.delete_files_button = tk.Button(self.master, text="Delete Selected Files", command=self.delete_selected_files)
        self.delete_files_button.pack(pady=5)
    
    def load_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.directory_path.set(directory_path)
            hash_duplicates, _ = find_duplicate_files(directory_path)

            self.duplicates_listbox.delete(0, tk.END)

            # Create a list to store entries with file size for sorting
            entries_with_size = []

            for file_hash, file_paths in hash_duplicates.items():
                if len(file_paths) > 1:
                    total_size_per_hash = 0
                    for file_path in file_paths:
                        total_size_per_hash += get_file_size(file_path)

                    entries_with_size.append((total_size_per_hash, f"Hash: {file_hash}", file_paths))

            # Sort the list by file size in descending order
            entries_with_size.sort(reverse=True, key=lambda x: x[0])

            total_size = 0

            for entry in entries_with_size:
                total_size_per_hash, header, file_paths = entry
                self.duplicates_listbox.insert(tk.END, f"{header} - Size: {total_size_per_hash / (1024**2):.2f} MB")
                for file_path in file_paths:
                    self.duplicates_listbox.insert(tk.END, f"  - {file_path} - Size: {total_size_per_hash / (len(file_paths) * 1024**2):.2f} MB")
                self.duplicates_listbox.insert(tk.END, "\n")
                total_size += total_size_per_hash

            self.total_size_label.config(text=f"Total Size of Duplicates: {total_size / (1024**2):.2f} MB")

    def show_selected_files(self, event):
        selected_index = self.duplicates_listbox.curselection()
        if selected_index:
            selected_text = self.duplicates_listbox.get(selected_index)
            tk.messagebox.showinfo("Selected Files", selected_text)

    def add_to_removal_list(self):
        selected_indices = self.duplicates_listbox.curselection()
        for index in selected_indices:
            file_path = self.duplicates_listbox.get(index)
            file_path = os.path.normpath(file_path)  # Normalize path
            file_path = file_path.lstrip(" -")  # Remove leading space and hyphen
            self.removable_files_listbox.insert(tk.END, os.path.normpath(file_path))

    def remove_from_removal_list(self):
        selected_indices = self.removable_files_listbox.curselection()
        for index in selected_indices:
            self.removable_files_listbox.delete(index)

    def delete_selected_files(self):
        selected_indices = self.removable_files_listbox.curselection()

        if not selected_indices:
            tk.messagebox.showinfo("No Files Selected", "Please select files to delete.")
            return

        confirmation = tk.messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected files?")
        if confirmation:
            for index in selected_indices:
                file_path = self.removable_files_listbox.get(index)
                try:
                    os.remove(file_path)
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Error deleting file: {str(e)}")

            tk.messagebox.showinfo("Deletion Complete", "Selected files have been deleted.")
            self.removable_files_listbox.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFileViewer(root)
    root.mainloop()
