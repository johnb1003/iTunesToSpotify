import sys
import spotipy
import spotipy.util as util
import xlrd
import os
import re

SCOPE = 'user-library-read,playlist-modify-private,user-read-private,playlist-modify-public'
REDIRECT_URI = 'http://localhost/'


# Dictionary of (playlist['name']: playlist['id'], []) tuples
playlistDic = {}

# Dictionary of (song['name']: songID) tuples
spotifyDic = {}

# List of Song objects relating to all songs in iTunes Library
allSongsiTunes = []

# List of Song objects relating to all songs successfully found on Spotify
allSongsSpotify = []

# Minimum score needed to determine if a song is a valid match from matchScore
MIN_MATCH_SCORE = .5


class Song:
    def __init__(self, title='', time=0, artist=[], album='', genre='', songID='', matchScore=0):
        self.title = title
        self.time = float(time)
        self.artist = artist
        self.album = album
        self.genre = genre
        self.songID = songID
        self.matchScore = matchScore
        self.returnedResults = 0
        self.playlists = []



def getSongID(iTunesSong, sp):
    spotifySearchResults = []
    query = '"%s" %s' % (iTunesSong.title, iTunesSong.artist)
    result = sp.search(query, limit=3, offset=0, type='track', market='from_token')
    spotifySong = Song()

    #Check if results are valid / pick correct item from result (to get Song ID from)
    if (len(result['tracks']['items'])>0):
        for item in result['tracks']['items']:
            albumName = item['album']['name']
            artistsJSON = item['artists']
            artists = []
            for artist in artistsJSON: artists.append(artist['name'])
            time = item['duration_ms']
            songID = item['id']
            songName = item['name']
            popularity = item['popularity']
            spotifySong = Song(title=songName, time=time/1000, artist=artists, album=albumName, genre='', songID=songID)
            score = getMatchScore(iTunesSong, spotifySong)
            spotifySong.matchScore = score
            #getMatchScore() returns 2 if it is certain that the song is a match
            if spotifySong.matchScore == 2:
                return spotifySong
            spotifySearchResults.append(spotifySong)
        
        maxScore=0
        maxIndex=0
        for i in range(0, len(spotifySearchResults)):
            #find song with highest matchScore
            if spotifySearchResults[i].matchScore > maxScore:
                maxIndex = i
                maxScore = spotifySearchResults[i].matchScore

        #Is score high enough? either return that song or empty Song() if not high enough match ---- MIN_MATCH_SCORE
        if maxScore >= MIN_MATCH_SCORE:
            return spotifySearchResults[maxIndex]
        else:
            emptySong = Song()
            emptySong.returnedResults=1
            return Song()
    else:
        return Song()
    

def standardizeString(string):
    string = string.replace("(", '').replace(")", '').replace("-", '').replace("[", '').replace("]", '').replace("feat. ", '').strip()
    return string


def getMatchScore(iTunesSong, spotifySong):
    matchScore = 0
    titleMatch=0
    artistMatch=0
    timeMatch=0
    albumMatch=0

    # Does title match? Similar Title?
    if iTunesSong.title.lower() == spotifySong.title.lower():
        titleMatch = 1
    elif standardizeString(iTunesSong.title.lower()).replace(' ', '') == standardizeString(spotifySong.title.lower()).replace(' ', ''):
        titleMatch = 1

    # Does Artist match?
    check = []
    newSpotifyArtists = []

    for j in range(0, len(spotifySong.artist)):
        newSpotifyArtists.extend(re.split(", | & " , spotifySong.artist[j]))

    for i in range(0, len(iTunesSong.artist)):
        for j in range(0, len(newSpotifyArtists)):
            if iTunesSong.artist[i].lower() == newSpotifyArtists[j].lower():
                check.append(1)
                break
    if len(check) == len(iTunesSong.artist) or len(check) == len(newSpotifyArtists):
        artistMatch = 1

    # Is song length similar to iTunesSong?
    if float(iTunesSong.time)+5 >= float(spotifySong.time) and float(iTunesSong.time)-5 <= float(spotifySong.time):
        timeMatch = 1

    if titleMatch == 1 and artistMatch == 1 and timeMatch == 1:
        matchScore = 2
        return matchScore

    # Album name match?
    if iTunesSong.album.lower() == spotifySong.album.lower():
        albumMatch = 1
    elif standardizeString(iTunesSong.album.lower()).replace(' ', '') == standardizeString(spotifySong.album.lower()).replace(' ', ''):
        albumMatch = 1

    matchScore = (titleMatch + artistMatch + timeMatch + albumMatch) / 4
    return matchScore


