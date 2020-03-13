### iTunesToSpotify.py README ### 

Transfer all playlists from your iTunes Library to your Spotify Library for free! This program & tutorial was written using the following applications and versions: 
- macOS Catalina version 10.15.1
- Python 3.7.4
- Microsoft Excel for Mac version 16.35
- Apple Music Desktop App version 1.0.1.37
- Spotify Desktop App version 1.1.28.721

Other dependencies and how to insatll from terminal:
- xlrd - run "pip3 install xlrd" from terminal
- Spotipy - run "pip3 install spotipy" from terminal


Since this program does not use the Apple Music API (in order to avoid the costs of an Apple Developer Program Membership), there are a few steps that need to be taken before it can be run:

1) SETTING UP EXCEL SPREADSHEET: Go to your Apple Music Desktop App and select all of the songs in your iTunes 'Songs' Library (highlight first song in library, scroll to last song and 'shift+click' to highlight all songs) Copy them using 'command+c'. Open up an empty Excel spreadsheet and click on the first cell, A1, then paste all of the songs with 'command+v. There should be 8 columns filled in with data, and n rows filled in where n is the number of total songs in your iTunes 'Songs' Library. Save this Excel sheet to the same directory that the iTunesToSpotify.py file is located.
*** NOTE *** Do not modify the Excel sheet at all. Even if a column is completely empty, leave it be!!


2) SETTING UP PLAYLISTS: Go back into your Apple Music Desktop App and click on the first playlist in the left-side panel that you would like to transfer to Spotify. While the playlist name is highlighted in the left-side pannel (i.e. you have clicked on the playlist and the songs in the playlist are showing in the main pannel), go to the top left corner of the screen and select File > Library > Export Playlist... then save the playlist as a .txt file in the 'playlists' directory (which is located in the same directory as the iTunesToSpotify.py file).
*** NOTE *** Make sure that the name of the file has no spaces in it, instead either delete the spaces, or replcae them with underscores.
Repeat this step for all playlists that you would like to transfer into Spotify.


3) AQCUIRE SPOTIFY DEVELOPER CREDENTIALS: Go to https://developer.spotify.com/dashboard/ and sign in using your Spotify log-in information (Or sign up to make a new account). Once you are successfully signed-in and on the 'dashboard' page, click 'Create an app or hardware integration'. Fill in the information needed with whatever you would like (use the information below as an example):

App or Hardware Name: 'iTunesTransfer'
App or Hardware Description: 'Transfer playlists from iTunes to Spotify'
What are you building?: Desktop App
*NEXT*
*Non-commercial*
*Check the 3 "I understand" boxes*
*Submit*

Once you hit submit, you will be taken to a page that shows an attribute called Client ID, and a button that says "Show Client Secret". These 2 values will be needed for step 4 so keep them handy. 

Now we must take a minute to set what is called the 'Redirect URI' for your program. This is used to authenticate your credentials when the program is run later. To do this, click on the "Edit Settings" button located in the upper right hand corner. Scroll down to the field labeled 'Redirect URIs' and enter "http://localhost/" (without the quotes), then scroll down and hit 'Save'. 

In addition to the client values you will need your Spotify username. This can be found by going into the Spotify Desktop App, clicking on the drop-down arrow in the top-right corner next to your profile name, and selecting 'Account'. A webpage will be opened with your 'Account Overview' which displays your username if you scroll down. 

4) ENTER SPOTIFY ACCOUNT INFORMATION: Open up the iTunesToSpotify.py file. Go to the lines where USERNAME, CLIENT_ID, CLIENT_SECRET, and EXCEL_FILE are initialized and enter your credentials that were found above in step 3. EXCEL_FILE should be set to name that you used to save the excel file in step 1. 
*** NOTE *** Make sure that all credentials are entered as strings. (I.e. the values should be entered between the '' that are already there)


Now you are ready to run the program! Launch a Terminal window and navigate to the 'iTunesToSpotifyPlaylists' directory (the same one in which iTunesToSpotify.py is located). Run the program with the command 'python3 iTunesToSpotify.py'. Upon running the program, it will open a page in your web browser, and Terminal will prompt you with the message "Enter the URL you were redirected to: ". Copy the URL from the web browser that was automatically opened, and paste it into Terminal and hit enter. 
*** NOTE *** Don't be discouraged if the page that is automatically opened in your web browser has an error message like "Site can't be reached" --- this is completely normal.

Once you enter the URL into Terminal, the program will begin to run! It may take a few minutes depending on how many / how large the playlists are that you are transferring. Upon completion (or even during runtime), you will see changes made to your Spotify Library and playlists. The program is not gauranteed to find all of the songs on Spotify, so after it is finished running you should take a look at the songNotFound.txt file to see which songs were not found or added to the appropriate playlists, and do it manually if possible. 


