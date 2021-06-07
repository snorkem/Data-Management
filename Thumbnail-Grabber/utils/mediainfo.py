#!/usr/env python3.9
import json
import os
import re
import shlex
import subprocess
from datetime import datetime
from glob import glob
from pathlib import Path
import pandas as pd
import xmltodict
from IPython.display import display, HTML
from pymediainfo import MediaInfo
from utils.thumbnails import thumb_to_df

camera_dict = {  # These letters indicate camera used and the folder structure to navigate in order to find footage.
    'A7s': ('D', 'E', 'F', 'G', 'L'),  # A7s or similar structure
    'FX3': ('N', 'K'),
    'Alexa': ('A', 'B'),
}

def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return round(total_size / 1024 ** 3, 2)


def get_startTC(video_path: Path):
    # only works on alexa footage right now
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(str(video_path))
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)
    output0 = ffprobeOutput['streams'][0]
    output1 = ffprobeOutput['streams'][1]
    for i in ffprobeOutput:
        for x in ffprobeOutput[i]:
            print(x)
    timecode = output1['tags']['timecode']
    duration_frames = output0['nb_frames']
    timecode_info = {'Start TC': timecode,
                     'Duration in Frames': str(duration_frames),
                     }
    print('duration is: ' + str(duration_frames))
    return timecode_info


def get_media_info(file: Path, camera_letter: str):
    media_stats = {
        'Thumbnail': 'Unknown', 'Name': 'Unknown', 'First File Name': 'Unknown', 'Manufacturer': 'Unknown', 'Size (GiB)': 'Unknown', 'Format': 'Unknown',
        'Bitrate': 'Unknown', 'Frame Rate': 'Unknown', 'Width': 'Unknown', 'Height': 'Unknown',
        'Color Primaries': 'Unknown', 'White Balance': 'Unknown',  'Gamma': 'Unknown', 'Bit Depth': 'Unknown',
        'ISO/ASA': 'Unknown'
        }
    if camera_letter in camera_dict['A7s'] or camera_letter == 'A7s':  # A7siii footage or similar
        media_stats.update({'Name': dirname.name})
        media_info = MediaInfo.parse(file)
        try:
            xmlfile = file.with_name(file.stem + 'M01.xml')
            with open(xmlfile) as f:
                xml = xmltodict.parse(f.read())
                capture_gamma_equation = xml['NonRealTimeMeta']['AcquisitionRecord']['Group']['Item'][0]['@value']
                capture_color_primaries = xml['NonRealTimeMeta']['AcquisitionRecord']['Group']['Item'][1]['@value']
        except Exception as e:
            print('Error accessing Sony XML file for folder: {f}'.format(f=dirname))
            print(e)
        for track in media_info.video_tracks:
            # print(track.to_data())
            media_stats.update({
                'Size (GiB)': str(get_size(dirname)),
                'Manufacturer': 'Sony',
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

    elif camera_letter in camera_dict['FX3'] or camera_letter == 'FX3':  # FX3 Footage or similar
        media_stats.update({'Name': dirname.name})
        media_info = MediaInfo.parse(file)
        try:
            xmlfile = file.with_name(file.stem + 'M01.xml')
            with open(xmlfile) as f:
                xml = xmltodict.parse(f.read())
                capture_gamma_equation = xml['NonRealTimeMeta']['AcquisitionRecord']['Group']['Item'][0]['@value']
                capture_color_primaries = xml['NonRealTimeMeta']['AcquisitionRecord']['Group']['Item'][1]['@value']
        except Exception as e:
            print('Error accessing Sony XML file for folder: {f}'.format(f=dirname))
            print(e)
        for track in media_info.video_tracks:
            media_stats.update({
                'Size (GiB)': str(get_size(dirname)),
                'First File Name': file.name,
                'Manufacturer': 'Sony',
                'Format': str(track.to_data()['format']),
                'Color Primaries': capture_color_primaries,
                'Gamma': capture_gamma_equation,
                'Bitrate': track.to_data()['other_bit_rate'][0],
                'Frame Rate': str(track.to_data()['frame_rate']),
                'Width': str(track.to_data()['other_width'][0]),
                'Height': str(track.to_data()['other_height'][0]),
                'Bit Depth': str(track.to_data()['bit_depth']) + 'bits, '
                             + str(track.to_data()['chroma_subsampling'])})

    elif camera_letter in camera_dict['Alexa'] or camera_letter == 'Alexa':  # Alexa footage
        media_stats.update({
            'Name': file.parent.parent.name
        })
        timecode_info = get_startTC(file)
        media_info = MediaInfo.parse(file)
        for track in media_info.general_tracks:
            # print(track.to_data())
            media_stats.update({
                'Size (GiB)': str(get_size(file)),
                'First File Name': file.name,
                'Manufacturer': 'Arri',
                'Format': str(track.to_data()['video_format_list']),
                'Bitrate': str(track.to_data()['other_overall_bit_rate'][0]),
                'Frame Rate': str(int(track.to_data()['comarricamerasensorfps']) / 1000),
                'Width': str(track.to_data()['comarricameraframelinerect1awidth']),
                'Height': str(track.to_data()['comarricameraframelinerect1aheight']),
                'Gamma': str(track.to_data()['comarricameracolorgammasxs']),
                'White Balance': str(track.to_data()['comarricamerawhitebalancekelvin']),
                'ISO/ASA': str(track.to_data()['comarricameraexposureindexasa']),
                'Start TC': timecode_info['Start TC'],
                'Duration-Frames': int(timecode_info['Duration in Frames'])})
        for track in media_info.video_tracks:
            media_stats.update({'Color Primaries': str(track.to_data()['color_primaries']),
                                'Bit Depth': track.to_data()['chroma_subsampling']})
    else:
        media_stats.update({
            'Name': file.parent.parent.name
        })
    return media_stats