def addPlaylist(songTitle, songArtist, playlistName):
    for i in range(0, len(allSongsiTunes)):
        song = allSongsiTunes[i]
        if (song.title == songTitle): 
            song.playlists.append(playlistName)
            break

def main(usr, cid, csec, efile):
    USERNAME = usr
    CLIENT_ID = cid
    CLIENT_SECRET = csec
    EXCEL_FILE = efile

    # Read excel file into songSheet
    excelFile = xlrd.open_workbook(EXCEL_FILE) 
    songSheet = excelFile.sheet_by_index(0) 

    print("Reading in iTunes Songs...")
    # Read songs into allSongs list
    for i in range(0, songSheet.nrows):
        artistList = re.split(", | & " , str(songSheet.cell_value(i, 3)))
        allSongsiTunes.append(Song(str(songSheet.cell_value(i, 0)).strip(), int(songSheet.cell_value(i, 2))*1440, artistList, str(songSheet.cell_value(i, 4)).strip(), str(songSheet.cell_value(i, 5)).strip()))


    # Export all playlists to excel sheets >> Click playlist. File > Library > Export playlist > save as .txt in directory labeled 'playlists'

    playlistFiles = os.listdir('playlists/')

    print("Reading in iTunes Playlists...")
    # Loop through .txt files (playlists) and append the playlist title to the Song.playlist list
    for playlist in playlistFiles:
        if(".txt" in playlist):
            with open('playlists/' + playlist, 'r', encoding="utf8", errors='ignore') as f:
                songList = f.readlines()
                for i in range(1, len(songList)-1):
                    line = songList[i]
                    songInfo = line.split("\t")
                    newTitle=""
                    for j in range (len(songInfo[0])):
                        if j%2 == 1:
                            newTitle = newTitle + songInfo[0][j]
                    addPlaylist(newTitle, songInfo[1], playlist)


    # Connect to Spotify API with credentials declared earlier
    token = util.prompt_for_user_token(USERNAME, SCOPE,  client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

    if token:
        sp = spotipy.Spotify(auth=token)
        setOff=0
        hasNext = True

        # Get list of all songs currently in Spotify Library
        while (hasNext):
            trackList = sp.current_user_saved_tracks(limit=20, offset=setOff)
            hasNext = not (trackList['next'] == None)
            setOff = trackList['offset'] + 1

            if(len(trackList['items']) > 0):
                for track in trackList['items']['track']:
                    spotifyDic[track['name']]=track['id']


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
                            playlistDic[playlist['name']][1].append(track['track']['id'])

        print("Searching for songs on Spotify...")
        with open('songNotFound.txt', 'a+') as notFoundFile:
            with open('songFound.txt', 'a+') as foundFiles:
                for iTunesSong in allSongsiTunes:
                    result = getSongID(iTunesSong, sp)

                    if not (result.songID == ''):
                        allSongsSpotify.append(result)
                        foundFiles.write("%s \t %s \t %s \t %s \t %s \t %s \t %s \n"%(result.title, result.time, result.artist, result.album, result.genre, result.songID, iTunesSong.playlists))
                        #print ("Successfully found %s (%s) on Spotify" % (result.title, result.songID))
                    else:
                        if (result.returnedResults == 0):
                            newSong = Song(title=standardizeString(iTunesSong.title), time=iTunesSong.time, artist=iTunesSong.artist, album=iTunesSong.album, genre=iTunesSong.genre)
                            result = getSongID(newSong, sp)
                            if not (result.songID == ''):
                                allSongsSpotify.append(result)
                                foundFiles.write("%s \t %s \t %s \t %s \t %s \t %s \t %s \n"%(result.title, result.time, result.artist, result.album, result.genre, result.songID, iTunesSong.playlists))
                                #print ("Successfully found %s (%s) on Spotify" % (result.title, result.songID))
                            else:
                                if (result.returnedResults == 0):
                                    ind = iTunesSong.title.find("(")
                                    if(ind>=0):
                                        newSong = Song(title=iTunesSong.title[0:iTunesSong.title.find("(")].strip(), time=iTunesSong.time, artist=iTunesSong.artist, album=iTunesSong.album, genre=iTunesSong.genre)                               
                                    #print ("Trying newTitle: %s" % (iTunesSong.title[0:iTunesSong.title.find("(")].strip()))
                                    result = getSongID(newSong, sp)
                                    if not (result.songID == ''):
                                        allSongsSpotify.append(result)
                                        foundFiles.write("%s \t %s \t %s \t %s \t %s \t %s \t %s \n"%(result.title, result.time, result.artist, result.album, result.genre, result.songID, iTunesSong.playlists))
                                        #print ("Successfully found %s (%s) on Spotify" % (result.title, result.songID))
                                    else:
                                        # Write info of iTunesSong to songNotFound.txt file
                                        notFoundFile.write("%s \t %s \n"%(iTunesSong.title, iTunesSong.artist,))
                                        #print ("\n")
                                        #print ("Search for '%s' failed." % (iTunesSong.title))
                                        #print ("\n")
                                else:
                                    notFoundFile.write("%s \t %s \n"%(iTunesSong.title, iTunesSong.artist,))
                                    #print ("\n")
                                    #print ("Search for '%s' failed." % (iTunesSong.title))
                                    #print ("\n")
                        else:
                            notFoundFile.write("%s \t %s \t %s \t %s \t %s \n"%(iTunesSong.title, iTunesSong.time, iTunesSong.artist, iTunesSong.album, iTunesSong.genre))
                            #print ("\n")
                            #print ("Search for '%s' failed." % (iTunesSong.title))
                            #print ("\n")            
            notFoundFile.close()
            foundFiles.close()


        
        # Loop through Songs in allSongs and add them to appropriate playlists using Song.playlists
        for song in allSongsSpotify:
            if not (sp.current_user_saved_tracks_contains(tracks=[song.songID])):
                sp.current_user_saved_tracks_add(tracks=[song.songID])
            for playlist in song.playlists:
                playlistName = playlist.replace('.txt', '')
                # Does playlist already exist?
                if playlistName in playlistDic.keys():
                    #print('Playlist %s exists'%(playlistName))
                    # Check if the Song is already in the playlist
                    if song.songID in playlistDic[playlistName][1]:
                        pass
                    else:
                        # add song to playlist
                        #print('Adding song %s to playlist %s'%(song.songID, playlistName))
                        sp.user_playlist_add_tracks(user=USERNAME, playlist_id=playlistDic[playlistName][0], tracks= [song.songID], position=None)
                        playlistDic[playlistName][1].append(song.songID)
                else:
                    # Create new Playlist and song
                    #print('Creating new playlist %s and adding song'%(playlistName, song.songID))
                    newPlaylist = sp.user_playlist_create(user=USERNAME, name=playlistName, public=True)
                    sp.user_playlist_add_tracks(user=USERNAME, playlist_id=newPlaylist['id'], tracks= [song.songID], position=None)
                    playlistDic[playlistName] = (newPlaylist['id'], [])
                    playlistDic[playlistName][1].append(song.songID)

    else:
        print("Can't get token for ", USERNAME)
