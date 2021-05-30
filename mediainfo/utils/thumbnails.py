from pathlib import Path
import ffmpeg
from ffprobe3 import ffprobe
import shutil

luts = {
    'Arri': '/Users/admin/PycharmProjects/Data_Management/mediainfo/utils/ARRI_LogC2Video_709_davinci3d_33.cube',
    'Sony': '/Users/admin/PycharmProjects/Data_Management/mediainfo/utils/ARRI_LogC2Video_709_davinci3d_33.cube'
}


def get_lut(camera):
    if camera == 'Sony':
        return luts['Sony']
    elif camera == 'Arri':
        return luts['Arri']


def thumb_to_df(file: Path, output_dir: Path, seek_time: str, media_stats: dict, width='150'):
    # seek_time should be formated "00:01" or similar
    if are_drives_connected(output_dir) is False:
        print('Making thumb dir:' + str(output_dir))
        Path.mkdir(output_dir)
    print('input file: ' + str(file))
    try:
        output_file = output_dir.joinpath(file.stem + '.jpg')
        (
            ffmpeg
                .input(str(file), t=seek_time)
                .filter('scale', '1920', -1)
                .filter('lut3d', get_lut(media_stats['Manufacturer']))
                .output(str(output_file), vframes=1)
                .overwrite_output()
                .run()
        )
        html = '<img src="' + str(output_file) + '" width="{width}" >'.format(width=width)
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
