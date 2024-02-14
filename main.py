import os
import hashlib
from collections import defaultdict
from tqdm import tqdm

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
                variations = ['- Copy', '- Copy (', '- Copy ', ' - Copy (1)']
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

def calculate_duplicate_size(hash_duplicates):
    total_size = 0
    for file_paths in hash_duplicates.values():
        if len(file_paths) > 1:
            file_size = get_file_size(file_paths[0])  # Use the size of the first file as they are duplicates
            total_size += file_size * (len(file_paths) - 1)  # Add size for each additional duplicate

    return total_size

if __name__ == "__main__":
    # directory_path = r'C:/Users/sebas/Pictures/Seb Phone Pictures'
    directory_path = r'C:/Users/sebas/Pictures'

    # duplicates = find_duplicate_files_deep(directory_path)
    hash_duplicates, folders_with_duplicates = find_duplicate_files_fast(directory_path)

    if hash_duplicates:
        print("Duplicate Files:")
        for file_hash, file_paths in hash_duplicates.items():
            print(f"Hash: {file_hash}")
            for file_path in file_paths:
                print(f"  - {file_path}")
            print("\n")
    else:
        print("No duplicate files found.")

    if folders_with_duplicates:
        print("Folders with Duplicates:")
        for folder, files in folders_with_duplicates.items():
            print(f"Folder: {folder}")
            for file_path in files:
                print(f"  - {file_path}")
            print("\n")
    else:
        print("No folders with duplicates found.")
