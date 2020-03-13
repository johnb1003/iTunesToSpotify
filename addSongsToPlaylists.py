import sys
import spotipy
import spotipy.util as util
import xlrd
import os
import re
import time

SCOPE = 'user-library-read,playlist-modify-private,user-read-private,playlist-modify-public'
REDIRECT_URI = 'http://localhost/'


class Song:
    def __init__(self, title='', time=0, artist=[], album='', genre='', songID='', matchScore=0, playlists=[]):
        self.title = title
        self.time = time
        self.artist = artist
        self.album = album
        self.genre = genre
        self.songID = songID
        self.matchScore = matchScore
        self.returnedResults = 0
        self.playlists = playlists

# Dictionary of (playlist['name']: playlist['id']) tuples
playlistDic = {}

# List of Song objects relating to all songs successfully found on Spotify
allSongsSpotify = []

def main(usr, cid, csec):
    USERNAME = usr
    CLIENT_ID = cid
    CLIENT_SECRET = csec

    # Connect to Spotify API with credentials declared earlier
    token = util.prompt_for_user_token(USERNAME, SCOPE,  client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

    if token:
        sp = spotipy.Spotify(auth=token)

        # Read in Spotify songs found by allSongsSearch.py
        with open('songFound.txt', 'r', encoding="utf8", errors='ignore') as f:
            songList = f.readlines()
            for line in songList:
                songInfo = line.split("\t")
                playlistsList = re.split(", ", str(songInfo[6]).replace('[', '').replace(']', '').replace("'", '').replace(".txt", '').strip())
                artistsList = re.split(", ", str(songInfo[2]).replace('[', '').replace(']', '').replace("'", '').strip())
                newSong = Song(title=str(songInfo[0]).strip(), time=float(songInfo[1]), artist=artistsList, album=str(songInfo[3]), songID=str(songInfo[5]).strip(), playlists=playlistsList)
                allSongsSpotify.append(newSong)
        f.close()


        print("Retrieving current Spotify playlists...")
        # Get list of all current playlists on Spotify and list of all songs in them
        setOff=0
        hasNext = True
        while (hasNext):
            playlists = sp.user_playlists(USERNAME, limit=50, offset=setOff)
            hasNext = not (playlists['next'] == None)
            setOff = playlists['offset'] + 1

            for playlist in playlists['items']:
                setOff2 = 0
                hasNext2 = True

                playlistDic[playlist['name']] = (playlist['id'], [])
                while (hasNext2):
                    playlistTracks = sp.user_playlist_tracks(user=USERNAME, playlist_id=playlist['id'], fields=None, limit=100, offset=setOff2, market='from_token')
                    hasNext2 = not (playlistTracks['next'] == None)
                    setOff2 = playlistTracks['offset'] + 1
                    if(len(playlistTracks['items']) > 0):
                        for track in playlistTracks['items']:
                            playlistDic[playlist['name']][1].append(track['track']['id'].replace("'", '').strip())


        print("Adding songs to appropriate Spotify playlists...")
        # Add songs to playlists depending on if playlist exists / if song is already on playlist
        for song in allSongsSpotify:
            if not (sp.current_user_saved_tracks_contains(tracks=[song.songID.strip()])):
                sp.current_user_saved_tracks_add(tracks=[song.songID.strip()])
            if not song.playlists[0] == '':
                time.sleep(.2)
                for playlist in song.playlists:
                    playlistName = playlist.replace('.txt', '')
                    # Does playlist already exist?
                    if playlistName in playlistDic.keys():
                        if song.songID.strip() not in playlistDic[playlistName][1]:
                            # add song to playlist
                            #print('Adding song %s to playlist %s'%(song.title, playlistName))
                            sp.user_playlist_add_tracks(user=USERNAME, playlist_id=playlistDic[playlistName][0], tracks=[song.songID.strip()])
                            playlistDic[playlistName][1].append(song.songID)
                        else:
                            #print('Song %s already exists in playlist %s'%(song.title, playlistName))
                            pass
                    else:
                        # Create new Playlist and song
                        #print('Creating new playlist %s and adding song %s'%(playlistName, song.title))
                        newPlaylist = sp.user_playlist_create(user=USERNAME, name=playlistName, public=True)
                        sp.user_playlist_add_tracks(user=USERNAME, playlist_id=newPlaylist['id'], tracks=[song.songID.strip()])
                        playlistDic[playlistName] = (newPlaylist['id'], [])
                        playlistDic[playlistName][1].append(song.songID.strip())
        print("Transfer complete!")
    else:
        print("Can't get token for ", USERNAME)    
