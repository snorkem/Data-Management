#!/bin/sh
#-- Set Volume Path Variables --#
g_rack_path="/Volumes/SEG/S41\ TAPELESS\ MEDIA"
g_shuttle_path="/Volumes/S41\ G-SPEED\ Shuttle\ XL/S41\ TAPELESS\ MEDIA"
#-- End Variables --#

osascript -e 'display notification "Comparing Drives" with title "Asher Pink"'
afplay /System/Library/PrivateFrameworks/ScreenReader.framework/Versions/A/Resources/Sounds/PopupAppeared.aiff

mkdir ~/treecheck

#cd /Volumes/S40\ G-SPEED\ Shuttle\ XL/S40\ TAPELESS\ MEDIA
cd ${g_shuttle_path}
ls -R > ~/treecheck/gspeed_dir_temp.txt

sed '/RMD/ d' ~/treecheck/gspeed_dir_temp.txt > ~/treecheck/gspeed_dir.txt

rm ~/treecheck/gspeed_dir_temp.txt

#cd /Volumes/SEG/S40\ TAPELESS\ MEDIA
cd ${g_rack_path}
ls -R > ~/treecheck/grack_dir_temp.txt

sed '/RMD/ d' ~/treecheck/grack_dir_temp.txt > ~/treecheck/grack_dir.txt

rm ~/treecheck/grack_dir_temp.txt

diff ~/treecheck/gspeed_dir.txt ~/treecheck/grack_dir.txt > ~/treecheck/tapeless_dir.txt

diff -y ~/treecheck/gspeed_dir.txt ~/treecheck/grack_dir.txt > ~/treecheck/tapeless_dir_Detailed.txt

afplay /System/Library/PrivateFrameworks/ScreenReader.framework/Versions/A/Resources/Sounds/DrillOut.aiff

osascript -e 'display notification "Compare Complete" with title "Asher Pink"'

open ~/treecheck/tapeless_dir.txt

osascript -e 'display alert "Compare Complete" message "Time to check your work. Left carrot means that the asset is on the G-Speed and not the G-Rack. Right carrot means that the asset is on the G-Rack and not the G-Speed. If the document is blank, both drives are paired."'
