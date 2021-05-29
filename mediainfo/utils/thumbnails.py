from pathlib import Path
import ffmpeg
from ffprobe3 import ffprobe
import shutil

# Working test code!
'''(
    ffmpeg
    .input('/Users/admin/Desktop/Scott_Good_Timelapse_v4_ProRes422HQ_1080p.mov', ss='00:01')
    .filter('scale', '1920', -1)
    .output('/Users/admin/Desktop/test2.jpg', vframes=1)
    .run()
)'''


def thumb_to_df(file: Path, output_dir: Path, seek_time: str, width='60'):
    # seek_time should be formated "00:01" or similar
    print('output dir ' + str(output_dir))
    if are_drives_connected(output_dir) is False:
        print('Making thumb dir:' + str(output_dir))
        Path.mkdir(output_dir)
    print('input file: ' + str(file))
    try:
        output_file = output_dir.joinpath(file.stem + '.jpg')
        print(output_file)
        (
            ffmpeg
                .input(str(file), t=seek_time)
                .filter('scale', '1920', -1)
                .output(str(output_file), vframes=1)
                .overwrite_output()
                .run()
        )
        html = '<img src="' + str(output_file) + '" width="150" >'
        return html
    except Exception as e:
        print('Could not get thumbnail!')
        print(e)
        return None


def are_drives_connected(output_dir: Path):
    if output_dir.exists() and output_dir.is_dir():
        print('Thumbnail path exists')
        return True
    else:
        return False
