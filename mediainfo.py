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


def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return round(total_size / 1024**3, 2)

    for track in media_info.tracks:
        if track.bit_rate is None:
            print('making 0')
            #media_stats = {p: 'Unknown File(s)' for p in range(0, 4)}
            media_stats.update({"Example File Name": str(file.name)})
            media_stats.update({'Bitrate': str(track.bit_rate)})
            #print("""{} tracks do not have bit rate associated with them.""".format(track.track_type))
        elif track.track_type == 'Video':
            #print("{}: {}".format(track.track_type, track.bit_rate))
            #media_stats.update ({'bitrate': str(track.bit_rate)})
            #print(track.to_data())
            #print('media stats:')
           #print(media_stats)
            media_stats.update({'Track type': str(track.track_type), 'Format': str(track.to_data()['format']), 'Bitrate': str(track.bit_rate), 'Frame Rate': str(track.to_data()['frame_rate'])})
            #media_stats.update({'Track type': str(track.track_type), 'Format': str(track.to_data()['format']), 'Bitrate': str(track.bit_rate), 'Frame Rate': str(track.to_data()['frame_rate'])})
    #print(media_stats)
    if media_info.video_tracks is None:
        print('making 0')
        media_stats = {p: 'None Detected' for p in range(0, 6)}
    #print(media_stats)
    return media_stats


def main():
    for day in Path(G_RACK_PATH).iterdir():
        if day.is_dir():
            day_list.append(str(day))
            day_tape_list = [x for x in day.iterdir() if x.is_dir()]
            day_tape_list.sort()
            for tape in day_tape_list:
                n_files_in_tape = 0
                #print(tape)
                file_list = [f for f in tape.glob('**/[!.]*.*')]
                files_in_tape = file_list.copy()
                if len(files_in_tape) != 0:
                    cur_row.append(tape.name)
                    for f in files_in_tape:  # THIS WORKS!!!
                        if str(f.suffix).lower() == '.mp4' or str(f.suffix).lower() == '.mov' or str(f.suffix).lower() == '.r3d':
                            n_files_in_tape += 1
                    '''if str(files_in_tape[0].suffix).lower() == '.mp4' or str(f.suffix).lower() == '.mov' or str(f.suffix).lower() == '.r3d' or str(f.suffix).lower() == '.mxf':
                        cur_row.append([n_files_in_tape, get_size(tape), str(files_in_tape[0].name)])'''
                    cur_row.extend([n_files_in_tape, get_size(tape), str(files_in_tape[0].name)])
                    #print(cur_row)
                    #print(files_in_tape[0])
                    #media_stats = get_media_info(files_in_tape[0])
                    #for key, value in media_stats.items():
                    #    cur_row.append(value)
                    #print(list(media_stats.values()))
                    #cur_row.extend()
                    #print(cur_row)
                    BIG_LIST.append(cur_row.copy())
                    cur_row.clear()
                #print('pringing files')
                #print(files)# use first element to get info
                    #print('tests')
                    #print(i)
                        #files_in_tape.append(i.name)
                        #print(files_in_tape)
                        #print(media_stats)
                    #cur_row.extend(list(media_stats.values()))
                    #BIG_LIST.append(cur_row.copy())
                    #cur_row.clear()
                        #print('cur row is:')
                        #print(cur_row)
                        #print(BIG_LIST)
                        #cur_row = []
                          # count files in tape dir

                        #append tape to df
                        # itterate through media info and add to collumns of df

    #print('big list is')
    #print(BIG_LIST)
    BIG_LIST.sort()
    #df = pd.DataFrame(BIG_LIST, columns=['Name', 'Item Count', 'Track Type', 'Format', 'Bitrate', 'Frame Rate', 'Example File Name'])
    df = pd.DataFrame(BIG_LIST, columns=['Name', 'Item Count', 'Size (GiB)', 'Example File Name'])

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)


main()
