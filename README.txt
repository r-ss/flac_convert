=========================
Batch convert FLAC to MP3
=========================

I use this script to convert my lossess music collection
to mp3 format for some devices, which doesn't have FLAC support
or enough storage space.

I organize my music to directories with "Artist - Album [year]" format
which contain songs named as "01 - Artist - Title.flac".
Each directory have an 500x500px JPEG artwork named "folder.jpg".
Very often also included CUE and LOG files and additional artwork
This script ignores all but FLACS, resizes "folder.jpg" to 300x300px
and embeds it to the MP3s as album artwork.
Script doesn't make any changes in input directory.


for example, i have:
Autechre - Amber [1994] /  01 - Autechre - Foil.flac
                           02 - Autechre - Montreal.flac
                           03 - Autechre - Silverside.flac
                           scans/
                           cue.cue
                           log.log
                           folder.jpg
VA - Back and 4th [2011] / CD1 / 1 - Sepalcure - Taking You Back.flac
                                 2 - Boxcutter - LOADtime.flac
                                 3 - Boddika - Warehouse.flac
                                 cue.cue
                                 log.log
                           CD2 / 1 - Mount Kimbie - Sketch On Glass.flac
                                 2 - Scuba - Twitch (Jamie Vex'd Remix).flac
                                 3 - Joy Orbison - Hyph Mngo.flac
                                 cue.cue
                                 log.log
                           folder.jpg

and after convert:
Autechre - Amber [1994] /  01 - Autechre - Foil.mp3
                           02 - Autechre - Montreal.mp3
                           03 - Autechre - Silverside.mp3
VA - Back and 4th [2011] / CD1 / 1 - Sepalcure - Taking You Back.mp3
                                 2 - Boxcutter - LOADtime.mp3
                                 3 - Boddika - Warehouse.mp3
                           CD2 / 1 - Mount Kimbie - Sketch On Glass.mp3
                                 2 - Scuba - Twitch (Jamie Vex'd Remix).mp3
                                 3 - Joy Orbison - Hyph Mngo.mp3

Requirements
============

The script is in Python and it uses the binaries:

- flac: decode flac files
- lame: encode mp3 file
- metaflac: pulling metadata from flac file like Artist, Album, Title
- id3v2: save metadata to mp3 file