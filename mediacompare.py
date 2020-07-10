#!/opt/python/bin/python
#
# Wrapper around mediainfo that enables comparing two files side-by-side
#
# Known issues:
#    - It only compares the first video and audio stream it finds, 2nd+ are ignored, 
#    - It outputs to three columns to provide a side-by-side view, but column widths aren't pretty
#    - Column width is set up the 'General:Complete_name' field, and field longer will get truncated
#      This affects the 'Video:Encoding_settings' and a few other fields. Is by design. 
#    - It tries to keep the order, but fields in the 2nd file not present in the 1st get shuffled
#      to the bottom rather than injected into the middle. I'm not sure how to clean that up.
# Future ideas:
#    - only print out interesting fields, drop things like 'Encoding_settings'
#    - add a -t option that creates a tab-separated output instead of columns, won't need to truncate
#
from collections import OrderedDict
from collections import defaultdict
import subprocess
import lxml
import argparse
import xmltodict
import json
# Parse the command line arguments
#
parser = argparse.ArgumentParser(description='Wrapper for mediainfo to compare two files side-by-side')
parser.set_defaults(v=False)
parser.add_argument('-v', '--verbose', required=False,
                    dest='verbose', default=False, action='store_true',
                    help='include verbose debugging output')
parser.add_argument('file1',
                    help='the first media file')
parser.add_argument('file2',
                    help='the second media file')
args = parser.parse_args()
# logging output to validate arguments are read correctly
if args.verbose: print('file 1 = ' + args.file1)
if args.verbose: print('file 2 = ' + args.file2)
if args.verbose: print('')

# execute mediainfo against specified file
#
def exec_mediainfo(file):
    mediainfo_out = subprocess.Popen(['mediainfo','--output=XML',file],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
    returncode = mediainfo_out.wait()
    #logging output to validate mediainfo execution produced what we expected
    if args.verbose: print('mediainfo returned {0}'.format(returncode))
    if args.verbose: print('mediainfo for ' + file)# + ':\n' + mediainfo_out.stdout.read())
    # put the output in 'tracks', trim off the top layers of the tree
    output = mediainfo_out.stdout.read()
    x2dict = xmltodict.parse(output)
    tracks = x2dict['Mediainfo']['File']['track']
    # tracks is a list of dict, one list item per track with dict items per data point
    # next block converts the list to a dict using track id as the key
    # this allows us to compare files with different numbers of tracks 
    if args.verbose: print('Converting XML to dict...')
    data = OrderedDict()
    for track in tracks:
        if track['@type'] == 'General':
            key = 'g'
        elif track['@type'] == 'Video':
            key = 'v' + str(track['ID'])
        elif track['@type'] == 'Audio':
            key = 'a' + str(track['ID'])
        elif track['@type'] == 'Text':
            key = 's' + str(track['ID'])
        else:
            if args.verbose: print('Im lost')
        if args.verbose: print('Processing track: ' + key)
        if args.verbose: print(str(track.items()))
        data[key] = track 
    # now return the dict of dict with track data
    #if args.verbose: print('Returning this: ' + str(data))
    return data
#
# end of exec_mediainfo()

# merge two dicts where {k1:v1} + {k1:v2} = {k1:[v1,v2]}
#
def merge_dict(dict1,dict2):
    if args.verbose: print('dict1: ' + str(dict1))
    if args.verbose: print('dict2: ' + str(dict2))
    # prepare to catch
    dict3 = OrderedDict()
    # iterate through first dict, create all the keys and blanks for the other dict
    for k, v in dict1.iteritems():
        dict3[k] = [v,'']
    # iterate through second dict, update or add depending on if key already exists
    for k, v in dict2.iteritems():
        if k in dict3:
            dict3[k][1] = v 
        else:
            dict3[k] = ['',v]
    return dict3
#
# end of merge_dict()

# get the data from both files into dictionaries
#
if args.verbose: print('Executing mediainfo...')
mediainfo1 = exec_mediainfo(args.file1)
mediainfo2 = exec_mediainfo(args.file2)

# merge the two dictionaries together
#
if args.verbose: print('Merging data...')
# setup a new dict to catch, with tracks in correct order
# if left on its own they got out of order, so hard coding them to force the order
bothinfo = OrderedDict()
bothinfo['g'] = ''
bothinfo['v1'] = ''
bothinfo['a2'] = ''
# step through each track, combining the two inputs
for tracks in bothinfo:
    track = merge_dict(mediainfo1[tracks],mediainfo2[tracks])
    bothinfo[tracks] = track 
if args.verbose: print('Merged: ')
if args.verbose: print(json.dumps(bothinfo,indent=2))


# print out the results
#
if args.verbose: print('Output time...')
# set column widths using file name as the width to match
# painfully long lines (e.g. 'Unique_ID', 'Encoding_settings') get truncated
c1 = c2 = c3 = 20
for track in bothinfo:
    for key in bothinfo[track].keys():
        if len(key) > c1: c1 = len(key) + 2
c2 = len(bothinfo['g']['Complete_name'][0])
c3 = len(bothinfo['g']['Complete_name'][1])
for track in bothinfo:
    print('')
    if args.verbose: print('Column widths: ' + str(c1) + ', ' + str(c2) + ', ' + str(c3))
    for key, values in bothinfo[track].iteritems():
        print("{k:<{c1}}\t".format(k=key, c1=c1) +
              "{v1:<{c2}.{t2}}\t".format(v1=str(values[0]), c2=c2, t2=c2) +
              "{v2:<{c3}.{t3}}".format(v2=str(values[1]), c3=c3, t3=c3))


