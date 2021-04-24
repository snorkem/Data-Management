#!/usr/bin/env python3
# By Alex Fichera
# Based on bash workflow by Asher Pink, without whom this project would not exist.
# Only tested on MacOS. Does not work with Python 2.7 for syntax reasons.
import difflib
import csv
from pathlib import Path
import argparse
import subprocess
import os
import shutil
import pandas as pd
import collections
import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename
######### Global Variables #########
camera_keywords = ['FX3', 'RED', 'BLK', 'DRN', 'AMI', 'ADC', 'CC', 'OSM', 'SA7', 'SD', 'W', 'TTL', 'A7S',
                   'GPR']
working_dir = Path('~/tapelist').expanduser()
reports_dir = working_dir / 'zOld_Reports'
PATH_TO_G_RACK = Path('/Users/Alex/Desktop/ODA/')
output_html = 'Tapelist_Compare_by_Camera.html'
output_dups = 'Duplicate_Report.html'
column_id = 'ID'
dt_string = datetime.datetime.now().strftime("%Y-%m-%d_%HH-%MM-%SS")
output_path = str(working_dir / '{time}_{file_name}'.format(time=dt_string, file_name=output_html))
dup_output_path = str(working_dir / '{time}_{file_name}'.format(time=dt_string, file_name=output_dups))
######### End Global Variables #########


def gui_get_csv():
    Tk().withdraw()
    filename = askopenfilename()
    return Path(filename)


def is_g_rack_connected(path: Path):
    if path.exists() and path.is_dir():
        print('Checking G-Rack path...\n'
              'G-Rack path valid...')
        return True
    else:
        print('G-Rack path not valid. Check the G-Rack is mounted, or check the path variable in the program. Quiting.')
        exit(1)


def get_file_path():
    path = Path(input("CSV File Path:").replace("\\", "").rstrip())
    return path


def is_csv_valid(user_input):
    if user_input is None:
        return False
    elif user_input.is_file() is False:
        return False
    elif user_input.is_file():
        if user_input.suffix == '.csv' or user_input.suffix == '.CSV':
            return True
        else:
            return False
    else:
        print('Something went wrong validating the csv file...')


def get_tapes_from_csv(csv_file, sort):
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        try:
            inventory_ids = [row[column_id] for row in reader]
        except KeyError:
            print('Something is wrong with the CSV file. Check that it is formatted properly with the tape'
                  'names in an "ID" column. Quiting...')
            exit(1)
    inventory_ids.sort(reverse=sort)
    return inventory_ids


def get_tapes_from_path(path):
    newpath = Path(path).glob('*/*')
    tape_names = [item.name for item in newpath if item.is_dir()]
    tape_names.sort(reverse=False)
    #for tape in tapenames:
    #    print('tape item is: ' + tape)
    return tape_names


