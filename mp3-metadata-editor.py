from argparse import ArgumentParser
from pathlib import Path
import eyed3 as ed3
import re
from typing import Tuple

def main() -> None:

    parser = ArgumentParser()

    parser.add_argument('file')
    parser.add_argument('-a', '--artist',
        action='store', required=False)
    parser.add_argument('-i', '--image', required=False)

    args = parser.parse_args()

    if args.file.endswith('.txt'):
        with open(args.file) as file:
            files = [line.rstrip() for line in file.readlines()]
    else: files = [args.file]

    for file in files:

        if '\"' in file: file = file.replace('\"', '')
        print(f'On file: {file}')
        em = ExtractMetadata(args.artist, file)
        em.find_number()
        title, ep_number = em.return_metadata()
        mp3me = MP3MetadataEditor(mp3=file, title=title, artist=args.artist,
                                  episode_num=ep_number, artwork=args.image)
        mp3me.add_metadata()
        mp3me.save()

class ExtractMetadata:
    '''Extract file metadata from file name'''
    def __init__(self, artist: str, mp3: Path):

        self.mp3 = mp3
        self.artist = artist
        self.title = ''
        self.episode_num = ''

    def format_metadata(self) -> Tuple[str]:
        '''Format metadata for mp3 tag'''
        mp3 = Path(self.mp3).name
        episode, self.title = mp3[:-4].split(' - ', maxsplit=1)
        return episode

    def find_number(self) -> None:
        '''Find the mp3 track number'''
        episode  = self.format_metadata()
        self.episode_num = re.findall('\\d+', episode)[0]

    def return_metadata(self) -> Tuple[str]:
        '''Returns a Tuple of formatted metadata'''
        return (self.title, self.episode_num)

class MP3MetadataEditor:
    '''Editor for mp3 file metadata'''
    def __init__(self, mp3: Path, title: str, artist: str,
                 episode_num: str, artwork: Path = None):

        self.audio_file = ed3.load(mp3)
        self.title = title
        self.artist = artist
        self.episode_num = episode_num
        self.artwork = open(artwork, 'rb').read()

    def metadata(self) -> str:
        '''Return metadata if it exists'''
        if self.audio_file.tag:
            return self.audio_file.tag.frame_set

    def add_metadata(self) -> None:
        '''Add metadata to mp3 file'''
        self.audio_file.initTag()
        self.audio_file.tag.artist = self.artist
        self.audio_file.tag.title = self.title
        self.audio_file.tag.album_artist = self.artist
        self.audio_file.tag.track_num = self.episode_num
        self.audio_file.tag.album = f'{self.artist} Podcast'

        if self.artwork is not None:
            self.audio_file.tag.images.set(3, self.artwork, 'image/jpg')
    def save(self) -> None:
        '''Save metadata back to original file'''
        self.audio_file.tag.save()

if __name__ == '__main__':
    main()
