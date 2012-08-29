#!/usr/bin/env python

import os
import re
import subprocess
import time
import datetime
import shutil
import sys
from subprocess import Popen, PIPE
try:
    from PIL import Image
except ImportError:
    import Image

dry_run = False
#dry_run = True

# Set directories
#dir_source =      '/home/ress/h1/music/lossless/'
#dir_destination = '/home/ress/h1/music/lossy_duplicates/'
dir_source =      '/home/ress/flac_convert_tests/in/'
dir_destination = '/home/ress/flac_convert_tests/out/'
dir_temp =        '/dev/shm/' #ramdisk

# I use this script on fanless home server, this pause for prevent overheating.
# set to 0 for max performance
sleep_seconds = 3

artwork_temp_path = '%sartwork.jpg' % dir_temp
lossless_extentions = re.compile('\.(flac?|FLAC)$')
lossy_extentions = re.compile('\.(mp3?|MP3)$')
files_total = 0
files_converted = 0
folders_removed = 0

time_start = 0
time_end = 0

def make_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)

def path_relative(path):
    return path[len(dir_source):]

def delete_file(path):
    if os.path.isfile(path):
        os.remove(path)
        
def check_file_exists(path):
    if os.path.isfile(path):
        return True
    else:
        return False
  
def to_unicode(string):
    return unicode(string, errors='ignore')

def process_path(string):
    encoding = sys.getfilesystemencoding()
    string = string.decode(encoding)
    string = re.escape(string)
    return string

def convert(source_path, destination_path, artwork_path):
    global files_total, files_converted
    subprocess.call(['clear'], shell=True)
    time_now = time.time()
    print 'TIME RUNNING (H:M:S): %s' % str(datetime.timedelta(seconds = time_now - time_start))
    try:
        print 'CONVERTED %d OF %d, %F %%' % (files_converted, files_total, round(1.0 * files_converted / files_total * 100, 3))
        average = (time_now - time_start) / files_converted
        print 'AVERAGE TRACK CONVERTING TIME (SECONDS): %s' % str(average)
        remaining = files_total - files_converted
        print 'TRACKS REMAINING: %d' % remaining
        print 'TIME ESTIMATED (H:M:S): %s' % str(datetime.timedelta(seconds = remaining * average))
    except ZeroDivisionError:
        print 'Zero Division Error xD'


    if not dry_run:
        flac_artist = get_flac_tag('ARTIST', source_path)
        flac_album  = get_flac_tag('ALBUM', source_path)
        flac_title  = get_flac_tag('TITLE', source_path)
        flac_track  = get_flac_tag('TRACKNUMBER', source_path)
        flac_tracktotal = get_flac_tag('TRACKTOTAL', source_path)
        flac_disc = get_flac_tag('DISCNUMBER', source_path)
        flac_disctotal = get_flac_tag('DISCTOTAL', source_path)
        flac_genre = get_flac_tag('GENRE', source_path)
        flac_date = get_flac_tag('DATE', source_path)
        flac_compilation = get_flac_tag('COMPILATION', source_path)
        print 'Artist: %s  |  Album: %s  |  Title: %s' % (flac_artist, flac_album, flac_title)
        title = flac_title or source_path.replace('.flac', '')
        mp3_artist = flac_artist or artist
        mp3_album  = flac_album  or album
        mp3_title  = flac_title  or title
        if check_file_exists('%strack.wav' % dir_temp):
            delete_file('%strack.wav' % dir_temp)

        subprocess.call(['flac -d -o "%strack.wav" "%s"' % (dir_temp, source_path)], shell=True)
        print destination_path
    
        if check_file_exists(artwork_temp_path):
            os.remove(artwork_temp_path)
        if check_file_exists(artwork_path):
            image = Image.open(artwork_path)
            image.thumbnail((500,500), Image.ANTIALIAS)

            # max 128Kb for artwork allowed, so...
            image.save(artwork_temp_path, image.format, quality=90)
            if os.path.getsize(artwork_temp_path) > 131070:
                delete_file(artwork_temp_path)
                image.save(artwork_temp_path, image.format, quality=70)
                if os.path.getsize(artwork_temp_path) > 131070:
                    delete_file(artwork_temp_path)
                    image.save(artwork_temp_path, image.format, quality=50)
                    if os.path.getsize(artwork_temp_path) > 131070:
                        delete_file(artwork_temp_path)
                        image.save(artwork_temp_path, image.format, quality=30)
                        if os.path.getsize(artwork_temp_path) > 131070:
                            delete_file(artwork_temp_path)
                            image.thumbnail((300,300), Image.ANTIALIAS)
                            image.save(artwork_temp_path, image.format, quality=30)
            del image
            subprocess.call([u'lame -V2 --id3v2-only --tg "%s" --tn %s/%s --ty %s --tv TCMP=%s --tv TPOS=%s/%s --ti %s %strack.wav %s' % (flac_genre, flac_track, flac_tracktotal, flac_date, flac_compilation, flac_disc, flac_disctotal, artwork_temp_path, dir_temp, process_path(destination_path))], shell=True)
        else:
            subprocess.call([u'lame -V2 --id3v2-only --tg "%s" --tn %s/%s --ty %s --tv TCMP=%s --tv TPOS=%s/%s %strack.wav %s' % (flac_genre, flac_track, flac_tracktotal, flac_date, flac_compilation, flac_disc, flac_disctotal, dir_temp, process_path(destination_path))], shell=True)

        subprocess.call(['eyeD3 --to-v2.4 -a "%s" -A "%s" -t "%s" %s' % (mp3_artist, mp3_album, mp3_title, re.escape(destination_path))], shell=True)

    files_converted += 1
    time.sleep(sleep_seconds)
        
