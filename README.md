# music-shuffler

music-shuffler creates playlists based on the BPM of a track, and it also emphasizes artist variety.

### Background
I didn't like how the Apple music app shuffled music, and I wanted a playlist that had smoother transitions between tracks. When DJs mix music, they typically change the BPM up or down by 5% from the current track, so I used that as a rule of thumb for selecting the next track. The sorting algorithm also adds artists that aren't in the playlist yet to have a good representation of artists.

### Installation
Run `pip install -r requirements-dev.txt` to install the project dependencies. You can test the build by running `make test`.

### Usage
Run `python music_shuffler/shuffler.py -h` to bring up the help prompt.

### To Dos
Apple music unfortunately does not have BPM information for tracks, unless you tag it manually. Eventually, I'd like to have the input and output file generated in a format that is easily importable to my library.
