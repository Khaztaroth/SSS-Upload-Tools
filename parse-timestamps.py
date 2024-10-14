from tkinter.filedialog import askopenfilename
from pathlib import Path

# Promting file menu and storing file name.
csv_file = askopenfilename()
text_file = (f'{Path(csv_file).stem}.txt')

import csv

with open(csv_file, 'r') as input:
    reader = csv.DictReader(input)
    rows = list(reader)

ad_label = {'Lemon'}
chapter_label = {'Yellow', 'Red'}
warning_label = {'Purple'}
highlight_label = {'Blue'}

#Checking for frame count, if it's higher or equal than 30 it adds a second to the timestamp, rippling the changes to minutes and hours.
def increment_time(time_str, color):
    hours, minutes, seconds, frames = map(int, time_str.split(':'))
    
    #Frames are not written as zero because we are converting from 60fps timecodes to 30fps 
    if frames >= 30:
         frames - 30
         seconds +=1
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        hours += 1

    #Only hours, minutes, and seconds are returned for most labels. YouTube does not use frame count for chapter markers.
    if color not in ad_label:
        return '{:01d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    #For ad labels, frames do matter
    else: return '{:01d}:{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds, frames)

#Initializing marker lists
chapter_markers = []
warning_markers = []
ad_markers = []
highlight_markers = []
markers = []

with open(text_file, 'w') as output:
    #Append marker to each group to separate by usecase
    for column in rows:
        #Ad labels only need the start time
        if column['Color'] in ad_label:
            ad_markers.append([increment_time(column['Record In'], column['Color']), column['Notes']])
        #Chapter labels only write the time they start as the next one dictates when the previous stop
        if column['Color'] in chapter_label:
            chapter_markers.append([increment_time(column['Record In'], column['Color']), column['Notes']])
        #Warning labels for the comment section are written as a set of start and end for clarity 
        if column['Color'] in warning_label:
            warning_markers.append([column['Notes'], increment_time(column['Record In'], column['Color']), '-', increment_time(column['Record Out'], column['Color'])])
        #Highlighted moments work just like warnings
        if column['Color'] in highlight_label:
            highlightIn = increment_time(column['Record In'], column['Color'])
            highlightOut = increment_time(column['Record Out'], column['Color'])
            if (highlightIn != highlightOut):
                highlight_markers.append([column['Notes'], highlightIn, '-', highlightOut])
            else: 
                highlight_markers.append([column['Notes'], highlightIn])

    #Grouping markers into a single list
    if ad_markers:
        markers.append(ad_markers)
    if chapter_markers:
        markers.append(chapter_markers)
    if warning_markers:
        markers.append(warning_markers)
    if highlight_markers:
        markers.append(highlight_markers)

    #Iterating through the lists of markers and writing each row
    #It skips adding a new line once it's done with all the item lists
    index = 0
    for list in markers:
        for row in list:
            output.write(' '.join(row) + '\n')
        index += 1
        if index < len(markers):
            output.write('\n')
            
#Open file in default editor
import os
os.startfile(text_file)
