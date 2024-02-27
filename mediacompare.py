#!python3
#
# Wrapper around mediainfo that enables comparing two files side-by-side
#

import subprocess
import json
import argparse
from collections import OrderedDict
import os

# Parse the command line arguments
#
parser = argparse.ArgumentParser(description='Wrapper for mediainfo to compare two files side-by-side')
parser.set_defaults(v=False)
parser.add_argument('-v', '--verbose', required=False,
                    dest='verbose', default=False, action='store_true',
                    help='Include verbose debugging output. You\'ll regret it.')
parser.add_argument('-s', '--short', required=False,
                    dest='short', default=False, action='store_true',
                    help='Truncate long lines instead of wrapping them.')
parser.add_argument('file1',
                    help='The first media file.')
parser.add_argument('file2',
                    help='The second media file.')
args = parser.parse_args()
# logging output to validate arguments are read correctly
if args.verbose: print('file 1 = ' + args.file1)
if args.verbose: print('file 2 = ' + args.file2)
if args.verbose: print('')


# Execute mediainfo, capture json output into a dict
#
def get_mediainfo(media_file):
    try:
        # Run mediainfo command and capture json output
        if args.verbose: print('Executing mediainfo...')
        result = subprocess.run(['mediainfo', '--Output=JSON', media_file], capture_output=True, text=True, check=True)
        if args.verbose: print('Captured this output:\n'+result.stdout+'\n\n')

        # Parse JSON output into a dictionary
        media_info_dict = json.loads(result.stdout)
        if args.verbose: print('Now as a dict:\n'+json.dumps(media_info_dict['media'],indent=2)+'\n\n')
        # Reformat the data a little to make it more cleaner
        name = media_info_dict['media']['@ref']
        new_item = new_item = {'@type': 'File', 'Name': name}
        track = media_info_dict['media']['track']
        track.insert(0,new_item)

        if args.verbose: print('Cleaned up into:\n'+json.dumps(track,indent=2)+'\n\n')

        return track

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


# Convert the output into a more proper format
#
def order_the_dict(list1):
    if args.verbose: print('Converting list to OrderedDict...')
    v = a = s = m = 0
    data = OrderedDict()
    # Label each stream and keep count in case there are more than one stream of that type
    for stream in list1:
        if stream['@type'] == 'File':
            key = 'f'
        elif stream['@type'] == 'General':
            key = 'g'
        elif stream['@type'] == 'Video':
            key = 'v' + str(v)
            v += 1
        elif stream['@type'] == 'Audio':
            key = 'a' + str(a)
            a += 1
        elif stream['@type'] == 'Text':
            key = 's' + str(s)
            s += 1
        elif stream['@type'] == 'Menu':
            key = 'm' + str(s)
            s += 1
        else:
            if args.verbose: print('Im lost')
        data[key] = stream 

    if args.verbose: print('Converted into:\n'+json.dumps(data,indent=2)+'\n\n')

    return data

# Combine the two outputs into a single mess
#
def merge_media_info(list1, list2):
    if args.verbose: print('Merging outputs...')
    dict1 = order_the_dict(list1)
    dict2 = order_the_dict(list2)
    # Get an ordered list of all the streams
    all_streams = OrderedDict()
    all_streams.update(dict.fromkeys(dict1.keys()))
    all_streams.update(dict.fromkeys(dict2.keys()))
    if args.verbose: print('Combined list of streams: ' + json.dumps(all_streams,indent=2)+'\n\n')
    # Prebuild the merged dict with the streams so they appear in the dict in order
    merged_dict = OrderedDict()
    for stream in all_streams:
        merged_dict[stream] = OrderedDict()
        if stream in dict1.keys():
            for subkey in dict1[stream].keys():
                merged_dict[stream][subkey] = (dict1[stream][subkey],"")
        if stream in dict2.keys():
            for subkey in dict2[stream].keys():
                if subkey not in merged_dict[stream].keys():
                    merged_dict[stream][subkey] = ("",dict2[stream][subkey])
                else:
                    merged_dict[stream][subkey] = (dict1[stream][subkey],dict2[stream][subkey]) 
            
    if args.verbose: print('Merged into:\n'+json.dumps(merged_dict,indent=2)+'\n\n')

    return merged_dict


# Splits a string into substrings of maximum length,
# breaking at whitespace if possible.
# 
def split_string(string, length):
    if args.verbose: print('Splitting a string...')
    if args.verbose: print('arrived as: ' + string)

    # Initialize variables
    substrings = []
    start_index = 0

    # Continue until all characters are processed
    while start_index < len(string):
        # Find the end index for the substring
        end_index = start_index + length
        if end_index >= len(string):
            end_index = len(string)
        else:
            # Check if the next character is whitespace
            while end_index > start_index and not string[end_index].isspace():
                end_index -= 1
            # If no whitespace found, use original end index
            if end_index == start_index:
                end_index = start_index + length

        # Add substring to the list
        substrings.append(string[start_index:end_index])

        # Update start index for next substring
        start_index = end_index

    if args.verbose: print('is now: ' + str(substrings))

    return substrings


# Print the output into columns
#
def print_media_info(merged_info):
    if args.verbose: print('Printing outputs...')

    # Define the maximum width for each column
    screen_width, screen_height = os.get_terminal_size()
    skl = 35
    v1l = 50
    v2l = 50
    if args.verbose: print('screen is ' + str(screen_width) + ' characters wide')
    if screen_width > 120:
        skl = 35
        v1l = v2l = (screen_width - skl - 10) // 2
    else:
        skl = 20
        v1l = v2l = ((screen_width - skl - 8) // 2) 
    if args.verbose: print('column widths will be ' + str(skl) + ', ' + str(v1l) + ', and ' + str(v2l))


    # Print the output in three columns with proper alignment and text wrapping
    for key, value in merged_info.items():
        print('\nStream {}: '.format(key))
        # for each element of a stream's metadata
        for subkey, subvalue in value.items():
            # split each string into a list of strings each no longer than max column width
            sk = split_string(str(subkey),skl)
            v1 = split_string(str(subvalue[0]),v1l)
            v2 = split_string(str(subvalue[1]),v2l)
            # count how many parts there are to the now split of strings
            if args.short:
                lines = 1
            else:
                lines = max(len(sk), len(v1), len(v2))
            # print that many lines, with each string in its place
            for i in range(lines):
                s1 = sk[i] if i < len(sk) else ""
                s2 = v1[i] if i < len(v1) else ""
                s3 = v2[i] if i < len(v2) else ""
                print("  {:<{skl}} : {:<{v1l}} : {:<{v2l}}".format(s1, s2, s3, skl=skl, v1l=v1l, v2l=v2l))


# Start doing stuff
#
media_info1 = get_mediainfo(args.file1)
media_info2 = get_mediainfo(args.file2)

if media_info1 and media_info2:
    merged_info = merge_media_info(media_info1, media_info2)
    print_media_info(merged_info)

