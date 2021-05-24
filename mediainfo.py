import os
import glob
from pathlib import Path
from glob import glob
from pymediainfo import MediaInfo
import pandas as pd

G_RACK_PATH = '/Users/Alex/Desktop/ODA/'
types = ('*.jpg', '*.cpp')
big_tape_list = []
day_paths = Path(G_RACK_PATH).glob('[!.]*')
BIG_LIST = []
cur_row = []
files_in_tape = []
day_list = []
i = 0


def get_media_info(file):
    media_info = MediaInfo.parse(file)
    media_stats = {'Track type': 0,
                   'Format': 0, 'Bitrate': 0, 'Frame Rate': 0, 'Example File Name': 0
                   }
    for track in media_info.tracks:
        if track.bit_rate is None:
            print('making 0')
            # media_stats = {p: 'Unknown File(s)' for p in range(0, 4)}
            media_stats.update({"Example File Name": str(file.name)})
            media_stats.update({'Bitrate': str(track.bit_rate)})
            # print("""{} tracks do not have bit rate associated with them.""".format(track.track_type))
        elif track.track_type == 'Video':
            # print("{}: {}".format(track.track_type, track.bit_rate))
            # media_stats.update ({'bitrate': str(track.bit_rate)})
            # print(track.to_data())
            # print('media stats:')
            # print(media_stats)
            media_stats.update({'Track type': str(track.track_type), 'Format': str(track.to_data()['format']),
                                'Bitrate': str(track.bit_rate), 'Frame Rate': str(track.to_data()['frame_rate'])})
            # media_stats.update({'Track type': str(track.track_type), 'Format': str(track.to_data()['format']), 'Bitrate': str(track.bit_rate), 'Frame Rate': str(track.to_data()['frame_rate'])})
    # print(media_stats)
    if media_info.video_tracks is None:
        print('making 0')
        media_stats = {p: 'None Detected' for p in range(0, 6)}
    # print(media_stats)
    return media_stats

def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return round(total_size / 1024 ** 3, 2)


def main():
    tape_list = [f for f in Path(G_RACK_PATH).glob('*/*') if f.is_dir()]
    tape_list.sort()
    for tape in tape_list:
        file_list = [f for f in tape.glob('**/[!.]*.*')]
        if len(file_list) > 0:
            cur_row.append(tape.name)
            first_file = file_list[0]
            cur_row.extend([str(len(file_list)), get_size(tape), file_list[0].name,
                            get_media_info(file_list[0])['Bitrate']])
            BIG_LIST.append(cur_row.copy())
            cur_row.clear()
    BIG_LIST.sort()
    # df = pd.DataFrame(BIG_LIST, columns=['Name', 'Item Count', 'Track Type', 'Format', 'Bitrate', 'Frame Rate', 'Example File Name'])
    df = pd.DataFrame(BIG_LIST, columns=['Name', 'Item Count', 'Size (GiB)', 'First File Name', 'Bitrate'])

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)


main()
