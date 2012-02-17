#!/usr/bin/env python

import os
import re
import subprocess
import time
from subprocess import Popen, PIPE
try:
    from PIL import Image
except ImportError:
    import Image


dry_run = False
#dry_run = True

# Set directories
dir_source =      '/home/ress/h1/music/lossless/'
dir_destination = '/home/ress/h1/music/lossy_duplicates/'
dir_temp =        '/dev/shm/' #ramdisk

# I use this script on fanless home server, this pause for prevent overheating.
# set to 0 for max performance
sleep_seconds = 20

artwork_temp_path = '%sartwork.jpg' % dir_temp
lossless_extentions = re.compile('\.(flac?|FLAC)$')
lossy_extentions = re.compile('\.(mp3?|MP3)$')
files_total = 0
files_converted = 0

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

def escape_path(string):
    string = re.escape(string)
    return string
    
def to_unicode(string):
    return unicode(string, errors='ignore')

def convert(source_path, destination_path, artwork_path):
    if not dry_run:
        subprocess.call(['clear'], shell=True)
        print 'CONVERTING'
        flac_artist = get_flac_tag('ARTIST',      source_path)
        flac_album  = get_flac_tag('ALBUM',       source_path)
        flac_title  = get_flac_tag('TITLE',       source_path)
        flac_track  = get_flac_tag('TRACKNUMBER', source_path)
        flac_genre  = get_flac_tag('GENRE',       source_path)
        flac_date   = get_flac_tag('DATE',        source_path)
        print "flac artist=%s  album=%s title=%s track=%s genre=%s date=%s" % (
                flac_artist, flac_album, flac_title,
                flac_track, flac_genre, flac_date)
        title = flac_title or source_path.replace('.flac', '')
        mp3_artist = flac_artist or artist
        mp3_album  = flac_album  or album
        mp3_title  = flac_title  or title
        print "mp3  artist=%s  album=%s title=%s" % (
                mp3_artist, mp3_album, mp3_title)
        subprocess.call(['flac -d -o "%strack.wav" "%s"' % (dir_temp, source_path)], shell=True)
        print escape_path(destination_path)
    
        if check_file_exists(artwork_path):
            image = Image.open(artwork_path)
            image.thumbnail((300,300), Image.ANTIALIAS)
            image.save(artwork_temp_path, image.format, quality=75)
            del image
            
            
            subprocess.call(['lame -V2 --ti %s %strack.wav %s' % (escape_path(artwork_temp_path), dir_temp, escape_path(destination_path))], shell=True)
        else:
            subprocess.call(['lame -V2 %strack.wav %s' % (dir_temp, escape_path(destination_path))], shell=True)
            
        id3out = Popen(["id3v2",
                            "--artist", to_unicode(mp3_artist),
                            "--album",  to_unicode(mp3_album),
                            "--song",   to_unicode(mp3_title),
                            "--track",  flac_track,
                            "--genre",  flac_genre,
                            "--year",   flac_date,
                            destination_path], stdout=PIPE).communicate()[0]
        if check_file_exists(artwork_temp_path):
            os.remove(artwork_temp_path)
        delete_file('%strack.wav' % dir_temp)
        
def get_flac_tag(tag, flac_path):
    TAGS = ('ARTIST', 'TITLE', 'ALBUM', 'GENRE', 'TRACKNUMBER', 'DATE')
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
    global files_total, files_converted
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
                        files_converted += 1
                        print 'CONVERTED %d OF %d, %F %%' % (files_converted, files_total, round(1.0 * files_converted / files_total * 100, 3))
                        time.sleep(sleep_seconds)
 
    print 'TOTAL FLAC FOUND: %d' % files_total
    print 'TOTAL FLAC CONVERTED: %d' % files_converted

if __name__ == '__main__':
    subprocess.call(['clear'], shell=True)
    count_flacs()
    walk_source()
