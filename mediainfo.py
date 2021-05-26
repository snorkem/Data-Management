import os
import glob
from pathlib import Path
from glob import glob
from pymediainfo import MediaInfo
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET


G_RACK_PATH = '/Volumes/S42 G-SPEED Shuttle XL/S42 TAPELESS MEDIA/ODA'
REPORT_NAME = 'Media_Stats.html'
dt_string = datetime.now().strftime("%Y-%m-%d_%HH-%MM-%SS")
working_dir = Path('~/').expanduser().resolve() / Path('Media Stat Reports')
report_path = str(working_dir) + '/' + '{time}_{file_name}'.format(time=dt_string, file_name=REPORT_NAME)
formats = ('.mov', '.mp4')
big_tape_list = []
BIG_LIST = []
cur_row = []

def get_media_info(file):
    media_info = MediaInfo.parse(file)
    media_stats = {
        'Format': 'Unknown', 'Bitrate': 'Unknown', 'Frame Rate': 'Unknown', 'Width': 'Unknown', 'Height': 'Unknown',
        'Color Primaries': 'Unknown', 'White Balance': 'Unknown',  'Gamma': 'Unknown', 'Bit Depth': 'Unknown', 'ISO/ASA': 'Unknown'
        }
    if media_info.video_tracks is None:
        # print('making 0')
        media_stats = {p: 'None Detected' for p in range(0, 6)}

    elif 'M4ROOT' in str(file) and '_C' in file.name:
        xlmfile = file.with_name(file.stem + 'M01.xml')
        root = ET.parse(str(xlmfile)).getroot()
        print(root)
        for tag in root.findall('AcquisitionRecord'):
            value = tag.find('CameraUnitMetadataSet')
            print(value)
        for track in media_info.video_tracks:
            #print(track.to_data())
            media_stats.update({'Format': str(track.to_data()['format']),
                                'Bitrate': str(track.bit_rate),
                                'Frame Rate': str(track.to_data()['frame_rate']),
                                'Width': str(track.to_data()['other_width']),
                                'Height': str(track.to_data()['other_height']),
                                'Bit Depth': str(track.to_data()['bit_depth']) + 'bits, '
                                                   + str(track.to_data()['chroma_subsampling'])})
    elif '0V' in file.name:
        for track in media_info.video_tracks:
            #print(file)
            media_stats.update({'Format': str(track.to_data()['format']),
                                'Bitrate': str(track.bit_rate),
                                'Frame Rate': str(track.to_data()['frame_rate']),
                                'Width': str(track.to_data()['other_width']),
                                'Height': str(track.to_data()['other_height']),
                                'Bit Depth': str(track.to_data()['bit_depth']) + 'bits, '
                                                   + str(track.to_data()['chroma_subsampling'])})
    else:
        for track in media_info.general_tracks:
            #print(track.to_data())
            media_stats.update({'Format': str(track.to_data()['video_format_list']),
                                'Bitrate': str(track.to_data()['other_overall_bit_rate']),
                                'Frame Rate': str(int(track.to_data()['comarricamerasensorfps']) / 1000),
                                'Width': str(track.to_data()['comarricameraframelinerect1awidth']),
                                'Height': str(track.to_data()['comarricameraframelinerect1aheight']),
                                'Gamma': str(track.to_data()['comarricameracolorgammasxs']),
                                'White Balance': str(track.to_data()['comarricamerawhitebalancekelvin']),
                                'ISO/ASA': str(track.to_data()['comarricameraexposureindexasa'])})
        for track in media_info.video_tracks:
            media_stats.update({'Color Primaries': str(track.to_data()['color_primaries']),
                                'Bit Depth': track.to_data()['chroma_subsampling']})
    return media_stats


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


def main():
    tape_list = [f for f in Path(G_RACK_PATH).glob('*/SD*') if f.is_dir()]
    tape_list.sort()
    for tape in tape_list:
        files = [f for f in tape.glob('**/[!.]*.*')]
        valid_files = sort_file_list(files)
        if len(valid_files) > 0:
            cur_row.append(tape.name)
            first_file = valid_files[0]
            stats = get_media_info(first_file)
            cur_row.extend([str(len(valid_files)), get_size(tape), first_file.name])
            cur_row.extend([value for key, value in stats.items()])
            '''for key, value in stats.items():
                print(value)'''
            BIG_LIST.append(cur_row.copy())
            cur_row.clear()
    BIG_LIST.sort()
    df = pd.DataFrame(BIG_LIST, columns=['Name', 'Item Count', 'Size (GiB)', 'First File Name', 'Format', 'Bitrate',
                                         'Frame Rate', 'Width', 'Height', 'Color Primaries', 'White Balance', 'Gamma', 'Bit Depth', 'ISO'])

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)
    html = df.to_html()
    with open(report_path, mode='w') as f:
        f.write(html)


main()
