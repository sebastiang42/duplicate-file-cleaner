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

def find_duplicate_files(directory, ignored_subdirectories):
    file_info_dict = defaultdict(list)
    duplicate_files = defaultdict(list)
    folders_with_duplicates = defaultdict(set)

    # Count the total number of files
    total_files = sum([len(files) for _, _, files in os.walk(directory)])

    with tqdm(total=total_files, desc="Searching for Duplicates") as pbar:
        for foldername, subfolders, filenames in os.walk(directory):
            # Convert foldername to a relative path
            relative_foldername = os.path.relpath(foldername, directory)

            # Skip ignored subdirectories and their contents
            if relative_foldername in ignored_subdirectories:
                pbar.update(len(filenames))
                continue

            for filename in filenames:
                file_path = os.path.join(relative_foldername, filename)
                full_file_path = os.path.join(directory, file_path)  # Get the full file path

                base_name, extension = os.path.splitext(filename)

                # Check for variations in filenames (e.g., ' - Copy')
                variations = [' - Copy', ' - Copy - Copy', '- Copy ', ' - Copy (1)']
                for variation in variations:
                    if variation in base_name:
                        base_name = base_name.replace(variation, '')

                file_info = (base_name, extension)
                file_info_dict[file_info].append(full_file_path)

                if len(file_info_dict[file_info]) > 1:
                    duplicate_files[file_info] = file_info_dict[file_info]
                    folders_with_duplicates[relative_foldername].update(file_info_dict[file_info])

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

        # Set default font size
        default_font = ("Helvetica", 12)
        default_listbox_font = ("Helvetica", 10)

        # Column 0
        self.load_button = tk.Button(self.master, text="Load Directory", command=self.load_directory, font=default_font)
        self.load_button.grid(row=0, column=0, pady=10, padx=10, sticky=tk.NS)

        self.directory_path_label = tk.Label(self.master, text="Selected Directory: None", font=default_font, wraplength=300)
        self.directory_path_label.grid(row=1, column=0, pady=5, padx=10, sticky=tk.NSEW)

        self.subdirectories_label = tk.Label(self.master, text="Subdirectories to be Searched:", font=default_font)
        self.subdirectories_label.grid(row=2, column=0, pady=5, padx=10, sticky=tk.S)

        # Create a horizontal scrollbar for subdirectories_listbox
        subdirectories_xscrollbar = tk.Scrollbar(self.master, orient=tk.HORIZONTAL)
        subdirectories_xscrollbar.grid(row=4, column=0, padx=10, sticky=tk.W + tk.E + tk.N)

        self.subdirectories_listbox = tk.Listbox(self.master, selectmode=tk.EXTENDED, font=default_listbox_font, width=40, height=20)
        self.subdirectories_listbox.grid(row=3, column=0, padx=10, sticky=tk.NSEW)
        subdirectories_xscrollbar.config(command=self.subdirectories_listbox.xview)

        self.ignore_folders_button = tk.Button(self.master, text="Ignore Selected Folders", command=self.ignore_selected_folders, font=default_font)
        self.ignore_folders_button.grid(row=5, column=0, pady=10, padx=10, sticky=tk.N)

        self.subdirectories_ignored_label = tk.Label(self.master, text="Subdirectories to be Ignored:", font=default_font)
        self.subdirectories_ignored_label.grid(row=6, column=0, pady=5, padx=10, sticky=tk.S)

        # Create a horizontal scrollbar for ignore_folders_listbox
        ignore_folders_xscrollbar = tk.Scrollbar(self.master, orient=tk.HORIZONTAL)
        ignore_folders_xscrollbar.grid(row=8, column=0, padx=10, sticky=tk.W + tk.E + tk.N)

        self.ignore_folders_listbox = tk.Listbox(self.master, selectmode=tk.EXTENDED, font=default_listbox_font, width=40, height=20)
        self.ignore_folders_listbox.grid(row=7, column=0, padx=10, sticky=tk.NSEW)
        ignore_folders_xscrollbar.config(command=self.ignore_folders_listbox.xview)

        self.remove_ignore_folders_button = tk.Button(self.master, text="Remove Selected Folders From Ignore List", command=self.remove_ignored_folders, font=default_font)
        self.remove_ignore_folders_button.grid(row=9, column=0, pady=10, padx=10, sticky=tk.N)

        # Column 1 + 2
        self.find_duplicates_button = tk.Button(self.master, text="Find Duplicates", command=self.find_duplicates, font=default_font)
        self.find_duplicates_button.grid(row=0, column=1, pady=10, padx=10, sticky=tk.NS)

        self.add_to_removal_button = tk.Button(self.master, text="Add to Removal List", command=self.add_to_removal_list, font=default_font)
        self.add_to_removal_button.grid(row=0, column=2, pady=10, padx=10, sticky=tk.NS)

        self.total_size_label = tk.Label(self.master, text="Total Size of Duplicates: ", font=default_font)
        self.total_size_label.grid(row=1, column=1, columnspan=2, pady=5, padx=10, sticky=tk.NSEW)

        self.duplicates_label = tk.Label(self.master, text="Duplicate Files Found: ", font=default_font)
        self.duplicates_label.grid(row=2, column=1, columnspan=2, pady=5, padx=10, sticky=tk.S)

        # Create a horizontal scrollbar for duplicates_listbox
        duplicates_xscrollbar = tk.Scrollbar(self.master, orient=tk.HORIZONTAL)
        duplicates_xscrollbar.grid(row=9, column=1, columnspan=2, padx=10, sticky=tk.W + tk.E + tk.N)

        self.duplicates_listbox = tk.Listbox(self.master, selectmode=tk.EXTENDED, font=default_listbox_font, width=85, xscrollcommand=duplicates_xscrollbar.set)
        self.duplicates_listbox.grid(row=3, column=1, rowspan=6, columnspan=2, padx=10, sticky=tk.NSEW)
        duplicates_xscrollbar.config(command=self.duplicates_listbox.xview)

        # Column 3
        self.remove_from_removal_button = tk.Button(self.master, text="Remove from Removal List", command=self.remove_from_removal_list, font=default_font)
        self.remove_from_removal_button.grid(row=1, column=3, pady=10, padx=10, sticky=tk.N)

        self.file_removal_label = tk.Label(self.master, text="Files to be Removed:", font=default_font)
        self.file_removal_label.grid(row=2, column=3, pady=5, padx=10, sticky=tk.S)

        # Create a horizontal scrollbar for removable_files_listbox
        removable_files_xscrollbar = tk.Scrollbar(self.master, orient=tk.HORIZONTAL)
        removable_files_xscrollbar.grid(row=9, column=3, padx=10, sticky=tk.W + tk.E + tk.N)

        self.removable_files_listbox = tk.Listbox(self.master, selectmode=tk.EXTENDED, font=default_listbox_font, width=85)
        self.removable_files_listbox.grid(row=3, column=3, rowspan=6, padx=10, sticky=tk.NSEW)
        removable_files_xscrollbar.config(command=self.removable_files_listbox.xview)

        # Column 3
        self.delete_files_button = tk.Button(self.master, text="Delete Selected Files", command=self.delete_selected_files, font=default_font)
        self.delete_files_button.grid(row=0, column=3, pady=10, padx=10, sticky=tk.NS)
    
    def ignore_selected_folders(self):
        selected_indices = self.subdirectories_listbox.curselection()
        for index in selected_indices[::-1]:
            folder_name = self.subdirectories_listbox.get(index)
            self.ignore_folders_listbox.insert(tk.END, folder_name)
            self.subdirectories_listbox.delete(index)
    
    def remove_ignored_folders(self):
        selected_indices = self.ignore_folders_listbox.curselection()
        for index in selected_indices[::-1]:
            folder_name = self.ignore_folders_listbox.get(index)
            self.subdirectories_listbox.insert(tk.END, folder_name)
            self.ignore_folders_listbox.delete(index)
    
    def find_duplicates(self):
        directory_path = self.directory_path.get()
        if not directory_path:
            messagebox.showwarning("Warning", "Please select a directory first.")
            return

        # Get a list of subdirectories to be ignored
        ignored_subdirectories = [self.ignore_folders_listbox.get(index) for index in range(self.ignore_folders_listbox.size())]

        # Use the find_duplicate_files function with the ignored_subdirectories parameter
        hash_duplicates, _ = find_duplicate_files(directory_path, ignored_subdirectories)

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
            total_size += total_size_per_hash * (len(file_paths) - 1) / len(file_paths)

        total_duplicates = sum((len(entry[2]) - 1) for entry in entries_with_size if len(entry[2]) > 1)
        self.duplicates_label.config(text=f"Duplicate Files Found: {total_duplicates}")
        self.total_size_label.config(text=f"Total Size of Duplicates: {total_size / (1024**2):.2f} MB")
    
    def load_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.directory_path.set(directory_path)
            self.directory_path_label.config(text=f"Selected Directory: {directory_path}")

            # Populate subdirectories list
            self.subdirectories_listbox.delete(0, tk.END)
            subdirectories = [os.path.relpath(os.path.join(dp, dn), directory_path) for dp, dns, _ in os.walk(directory_path) for dn in dns]
            for subdir in subdirectories:
                self.subdirectories_listbox.insert(tk.END, subdir)
            
            self.total_size_label.config(text="Total Size of Duplicates: ")  # Reset total size label
            self.duplicates_listbox.delete(0, tk.END)
            self.removable_files_listbox.delete(0, tk.END)

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
            file_path_end = file_path.find(" - Size: ")
            self.removable_files_listbox.insert(tk.END, os.path.normpath(file_path[:file_path_end]))

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
            # Create a list to store files to be deleted
            files_to_delete = []

            for index in selected_indices:
                file_path = self.removable_files_listbox.get(index)
                files_to_delete.append(file_path)

            # Remove selected files from the removal list
            for file_path in files_to_delete:
                self.removable_files_listbox.delete(self.removable_files_listbox.get(0, tk.END).index(file_path))

                try:
                    os.remove(file_path)
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Error deleting file: {str(e)}")

            tk.messagebox.showinfo("Deletion Complete", "Selected files have been deleted.")

if __name__ == "__main__":
    root = tk.Tk()

    # Set the initial window size
    root.geometry("1600x1080")

    app = DuplicateFileViewer(root)
    root.mainloop()
