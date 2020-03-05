#!/bin/sh
#####
tapeless_path="/Volumes/SEG/S40\ TAPELESS\ MEDIA/ODA/*/"
#####
osascript -e 'display notification "Generating Tapelist" with title "Asher Pink"'
mkdir ~/tapelist
ls -r1 ${tapeless_path} | sed '/SEG/ d'| sed '/^$/N;/^\n$/D'| sed '1!G;h;$!d' > ~/tapelist/tapelist_by_day.txt
sed '/ADC/!d' ~/tapelist/tapelist_by_day.txt > ~/tapelist/tapelist_by_camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/AMI/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/BLK/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/^CC/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/DRN/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/OSM/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/RED/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/SA7/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/SD/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed '/WAV/!d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
echo >> ~/tapelist/Tapelist_By_Camera.txt
sed -e '/WA/!d' -e '/WAV/d' ~/tapelist/tapelist_by_day.txt >> ~/tapelist/Tapelist_By_Camera.txt
afplay /System/Library/PrivateFrameworks/ScreenReader.framework/Versions/A/Resources/Sounds/DrillOut.aiff
open ~/tapelist/tapelist_by_camera.txt 
open ~/tapelist/tapelist_by_day.txt 