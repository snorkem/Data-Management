#!/usr/env python3.9
import os
from pathlib import Path
from glob import glob
from pymediainfo import MediaInfo
import pandas as pd
from datetime import datetime
import xmltodict
from IPython.display import display, HTML
import re
from utils.thumbnails import thumb_to_df

##### Begin User Variables #####
G_RACK_PATH = '/Volumes/S42 G-SPEED Shuttle XL/S42 TAPELESS MEDIA/ODA'
REPORT_NAME = 'Media_Stats.html'
SEASON_LTRS = 'UU'
SEARCH_PATTERN = 'SD'
THUMB_SEEK = '00:10:00'
##### End User Variables #####

dt_string = datetime.now().strftime("%Y-%m-%d_%HH-%MM-%SS")
working_dir = Path('~/').expanduser().resolve() / Path('SEGMediaInfo Reports')
thumbs_path = working_dir.joinpath('thumbnails')
report_path = Path(str(working_dir) + '/' + '{time}_{file_name}'.format(time=dt_string, file_name=REPORT_NAME))
formats = ('.mov', '.mp4', '.mxf')  # Accepted file formats.
camera_dict = {  # These letters indicate camera used and the folder structure to navigate in order to find footage.
    'A7s': ('D', 'E', 'F', 'G', 'L'),  # A7s or similar structure
    'FX3': ('N', 'K'),
    'Alexa': ('A', 'B'),
}
cur_row = []  # current working row as we build the dataframe
BIG_LIST = []  # master list of lists from which we will construct the final dataframe


def path_exists(path: Path):
    if path.exists() and path.is_dir():
        print('Checking G-Rack path...\n'
              'G-Rack path valid...')
        return True
    else:
        print('G-Rack path not valid. Check the G-Rack is mounted, or check the path variable in the program. Quiting.')
        exit(1)


def get_files(path_to_search):
    valid_files = sort_file_list([f for f in path_to_search.iterdir()])
    if len(valid_files) >= 1:
        file = valid_files[0]
        return Path(file)
    else:
        return None


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return round(total_size / 1024 ** 3, 2)


def sort_file_list(file_list):
    new_list = []
    for item in file_list:
        for f in formats:
            if f == item.suffix.lower():
                new_list.append(item)
    return new_list


def write_report(path: Path, df: pd.DataFrame):
    if path.exists() is False:
        report_path.mkdir(parents=True)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        pd.set_option('display.max_colwidth', None)
        print(df)
    html = HTML('''
            <style>
                .df tbody tr:nth-child(even) { background-color: lightblue; }
            </style>
            ''' + df.to_html(classes="df", escape=False))
    with open(report_path, mode='w') as f:
        f.write(html.data)