def get_size_GiB(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return round(total_size / 1024**3, 2)


def get_size_GB(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return round(total_size / 1000**3, 2)


def get_dup_list(path):
    path_list = [item for item in path.glob('*/**') if item.is_dir]
    names = [item.name for item in path_list]
    sizes_GiB = [get_size_GiB(item) for item in path_list]
    sizes_GB = [get_size_GB(item) for item in path_list]
    mod_times = [datetime.datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d-%H:%M') for item in path_list]
    df = pd.DataFrame(list(zip(path_list, names, sizes_GiB, sizes_GB, mod_times)), columns=['Path', 'Tape Name', 'Size (GiB)', 'Size (GB)',
                                                                                 'Last Modified'])
    duplicate_rows_df = df[df.duplicated(['Tape Name'], keep=False)].reset_index(drop=True)
    duplicate_rows_df.index = range(1, len(duplicate_rows_df)+1)
    return duplicate_rows_df


def get_tapes_by_camera(tape_list: list, camera_list: list, sort_order: bool):
    tapes = []
    final_tape_list = []
    # In this loop we compare camera list
    for camera in camera_list:
        if len(camera) == 3:
            for tape in tape_list:
                if camera in tape[:3]:
                    tapes.append(tape)
                    tape_list.remove(tape)
        elif len(camera) == 2:
            # Controlling for the tape names with only 2 letters. Parsing those in separate elif conditions.
            if camera == 'CC':
                for tape in tape_list:
                    if camera == tape[:2]:
                        tapes.append(tape)
                        tape_list.remove(tape)
            elif camera == 'SD':
                for tape in tape_list:
                    if camera == tape[:2]:
                        tapes.append(tape)
                        tape_list.remove(tape)
            elif len(camera) == 1:
                if camera == 'W':
                    for tape in tape_list:
                        if camera == tape[-2:]:  # W is cineflex camera -- not used in S1
                            tapes.append(tape)
                            tape_list.remove(tape)

    # add any leftover items to the list
    tapes.extend(tape_list)
    # sort
    tapes.sort(reverse=sort_order)
    return tapes


def write(tapes_by_camera: list, f_out: str):
    with open(f_out, 'w') as out:
        out.writelines(tapes_by_camera)


def write_diff_table(local_tapes, inventory_tapes):
    # Directory checking and cleanup.
    if Path(reports_dir).exists() is False:
        reports_dir.mkdir()
    files = [item for item in working_dir.glob('*/') if item.is_file() and item.suffix.lower() == '.html']
    for file in files:
        try:
            shutil.copy2(str(file), str(working_dir) + '/zOld_Reports')
            file.unlink()
        except FileNotFoundError:
            os.mkdir(working_dir + '/zOld_Reports')
    # Make HTML dif file from lists and open it.
    out_file = difflib.HtmlDiff().make_file(fromlines=local_tapes, tolines=inventory_tapes,
                                            fromdesc='G-Rack Tapeless Inventory',
                                            todesc='DELTA Spire Tapeless Inventory')
    with open(output_path, mode='w') as out:
        out.writelines(out_file)
    dups = get_dup_list(PATH_TO_G_RACK)
    if len(dups) > 0:
        html = dups.to_html()
        with open(dup_output_path, mode='w') as f:
            f.write(html)


def get_args():
    # Create the parser
    my_parser = argparse.ArgumentParser(description='Check tapeless media against inventory.')
    # Add the arguments
    my_parser.add_argument('csv',
                           metavar='csv',
                           type=str,
                           help='The path to csv list from Delta Spire',
                           default='~/')
    my_parser.add_argument('--reverse',
                           action='store_true',
                           help='turns on reverse sort order')
    # Execute the parse_args() method
    args = my_parser.parse_args()
    return args


def main():
    args = get_args()
    is_g_rack_connected(PATH_TO_G_RACK)
    #csv_file = Path(args.csv)  # Get CSV file from user argument
    csv_file = gui_get_csv()
    if reports_dir.exists() is False:
        reports_dir.mkdir(parents=True)
    # Check is csv file is valid and return path
    while is_csv_valid(csv_file) is False:
        print('Invalid path or file. Try again.')
        csv_file = gui_get_csv()
    print("CSV file located at: {0}".format(csv_file))
    tapes_from_inventory_by_camera = get_tapes_by_camera(tape_list=get_tapes_from_csv(csv_file, args.reverse),
                                                         camera_list=camera_keywords, sort_order=args.reverse)
    print('Tapes from DELTA SPIRE: {tapes}'.format(tapes=tapes_from_inventory_by_camera))
    tapes_from_g_rack_by_camera = get_tapes_by_camera(tape_list=get_tapes_from_path(PATH_TO_G_RACK),
                                                      camera_list=camera_keywords, sort_order=args.reverse)
    print('Tapes from G-Rack: {tapes}'.format(tapes=tapes_from_g_rack_by_camera))
    write_diff_table(local_tapes=tapes_from_g_rack_by_camera, inventory_tapes=tapes_from_inventory_by_camera)
    subprocess.check_call(['open', output_path])
    if Path(dup_output_path).exists():
        subprocess.check_call(['open', dup_output_path])
        subprocess.check_call(
            ['osascript', '-e', 'display notification "Report saved at: {0}/" with title '
                                '"Duplicates Found!"'.format(working_dir)])
    subprocess.check_call(['osascript', '-e', 'display notification "A comparison report between the G-Rack and Delta'
                                              ' Spire has been generated at: {0}/" with title '
                                              '"Report Generated!" subtitle "Thanks for '
                                              'checking your work!"'.format(working_dir)])

if __name__ == '__main__':
    main()