def get_flac_tag(tag, flac_path):
    TAGS = ('ARTIST', 'TITLE', 'ALBUM', 'GENRE', 'TRACKNUMBER', 'TRACKTOTAL', 'DISCNUMBER', 'DISCTOTAL', 'DATE', 'COMPILATION')
    if not tag in TAGS:
        raise RuntimeError("Tag=%s not valid, use: %s" % (tag, TAGS))
    metaflac = Popen(["metaflac", "--show-tag=%s" % tag, flac_path],
                 stdout=PIPE).communicate()[0]
    if metaflac:
        metaflac = metaflac.split('=')[1].strip()
    return metaflac

def count_flacs():
    global files_total
    for root, dirs, files in os.walk(dir_source):            
        for fn in files:
            if(re.search(lossless_extentions,fn)):
                files_total += 1
    for root, dirs, files in os.walk(dir_destination):            
        for fn in files:
            if(re.search(lossy_extentions,fn)):
                files_total -= 1

def walk_source():
    for root, dirs, files in os.walk(dir_source):            
        for fn in files:
            if not fn.startswith('.'):
                if(re.search(lossless_extentions,fn)):
                    path = os.path.join(root,fn)                
                    path = path_relative(path)                
                    splitted = path.split('/')    
                
                    # create level 1 directories
                    make_directory('%s%s' % (dir_destination, splitted[0]))
                
                    # create level 2 directories
                    if os.path.isdir('%s%s/%s' % (dir_source, splitted[0], splitted[1])):
                        make_directory('%s%s/%s' % (dir_destination, splitted[0], splitted[1]))
                        artwork_path = '%s%s/folder.jpg' % (dir_source, splitted[0])
                        source_file = '%s%s' % (dir_source, path)
                        destination_file = '%s%s/%s/%s.mp3' % (dir_destination, splitted[0], splitted[1], fn[:-5])
                    else:
                        artwork_path = '%s%s/folder.jpg' % (dir_source, splitted[0])
                        source_file = '%s%s' % (dir_source, path)
                        destination_file = '%s%s/%s.mp3' % (dir_destination, splitted[0], fn[:-5])
                
                    if not os.path.exists(destination_file):
                        convert(source_file, destination_file, artwork_path)
                    else:
                        lossless_modified = os.path.getmtime(source_file)
                        lossy_modified = os.path.getmtime(destination_file)
                        if lossless_modified > lossy_modified:
                            os.remove(destination_file)
                            convert(source_file, destination_file, artwork_path)

def walk_destination():
    global folders_removed
    for root, dirs, files in os.walk(dir_destination):
            
        for fn in files:
            if not fn.startswith('.'):
                if(re.search(lossy_extentions,fn)):
                    path = os.path.join(root,fn)                
                    path = path_relative(path)                
                    splitted = path.split('/') 
                    
                    spath = '%s%s%s' % (dir_source, splitted[0], splitted[1])
                    dpath = '%s%s%s' % (dir_destination, splitted[0], splitted[1])
                    
                    if not os.path.exists(spath) and os.path.exists(dpath):
                        if os.path.isdir(dpath):
                            if not dry_run:
                                print 'REMOVING > %s' % dpath
                                time.sleep(3) # For prevent mass-erase =)
                                shutil.rmtree(dpath)
                            folders_removed += 1
    if folders_removed > 0:
        print 'TOTAL FOLDERS REMOVED: %d' % folders_removed

if __name__ == '__main__':
    subprocess.call(['clear'], shell=True)

    count_flacs()

    time_start = time.time()

    walk_source()
    walk_destination()

    time_end = time.time()

    if check_file_exists(artwork_temp_path):
        os.remove(artwork_temp_path)
    if check_file_exists('%strack.wav' % dir_temp):
        delete_file('%strack.wav' % dir_temp)

    print 'TOTAL TIME (H:M:S): %s' % str(datetime.timedelta(seconds = time_end - time_start))
    print 'GOOD BYE'
