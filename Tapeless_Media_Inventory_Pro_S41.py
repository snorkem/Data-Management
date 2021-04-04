#!/usr/bin/env python3
import difflib
import csv
from pathlib import Path
import argparse
import subprocess
import os
import shutil
from datetime import datetime
######### Global Variables #########
camera_keywords = ['RED', 'BLK', 'DRN', 'AMI', 'ADC', 'CC', 'OSM', 'SA7', 'SD', 'WAV', 'WA', 'TTL', 'A7S',
                   'GPR']
working_dir = Path('~/tapelist').expanduser()
reports_dir = Path(working_dir) / 'zOld_Reports'
PATH_TO_G_RACK = Path('/Users/Alex/Desktop/ODA/')
output_html = 'Tapelist_Compare_by_Camera.html'
column_id = 'ID'
dt_string = datetime.now().strftime("%Y-%m-%d_%HH-%MM-%SS")
output_path = str(working_dir / '{time}_{file_name}'.format(time=dt_string, file_name=output_html))
######### End Global Variables #########


def is_g_rack_connected(path: Path):
    if path.exists() and path.is_dir():
        print('G-Rack path valid...')
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


def get_tapes_by_camera(tape_list: list, camera_list: list, sort_order: bool):
    tapes = []
    final_tape_list = []
    # In this loop we compare camera list
    for camera in camera_list:
        if len(camera) != 3:
            # Controlling for the tape names with only 2 letters. Parsing those in separate elif conditions.
            for tape in tape_list:
                if camera in tape[:3]:
                    tapes.append(tape)
                    tape_list.remove(tape)
        elif camera == 'WA':
            for tape in tape_list:
                if camera == tape[-2:]:
                    tapes.append(tape)
                    tape_list.remove(tape)
        elif camera == 'CC':
            for tape in tape_list:
                if camera == tape[:2]:
                    tapes.append(tape)
                    tape_list.remove(tape)
        elif camera == 'SD':
            for tape in tape_list:
                if camera == tape[:2]:
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
    if Path(reports_dir).exists() is False:
        reports_dir.mkdir()
    files = [item for item in working_dir.glob('*/') if item.is_file() and item.suffix == '.html'
             or item.suffix == '.HTML']
    for file in files:
        try:
            shutil.copy2(str(file), str(working_dir) + '/zOld_Reports')
            file.unlink()
        except FileNotFoundError:
            os.mkdir(working_dir + '/zOld_Reports')
    out_file = difflib.HtmlDiff().make_file(fromlines=local_tapes, tolines=inventory_tapes,
                                            fromdesc='G-Rack Tapeless Inventory',
                                            todesc='DELTA Spire Tapeless Inventory')
    with open(output_path, mode='w') as out:
        out.writelines(out_file)


def get_args():
    # Create the parser
    my_parser = argparse.ArgumentParser(description='Check tapeless media against inventory.')
    # Add the arguments
    my_parser.add_argument('csv',
                           metavar='csv',
                           type=str,
                           help='the path to csv list from Delta Spire',
                           default='~/')
    my_parser.add_argument('--reverse',
                           action='store_true',
                           help='turns on reverse sort order')
    # Execute the parse_args() method
    args = my_parser.parse_args()
    return args


def main():
    is_g_rack_connected(PATH_TO_G_RACK)
    is_reverse_sort = False
    args = get_args()
    csv_file = Path(args.csv)  # Get CSV file from user argument
    if args.reverse:
        is_reverse_sort = True
    if reports_dir.exists() is False:
        reports_dir.mkdir(parents=True)
    # Check is csv file is valid and return path
    while is_csv_valid(csv_file) is False:
        print('Invalid path or file. Try again.')
        csv_file = get_file_path()
    print("CSV file located at: {0}".format(csv_file))
    tapes_from_inventory_by_camera = get_tapes_by_camera(tape_list=get_tapes_from_csv(csv_file, is_reverse_sort),
                                                         camera_list=camera_keywords, sort_order=is_reverse_sort)
    print('Tapes from DELTA SPIRE: {tapes}'.format(tapes=tapes_from_inventory_by_camera))
    tapes_from_g_rack_by_camera = get_tapes_by_camera(tape_list=get_tapes_from_path(PATH_TO_G_RACK),
                                                      camera_list=camera_keywords, sort_order=is_reverse_sort)
    print('Tapes from g-rack: {tapes}'.format(tapes=tapes_from_g_rack_by_camera))
    write_diff_table(local_tapes=tapes_from_g_rack_by_camera, inventory_tapes=tapes_from_inventory_by_camera)
    subprocess.check_call(['open', output_path])


if __name__ == '__main__':
    main()
