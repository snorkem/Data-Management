from pathlib import Path
import os
import subprocess
import tkinter
from itertools import chain
from tkinter import messagebox

PATH_TO_G_RACK = Path('/Volumes/S42/SHOTPUT TRANSFER/TO ODA')
PATH_TO_G_SPEED = Path('/Volumes/S42 G-SPEED Shuttle XL/SHOTPUT TRANSFER/TO ODA')

season_letters = 'UU'
tape_keys = {'Drone': 'DRN', 'a7s': 'SD', 'Cablecam': 'CC', 'GoPro': 'GPR', 'Blackmagic':  'BLK'}


def get_tapes(root, key):
    tape_list = [item for item in root.glob('**/{key}{ltrs}*'.format(ltrs=season_letters, key=key)) if item.is_dir()]
    return tape_list


def rename_seale(tape_list):
    #  We're not using this anymore, but keeping it in case the need arises.
    for i in tape_list:
        i_parent = i.parent.resolve()
        name_prefix = i_parent.name
        new_folder_path = str(i.parent) + '/' + str(name_prefix) + '_' + str(i.name)
        i.rename(new_folder_path)
        new_folder_path = Path(new_folder_path).resolve()
        if new_folder_path.exists:
            files = [file for file in new_folder_path.glob('*') if file.is_file() and file.suffix.lower() == '.mp4' or
                     file.suffix.lower() == '.mov']
            for file in files:
                if 'DJI{ltrs}'.format(ltrs=season_letters) not in str(file.name) or \
                        'MVI{ltrs}'.format(ltrs=season_letters) not in str(file.name):
                    print('Old name is: ' + str(file))
                    new_file_name = str(new_folder_path) + '/' +str(name_prefix) + '_' + str(file.name)
                    print(new_file_name)
                    file.rename(new_file_name)
                else:
                    print('Name looks good. Skipping: ' + str(file))
            # print(str(files))
                    

def rename_CC(tape_list):
    for i in tape_list:
        # print(str(i.name))
        clip_path = i.joinpath('M4ROOT/CLIP/')
        if clip_path.exists:
            files = [file for file in clip_path.glob('*') if file.is_file() and file.suffix.lower() == '.mp4' or
                     file.suffix.lower() == '.xml']
            for file in files:
                if '{key}{ltrs}'.format(key=tape_keys['Cablecam'], ltrs=season_letters) not in str(file.name):
                    # print('Old name is: ' + str(file) + ' New name would be: ' + str(clip_path) + '/' + str(i.name) + '_' + str(file.name))
                    new_file_name = str(clip_path) + '/' +str(i.name) + '_' + str(file.name)
                    print(new_file_name)
                    file.rename(new_file_name)
                else:
                    print('Name looks good. Skipping: ' + str(file))
            # print(str(files))


def rename_a7s(tape_list):
    for i in tape_list:
        #print(str(i.name))
        clip_path = i.joinpath('M4ROOT/CLIP/')
        if clip_path.exists:
            files = [file for file in clip_path.glob('*') if file.is_file() and file.suffix.lower() == '.mp4' or
                     file.suffix.lower() == '.xml']
            for file in files:
                if '{key}{ltrs}'.format(key=tape_keys['a7s'], ltrs=season_letters) not in str(file.name):
                    #print('Old name is: ' + str(file) + ' New name would be: ' + str(clip_path) + '/' + str(i.name) + '_' + str(file.name))
                    new_file_name = str(clip_path) + '/' + str(i.name) + '_' + str(file.name)
                    print(new_file_name)
                    file.rename(new_file_name)
                else:
                    print('Name looks good. Skipping: ' + str(file))
            # print(str(files))

                    
