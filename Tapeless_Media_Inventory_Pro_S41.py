#!/usr/bin/env python3
import difflib
import csv
from pathlib import Path
import subprocess
import os
import shutil
from datetime import datetime
######### Global Variables #########
camera_keywords = ['RED', 'BLK', 'DRN', 'AMI', 'ADC', 'CC', 'OSM', 'SA7', 'SD', 'WAV', 'WA', 'TTL', 'SD', 'A7S',
                   'GPR']
working_dir = Path('~/tapelist').expanduser()
reports_dir = Path(working_dir) / 'zOld_Reports'
PATH_TO_G_RACK = Path('/Users/Alex/Desktop/ODA/')
output_html = 'Tapelist_Compare_by_Camera.html'
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
output_path = str(working_dir / '{time}_{file_name}'.format(time=dt_string, file_name=output_html))

######### End Global Variables #########


def is_csv_valid(user_input):
    path = Path(user_input)
    while path.is_file() is False:
        path = Path(input("In order to run a check between the G-Rack and the DELTA Spire inventory, you will need\n"
                          "to export a CVS file from DELTA Spire. Once you've done that, enter the path, or drag the file\n"
                          "into the terminal, then press enter. The results will appear in ~/tapelist and should open in your\n"
                          "web browser automatically.\n\n"
                          "CSV File Path:"))
        is_csv_valid(path)
    if path.is_file() is True:
        if path.suffix == '.csv' or path.suffix == '.CSV':
            return path


def get_tapes_from_csv(csv_file):
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        inventory_ids = [row['ID'] for row in reader]
    inventory_ids.sort(reverse=True)
    return inventory_ids


def get_tapes_from_path(path):
    newpath = Path(path).glob('*/*')
    tape_names = [item.name for item in newpath if item.is_dir()]
    tape_names.sort(reverse=True)
    #for tape in tapenames:
    #    print('tape item is: ' + tape)
    return tape_names


def get_tapes_by_camera(tape_list: list, camera_list: list):
    tapes = []
    final_tape_list = []
    for camera in camera_list:
        for tape in tape_list:
            if camera in tape:
                tapes.append(tape)
    # for tape in tapes_by_camera:
        # clean it up similar to Asher's regex
        # append to final_tape_list
    # sort
    tapes.sort(reverse=True)
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


def main():
    if reports_dir.exists() is False:
        reports_dir.mkdir(parents=True)
    csv_file = input("In order to run a check between the G-Rack and the DELTA Spire inventory, you will need\n"
                     "to export a CVS file from DELTA Spire. Once you've done that, enter the path, or drag the file\n"
                     "into the terminal, then press enter. The results will appear in ~/tapelist and should open in your\n"
                     "web browser automatically.\n\n"
                     "CSV File Path:").replace("\\","")
    print(csv_file)
    csv_file = is_csv_valid(csv_file)  # Check is csv file is valid
    tapes_from_inventory_by_camera = get_tapes_by_camera(tape_list=get_tapes_from_csv(csv_file),
                                                         camera_list=camera_keywords)
    print('Tapes from DELTA SPIRE: {tapes}'.format(tapes=tapes_from_inventory_by_camera))
    tapes_from_g_rack_by_camera = get_tapes_by_camera(tape_list=get_tapes_from_path(PATH_TO_G_RACK),
                                                      camera_list=camera_keywords)
    print('Tapes from g-rack: {tapes}'.format(tapes=tapes_from_g_rack_by_camera))
    write_diff_table(local_tapes=tapes_from_g_rack_by_camera, inventory_tapes=tapes_from_inventory_by_camera)
    subprocess.check_call(['open', output_path])

if __name__ == '__main__':
    main()
