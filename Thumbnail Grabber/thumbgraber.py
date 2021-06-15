import os
import re
from datetime import datetime
from glob import glob
from pathlib import Path
from pathlib import Path
import fire
import pandas as pd
import xmltodict
from pymediainfo import MediaInfo
from timecode import Timecode
from utils.mediainfo import get_media_info, get_startTC
from utils.thumbnails import thumb_to_df

# Code is incomplete. Need to be able to parse mxf and mp4 files from sony cameras. Also clean
# up all these garbage unused variables bellow.

##### Begin User Variables #####
FPS = '29.97'  # FPS of timecode track -- not the camera FPS!
##### End User Variables #####

TEST_PATH = Path('/Volumes/S42 G-SPEED Shuttle XL/S42 TAPELESS MEDIA/ODA/DAY 18 - [18 OF X]/SDUU18AA')
TEST_OUTPUT = Path('/Users/admin/Desktop/test_stills')

dt_string = datetime.now().strftime("%Y-%m-%d_%HH-%MM-%SS")
working_dir = Path('~/').expanduser().resolve() / Path('SEGMediaInfo Reports')
thumbs_path = working_dir.joinpath('thumbnails')
report_path = Path(str(working_dir) + '/' + '{time}_{file_name}'.format(time=dt_string, file_name=REPORT_NAME))
formats = ('.mov', '.mp4', '.mxf')  # Accepted file formats.


def get_clips_from_path(path: Path):
    # Recursively get all valid files into a list, excluding subclips.
    file_list = [f for f in path.glob(r'./**/*') if f.suffix.lower() in formats and f.parent.name != 'sub']
    if len(file_list) > 0:
        camera = get_camera_type(file_list[0])
        return file_list, camera
    else:
        print('No timecode!')
        quit(1)


""" Find out if given timecode exists within range and return True or False """
def does_tc_exist(tc_target: Timecode, tc_start: Timecode, tc_duration: Timecode, fps):
    tc_end = tc_start + tc_duration
    tc_start_frames = tc_start.frames
    tc_end_frames = tc_end.frames
    target_frame = tc_target.frames
    if target_frame in range(tc_start_frames, tc_end_frames):
        return True
    else:
        return False


def make_thumb(file: Path, output_dir: Path, timecode: Timecode, media_stats):
    if file.exists() and output_dir.exists:
        print('making thumb!')
        thumbhtml = thumb_to_df(file, output_dir, str(timecode), media_stats)
    else:
        print('Check that source and destination exist')
    return thumbhtml


def grab(target: str, tc: str):
    """
    :param target: Path to search for media files
    :param tc: Desired timecode of stills
    """
    clips, camera = get_clips_from_path(Path(target))
    looking_for = Timecode(FPS, tc)
    print(looking_for)
    for clip in clips:
        if clip.suffix.lower() == '.mov':  # Quick way to control for only Alexa quicktimes
            stats = get_media_info(clip)
            start_tc_frame = Timecode(FPS, stats['Start TC'])
            duration_frames = Timecode(FPS, start_timecode=None, frames=stats['Duration-Frames'])
            print('Start frame is: ' + str(start_tc_frame))
            print('Duration frames are: ' + str(duration_frames))
            end_frame = start_tc_frame + duration_frames
            print('End frame is: ' + str(end_frame.frames))
            print('Looking for frame: ' + str(looking_for.frames))
            if looking_for.frames in range(start_tc_frame.frames, end_frame.frames):
                abs_time = looking_for - start_tc_frame
                abs_time.set_fractional(True)
                print('Asking ffmpeg for frame: ' + str(abs_time))
                make_thumb(clip, TEST_OUTPUT, abs_time, stats)
            else:
                print('Cannot find requested timecode in: ' + clip.name)
        elif clip.suffix.lower() == '.mp4':
            # Deal with A7s shit here
        elif clip.suffix.lower() == '.mxf':
            # Deal with sony and other mxf cameras here


if __name__ == '__main__':
    fire.Fire(grab)