def get_media_info(tapename: Path):
    camera_letter = re.search(rf'({SEASON_LTRS})([-\d]{{1,2}})([A-Z])([A-Z])', tapename.name).group(3)
    media_stats = {
        'Thumbnail': 'Unknown', 'Name': 'Unknown', 'First File Name': 'Unknown', 'Size (GiB)': 'Unknown', 'Format': 'Unknown',
        'Bitrate': 'Unknown', 'Frame Rate': 'Unknown', 'Width': 'Unknown', 'Height': 'Unknown',
        'Color Primaries': 'Unknown', 'White Balance': 'Unknown',  'Gamma': 'Unknown', 'Bit Depth': 'Unknown',
        'ISO/ASA': 'Unknown'
        }
    if camera_letter in camera_dict['A7s']:  # A7siii footage or similar
        media_stats.update({
            'Name': tapename.name
        })
        subdir = tapename.joinpath('M4ROOT', 'Clip')
        if len(list(subdir.iterdir())) > 0:
            file = get_files(subdir)
            print('looking for thumb of ' + str(file))
            media_stats.update({
                'Thumbnail': thumb_to_df(file, thumbs_path, THUMB_SEEK)
            })
            media_info = MediaInfo.parse(file)
            try:
                xmlfile = file.with_name(file.stem + 'M01.xml')
                with open(xmlfile) as f:
                    xml = xmltodict.parse(f.read())
                    capture_gamma_equation = xml['NonRealTimeMeta']['AcquisitionRecord']['Group']['Item'][0]['@value']
                    capture_color_primaries = xml['NonRealTimeMeta']['AcquisitionRecord']['Group']['Item'][1]['@value']
            except Exception as e:
                print('Error accessing Sony XML file for folder: {f}'.format(f=tapename))
                print(e)
            for track in media_info.video_tracks:
                media_stats.update({
                                    'Size (GiB)': str(get_size(tapename)),
                                    'First File Name': file.name,
                                    'Format': str(track.to_data()['format']),
                                    'Bitrate': str(round(track.bit_rate / 1000000)) + ' Mb/s',  # Convert to Mb/s
                                    'Frame Rate': str(track.to_data()['frame_rate']),
                                    'Width': str(track.to_data()['other_width'][0]),
                                    'Height': str(track.to_data()['other_height'][0]),
                                    'Bit Depth': str(track.to_data()['bit_depth']) + 'bits, '
                                    + str(track.to_data()['chroma_subsampling']),
                                    'Gamma': capture_gamma_equation,
                                    'Color Primaries': capture_color_primaries})
        else:
            for key, value in media_stats.items():
                media_stats.update({
                    key: 'Empty Folder'
                })
    elif camera_letter in camera_dict['FX3']:  # FX3 Footage or similar
        media_stats.update({
            'Name': tapename.name
        })
        subdir = tapename.joinpath('XDROOT', 'Clip')
        if len(list(subdir.iterdir())) > 0:
            file = get_files(subdir)
            media_info = MediaInfo.parse(file)
            media_stats.update({
                'Thumbnail': thumb_to_df(file, thumbs_path, THUMB_SEEK)
            })
            try:
                xmlfile = file.with_name(file.stem + 'M01.xml')
                with open(xmlfile) as f:
                    xml = xmltodict.parse(f.read())
                    capture_gamma_equation = xml['NonRealTimeMeta']['AcquisitionRecord']['Group']['Item'][0]['@value']
                    capture_color_primaries = xml['NonRealTimeMeta']['AcquisitionRecord']['Group']['Item'][1]['@value']
            except Exception as e:
                print('Error accessing Sony XML file for folder: {f}'.format(f=tapename))
                print(e)
            for track in media_info.video_tracks:
                media_stats.update({
                                    'Size (GiB)': str(get_size(tapename)),
                                    'First File Name': file.name,
                                    'Format': str(track.to_data()['format']),
                                    'Color Primaries': capture_color_primaries,
                                    'Gamma': capture_gamma_equation,
                                    'Bitrate': track.to_data()['other_bit_rate'][0],
                                    'Frame Rate': str(track.to_data()['frame_rate']),
                                    'Width': str(track.to_data()['other_width'][0]),
                                    'Height': str(track.to_data()['other_height'][0]),
                                    'Bit Depth': str(track.to_data()['bit_depth']) + 'bits, '
                                    + str(track.to_data()['chroma_subsampling'])})
        else:
            for key, value in media_stats.items():
                media_stats.update({
                    key: 'Empty Folder'
                })

    elif camera_letter in camera_dict['Alexa']:  # Alexa footage
        media_stats.update({
            'Name': tapename.name
        })
        file = [f for f in tapename.glob('*/*') if f.is_file() and f.suffix.lower() in formats]
        if len(file) > 0:
            first_file = file[0]
            media_info = MediaInfo.parse(first_file)
            media_stats.update({
                'Thumbnail': thumb_to_df(first_file, thumbs_path, THUMB_SEEK)
            })
            for track in media_info.general_tracks:
                # print(track.to_data())
                media_stats.update({
                                    'Size (GiB)': str(get_size(tapename)),
                                    'Name': tapename.name,
                                    'First File Name': first_file.name,
                                    'Format': str(track.to_data()['video_format_list']),
                                    'Bitrate': str(track.to_data()['other_overall_bit_rate'][0]),
                                    'Frame Rate': str(int(track.to_data()['comarricamerasensorfps']) / 1000),
                                    'Width': str(track.to_data()['comarricameraframelinerect1awidth']),
                                    'Height': str(track.to_data()['comarricameraframelinerect1aheight']),
                                    'Gamma': str(track.to_data()['comarricameracolorgammasxs']),
                                    'White Balance': str(track.to_data()['comarricamerawhitebalancekelvin']),
                                    'ISO/ASA': str(track.to_data()['comarricameraexposureindexasa'])})
            for track in media_info.video_tracks:
                media_stats.update({'Color Primaries': str(track.to_data()['color_primaries']),
                                    'Bit Depth': track.to_data()['chroma_subsampling']})
    else:
        media_stats.update({
            'Name': tapename.name
        })
    return media_stats


def main():
    if path_exists(Path(G_RACK_PATH)) is True:
        tape_list = [f for f in Path(G_RACK_PATH).glob(rf'*/{SEARCH_PATTERN}*') if f.is_dir()]  # Find a regex to do this...
        tape_list.sort()
        for tape in tape_list:
            print('looking for tape: ' + str(tape))
            stats = get_media_info(tape)
            cur_row.extend([value for key, value in stats.items()])
            BIG_LIST.append(cur_row.copy())
            cur_row.clear()
        df = pd.DataFrame(BIG_LIST, columns=['Thumbnail', 'Name', 'First File Name', 'Size (GiB)', 'Format', 'Bitrate',
                                             'Frame Rate', 'Width', 'Height', 'Color Primaries', 'White Balance',
                                             'Gamma', 'Bit Depth', 'ISO/ASA'])
        write_report(working_dir, df)


if __name__ == '__main__':
    main()

