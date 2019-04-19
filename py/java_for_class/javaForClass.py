from pathlib import Path
from sys import argv
import os
from typing import Callable

folder_1 = argv[1]
folder_1_suffix = argv[2]
folder_2 = argv[3]
folder_2_suffix = argv[4]


def files_of_type_in_dir_r(directory: str, filter_strategy: Callable=lambda x: x):
    """
    Return a list of Path objects representing all files in @directory recursively. Files are filtered by @filter_strategy.
    :param directory: The directory root to walk down
    :param filter_strategy: The strategy by which to filter files. Must take a string and return True or False (think of
    filter()'s function argument). Defaults to all files.
    :return:
    """
    filtered = []
    [filtered.append(Path(os.path.join(root, f))) for root, dirs, fis in os.walk(directory) for f in fis if filter_strategy(f)]
    return filtered


def class_file_filter_strategy(fn: str):
    """
    Strategy for filtering Java .class files. Excludes inner class files.
    :param fn: file name
    :return: Is .class file and not inner class file
    """
    return '$' not in fn and fn.endswith('.class')


def java_file_filter_strategy(fn: str):
    return fn.endswith('.java')


def find_equiv_files(files_a: list, files_b: list, folder_b: str):
    """
    Print a warning if there is not a file in @files_2 with the same stem (prefix) as a file in @files_1.
    :param files_a: list of Paths representing files
    :param files_b: list of Paths representing files
    :param folder_b: Directory root which files_2 are contained in
    :return: None
    """
    for f1 in [j.stem for j in files_a]:
        match = False
        for f2 in [c.stem for c in files_b]:
            if f1 == f2:
                match = True
                break
        if not match:
            print('!!!!! No file called ' + f1 + files_b[0].suffix + ' in ' + folder_b + ' or below.')


filter_strategies = {
    '.class': class_file_filter_strategy,
    '.java': java_file_filter_strategy
}


def path_stem_sort_key(p: Path):
    return p.stem


files1 = sorted(files_of_type_in_dir_r(folder_1, filter_strategies[folder_1_suffix]), key=path_stem_sort_key)
files2 = sorted(files_of_type_in_dir_r(folder_2, filter_strategies[folder_2_suffix]), key=path_stem_sort_key)


print('------- listing files: --------')

print('Files of type ' + folder_1_suffix + ' in directories starting at ' + folder_1)
[print('{:>200}'.format(str(f.resolve()))) for f in files1]
print()

print('Files of type ' + folder_2_suffix + ' in directories starting at ' + folder_2)
[print('{:>200}'.format(str(f.resolve()))) for f in files2]
print()

print('------- comparing ' + folder_1_suffix + ' to ' + folder_2_suffix + ' -------')
find_equiv_files(files1, files2, folder_2)
print('------- comparing ' + folder_2_suffix + ' to ' + folder_1_suffix + ' -------')
find_equiv_files(files2, files1, folder_1)