def rename_gopro(tape_list):
    for i in tape_list:
        print(str(i.name))
        clip_path = i.joinpath('DCIM/100GOPRO/')
        three_sixty_path = i.joinpath('DCIM/Camera01/')
        # reality_gpr_paths = [dir for dir in i.parent.glob('*/*') if dir.is_dir() and 'GOPRO' in dir.name]
        if clip_path.exists:
            files = [file for file in clip_path.glob('*') if file.is_file() and file.suffix.lower() == '.mp4' or
                     file.suffix.lower() == '.lrv']
            for file in files:
                if not '{key}{ltrs}'.format(key=tape_keys['GoPro'], ltrs=season_letters) in str(file.name):
                    #print('Old name is: ' + str(file) + ' New name would be: ' + str(clip_path) + '/' + str(i.name) + '_' + str(file.name))
                    new_file_name = str(clip_path) + '/' +str(i.name) + '_' + str(file.name)
                    print(new_file_name)
                    file.rename(new_file_name)
                else:
                    print('Name looks good. Skipping: ' + str(file))
        if three_sixty_path.exists:
            clip_path = i.joinpath('DCIM/Camera01/')
            files = [file for file in clip_path.glob('*') if file.is_file() and file.suffix.lower() == '.insv']
            for file in files:
                if not '{key}{ltrs}'.format(key=tape_keys['GoPro'], ltrs=season_letters) in str(file.name):
                    new_file_name = str(clip_path) + '/' +str(i.name) + '_' + str(file.name)
                    print(new_file_name)
                    file.rename(new_file_name)
                else:
                    print('Name looks good. Skipping: ' + str(file))
        '''if len(reality_gpr_paths) > 0:
            for dir in reality_gpr_paths:
                files = [file for file dir.glob('*/**') if file.is_file() and file.suffix.lower() == '.mov' or
                         file.suffix.lower() == '.mp4']
                for file in files:
                    if not '{key}{ltrs}'.format(key=tape_keys['GoPro'], ltrs=season_letters) in str(file.name):
                        new_file_name = i.parent.joinpath(dir.name) / + '_' + str(file.name)'''




def rename_drone(tape_list):
    for i in tape_list:
        clip_folders = [item for item in i.iterdir() if item.is_dir() and '{key}{ltrs}'.format(key=tape_keys['Drone'], ltrs=season_letters)
                        not in str(item.name)]
        #print(clip_folders)
        for folder in clip_folders:
            new_folder_name = folder.rename(str(folder.parent) + '/' + i.name + '_' + str(folder.name))
            clip_files = [file for file in new_folder_name.glob('**/*') if file.is_file() and
                          file.suffix.lower() == '.mp4'
                          or  file.suffix.lower() == '.mov' or  file.suffix.lower() == '.mov']
            valid_clip_files = [file for file in clip_files if not '{key}{ltrs}'.format(key=tape_keys['Blackmagic'], ltrs=season_letters) in str(file.name)]
            for file in valid_clip_files:
                #print(str(file))
                new_file_name = file.rename(str(file.parent) + '/' + i.name + '_' + str(file.name))
                print(str(new_file_name))


def rename_blk(tape_list):
    for i in tape_list:
        clip_path = i
        if clip_path.exists:
            files = [file for file in clip_path.glob('*') if file.is_file() and file.suffix.lower() == '.mov' and
                     'capture' in file.name.lower()]
            for file in files:
                if '{key}{ltrs}'.format(key=tape_keys['Blackmagic'], ltrs=season_letters) not in str(file.name):
                    # print('Old name is: ' + str(file) + ' New name would be: ' + str(clip_path) + '/' +
                    #      str(i.name) + '_' + str(file.name))
                    new_file_name = str(clip_path) + '/' + str(i.name) + '_' + str(file.name)
                    print(new_file_name)
                    file.rename(new_file_name)
                else:
                    print('Name looks good. Skipping: ' + str(file))


def main():
    # First do G-Rack
    rename_drone(get_tapes(PATH_TO_G_RACK, tape_keys['Drone']))
    rename_a7s(get_tapes(PATH_TO_G_RACK, tape_keys['a7s']))
    rename_gopro(get_tapes(PATH_TO_G_RACK, tape_keys['GoPro']))
    rename_CC(get_tapes(PATH_TO_G_RACK, tape_keys['Cablecam']))
    rename_blk(get_tapes(PATH_TO_G_RACK, tape_keys['Blackmagic']))

    # Now do G-Speed
    rename_drone(get_tapes(PATH_TO_G_SPEED, tape_keys['Drone']))
    rename_a7s(get_tapes(PATH_TO_G_SPEED, tape_keys['a7s']))
    rename_gopro(get_tapes(PATH_TO_G_SPEED, tape_keys['GoPro']))
    rename_CC(get_tapes(PATH_TO_G_SPEED, tape_keys['Cablecam']))
    rename_blk(get_tapes(PATH_TO_G_SPEED, tape_keys['Blackmagic']))

    # This code is to hide the main tkinter window
    root = tkinter.Tk()
    root.withdraw()

    # Message Box
    messagebox.showinfo("Magic Renamer!", "Batch rename complete! Check your Shotput Transfer on G-Speed and G-Rack to verify.")


main()

if __name__ == "__main__":
    main()