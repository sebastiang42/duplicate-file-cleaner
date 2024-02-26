# DUPLICATE FILE CLEANER

This is a simple python app that I put together to help me clean up duplicate files in my pictures folder and on some external hard drives. Could it be polished more? Sure, but in its current state it helped me complete the task much faster than would ahve been otherwise possible (with tens of thousands of files in dozens of directories and sub-directories, and thousands of duplicates found). The program works by searching for any files matching filenames (or matching except with " - Copy" appended to one of the files). Then, for any matches found, a file hash if calculated for each file to ensure that the files are in fact identical. This program WILL NOT find duplicate files whose names do not match. This would involve calculating hashes for ALL files, which was extremely slow for my purposes, so I didn't bother.

## Instructions for use

1. Ensure that you have all required python packages installed (just check the top of *main.py*). Start the app by running the command `python main.py` in a terminal.
2. Using the "Load Directory" button, select the parent folder that you'd like to search for duplicate files. A list of all subdirectories within this folder will appear. By default, all subdirectories within this parent folder will be searched.
3. If you want to ignore duplicates in a specific subdirectory, simply select that subdirectory from the list and click "Ignore Selected Folders". The selected subdirectory(ies) will be added to the list below.
4. Click the "Find Duplicates" button to begin the search. Be patient, it can take some time if there are many files (you can see progress in the terminal from which you launched the app). Once complete, a list of all duplicates will be shown, grouped by their hash and sorted by file size with largest files first (making it easy to prioritize files that are wasting the most space).
5. Select files that you wish to delete, then click "Add to Removal List". The selected files should be added to the far right list.
6. From the far right list, select all files that you would like to delete and press the "Delete Selected Files" button