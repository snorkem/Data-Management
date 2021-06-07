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
from datetime import datetime
######### Global Variables #########
camera_keywords = ['FX3', 'RED', 'BLK', 'DRN', 'AMI', 'ADC', 'CC', 'OSM', 'SA7', 'SD', 'WAV', 'W', 'TTL', 'A7S',
                   'GPR']
working_dir = Path('~/tapelist').expanduser()
reports_dir = Path(working_dir) / 'zOld_Reports'
PATH_TO_G_RACK = Path('/Users/Alex/Desktop/ODA/')
PATH_TO_G_SPEED = Path('/Users/Alex/Desktop/G-Speed/')
output_html = 'Tapelist_Compare_by_Camera.html'
column_id = 'ID'
dt_string = datetime.now().strftime("%Y-%m-%d_%HH-%MM-%SS")
output_path = str(working_dir / '{time}_{file_name}'.format(time=dt_string, file_name=output_html))
######### End Global Variables #########


def are_drives_connected(g_rack_path: Path, g_speed_path: Path):
    if g_rack_path.exists() and g_rack_path.is_dir():
        print('Checking G-Rack path...\n'
              'G-Rack path valid...')
        return True
    else:
        print('G-Rack path not valid. Check the G-Rack is mounted, or check the path variable in the program. Quiting.')
        exit(1)
    if g_speed_path() and g_speed_path():
        print('Checking G-Speed path...\n'
              'G-Rack path valid...')
        return True
    else:
        print('G-Speed path not valid. Confirm G-Speed is mounted, or check the path variable in the program. Quiting.')
        exit(1)


def get_file_path():
    path = Path(input("CSV File Path:").replace("\\", "").rstrip())
    return path


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


'''def write(tapes_by_camera: list, f_out: str):
    with open(f_out, 'w') as out:
        out.writelines(tapes_by_camera)'''


def write_diff_table(local_tapes, inventory_tapes):
    # Directory checking and cleanup.
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
    # Make HTML dif file from lists and open it.
    out_file = difflib.HtmlDiff().make_file(fromlines=local_tapes, tolines=inventory_tapes,
                                            fromdesc='G-Rack Tapeless Inventory',
                                            todesc='G-Speed Tapeless Inventory (local)')
    with open(output_path, mode='w') as out:
        out.writelines(out_file)


def get_args():
    # Create the parser
    my_parser = argparse.ArgumentParser(description='Check tapeless media against inventory.')
    # Add the arguments
    my_parser.add_argument('--Grack',
                           metavar='G-Rack',
                           type=str,
                           help='The path to G-Rack RAID server',
                           default=str(PATH_TO_G_RACK))
    my_parser.add_argument('--Gspeed',
                           metavar='G-Speed',
                           type=str,
                           help='The path to local G-Speed backup drive',
                           default=str(PATH_TO_G_SPEED))
    my_parser.add_argument('--reverse',
                           action='store_true',
                           help='turns on reverse sort order')
    # Execute the parse_args() method
    args = my_parser.parse_args()
    return args


def main():
    args = get_args()
    are_drives_connected(Path(args.Grack), Path(args.Gspeed))
    #csv_file = Path(args.csv)  # Get CSV file from user argument
    if reports_dir.exists() is False:
        reports_dir.mkdir(parents=True)
    print('Getting tapes from: {0}'.format(args.Gspeed))
    tapes_from_g_speed_by_camera = get_tapes_by_camera(tape_list=get_tapes_from_path(args.Gspeed),
                                                         camera_list=camera_keywords, sort_order=args.reverse)
    print('Tapes from G-Speed: {tapes}'.format(tapes=tapes_from_g_speed_by_camera))
    tapes_from_g_rack_by_camera = get_tapes_by_camera(tape_list=get_tapes_from_path(args.Grack),
                                                      camera_list=camera_keywords, sort_order=args.reverse)
    print('Tapes from G-Rack: {tapes}'.format(tapes=tapes_from_g_rack_by_camera))
    write_diff_table(local_tapes=tapes_from_g_rack_by_camera, inventory_tapes=tapes_from_g_speed_by_camera)
    subprocess.check_call(['open', output_path])
    subprocess.check_call(['osascript', '-e', 'display notification "A comparison report between the G-Rack and G-Speed '
                                              'has been generated at: {0}/" with title '
                                              '"Report Generated!" subtitle "Thanks for '
                                              'checking your work!"'.format(working_dir)])

if __name__ == '__main__':
    main()
