import sys
import spotipy
import spotipy.util as util
import xlrd
import os
import re
import allSongsSearch
import addSongsToPlaylists

# Enter credentials below, as described in the README.md file
USERNAME = ''
CLIENT_ID = ''
CLIENT_SECRET = ''
EXCEL_FILE = ''

def main():
    allSongsSearch.main(USERNAME, CLIENT_ID, CLIENT_SECRET, EXCEL_FILE)
    addSongsToPlaylists.main(USERNAME, CLIENT_ID, CLIENT_SECRET)

if __name__ == '__main__':
    main()