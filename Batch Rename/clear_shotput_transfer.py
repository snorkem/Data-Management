#!/usr/local/bin/python3.9
from pathlib import Path
import re
import shutil

##### User-Defined Variables Here #####

G_RACK_PATH = '/Volumes/S42/'
G_SPEED_PATH = '/Volumes/S42 G-SPEED Shuttle XL/'
EXCLUDE_FOLDERS = ('YELTON_BTS', 'CBS UPFRONTS', 'TAPELESS TIMELAPSE')
SEASON_LTRS = 'UU'

##### End User-Defined Variables #####

G_RACK_ODA_DIR = G_RACK_PATH / Path('S42 TAPELESS MEDIA/ODA')
G_RACK_LAYOFF_DIR = G_RACK_PATH / Path('S42 TAPELESS MEDIA/LAYOFF')
G_RACK_SHOTPUT_LAYOFF = G_RACK_PATH / Path('SHOTPUT TRANSFER/TO LAYOFF')
G_RACK_SHOTPUT_ODA = G_RACK_PATH / Path('SHOTPUT TRANSFER/TO ODA')

G_SPEED_ODA_DIR = G_SPEED_PATH / Path('S42 TAPELESS MEDIA/ODA')
G_SPEED_LAYOFF_DIR = G_SPEED_PATH / Path('S42 TAPELESS MEDIA/LAYOFF')
G_SPEED_SHOTPUT_LAYOFF = G_SPEED_PATH / Path('SHOTPUT TRANSFER/TO LAYOFF')
G_SPEED_SHOTPUT_ODA = G_SPEED_PATH / Path('SHOTPUT TRANSFER/TO ODA')


def get_day_folders(root):
    oda_root = Path(root)
    days = [item for item in oda_root.glob('DAY*') if item.is_dir()]
    return days


def get_shotput_tapes(root):
    shotput_root = Path(root)
    tapes_to_move = [item for item in shotput_root.glob('*/*') if item.is_dir()]
    for item in tapes_to_move:
        if item.parent.name in EXCLUDE_FOLDERS:
            print('Removing: {Item} from list'.format(Item=str(item)))
            tapes_to_move.remove(item)
    return tapes_to_move


def move_tapes(src, dest):
    shotput_list = get_shotput_tapes(src)
    oda_list = get_day_folders(dest)
    ponderosa = dest.parent.parent / Path('S42 TAPELESS MEDIA') / Path('ODA') / Path('PONDEROSA')
    if len(shotput_list) > 0:
        for i in shotput_list:
            '''Get the day number from the tape name. Regex with 2 capture groups, using user-defined season letter
            code as a variable. The \d+ looks for the number in the DAY XX folders, then uses that number to match
            a destination'''
            season_and_day_num = re.search(rf'({SEASON_LTRS})(\d+)', str(i.name))
            if season_and_day_num is not None and season_and_day_num.group(1) == SEASON_LTRS:
                day_num = season_and_day_num.group(2)
                source = i
                try:  # Look for matching destination folder with correct number in the 'Day' name.
                    dest = Path([item for item in oda_list if int(str(item.name)[4:6]) == int(day_num)][0])
                    '''This iterates through the items to find the matching day folder, returns list of 1
                    Only returning the 1st element with type Path -- returning the whole list is unhelpful for
                    parsing the path when we run shutil.move()'''
                except IndexError as e:
                    print('Check your directorty structure. It worked on S42!')
                    print(str(e))
                try:
                    print('Source is: ' + str(source))
                    print('Moving to: ' + str(dest))
                    shutil.move(source, dest)
                except OSError as E:
                    print('Error copying the file to new location. Already exists? Check dir structure.\n'
                          'Here\'s the full error message:\n' + str(E))
                    continue
            elif i.parent.name == 'PONDEROSA':
                source = i
                try:
                    print('Source is: ' + str(source))
                    print('Moving to: ' + str(ponderosa))
                    shutil.move(source, ponderosa)
                except OSError as E:
                    print('Error copying the file to new location. Already exists? Check dir structure.\n'
                          'Here\'s the full error message:\n' + str(E))
                    continue


def main():
    #First do the local G-Speed drive
    move_tapes(G_SPEED_SHOTPUT_LAYOFF, G_SPEED_LAYOFF_DIR)
    move_tapes(G_SPEED_SHOTPUT_ODA, G_SPEED_ODA_DIR)
    # Now do the G-Rack
    move_tapes(G_RACK_SHOTPUT_LAYOFF, G_RACK_LAYOFF_DIR)
    move_tapes(G_RACK_SHOTPUT_ODA, G_RACK_ODA_DIR)
    print('All done!')


if __name__ == "__main__":
    main()