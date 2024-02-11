import os
import hashlib
from collections import defaultdict

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicate_files(directory):
    file_hash_dict = {}
    duplicate_files = {}

    for foldername, subfolders, filenames in os.walk(directory):
        print(foldername)
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            file_hash = get_file_hash(file_path)

            if file_hash in file_hash_dict:
                duplicate_files.setdefault(file_hash, []).append(file_path)
            else:
                file_hash_dict[file_hash] = file_path

    return {k: v for k, v in duplicate_files.items() if len(v) > 1}

def find_duplicate_files(directory):
    file_hash_dict = defaultdict(list)
    duplicate_files = defaultdict(list)

    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            file_hash = get_file_hash(file_path)

            file_hash_dict[file_hash].append(file_path)

            if len(file_hash_dict[file_hash]) > 1:
                duplicate_files[file_hash] = file_hash_dict[file_hash]

    return {k: v for k, v in duplicate_files.items() if len(v) > 1}

if __name__ == "__main__":
    directory_path = r'C:/Users/sebas/Pictures/Seb Phone Pictures/test'

    duplicates = find_duplicate_files(directory_path)

    if duplicates:
        print("Duplicate Files:")
        for file_hash, file_paths in duplicates.items():
            print(f"Hash: {file_hash}")
            for file_path in file_paths:
                print(f"  - {file_path}")
            print("\n")
    else:
        print("No duplicate files found.")
