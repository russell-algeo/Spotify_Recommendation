import numpy as np
import pandas as pd
import json
import csv
import datetime as dt
import os
import requests
import spotipy
import spotipy.util as util
from config import *
import io
from urllib.request import urlopen
import librosa
import pydub
import scipy


# Methods for collecting streaming history and relevant features to be compiled into usefull format. 


## Methods for working with json files: read and write

def read_json(input_file):
    try:
        with open(input_file) as f:
            data= json.load(f)
        return data
    except:
        return None

    
def write_json(data,output_file):
    jason = json.dumps(data,indent=4)
    path = output_file
    f = open(path,"w")
    f.write(jason)
    f.close()
    
## Methods for compiling streaming history and querying the Spotify API

def compile_streaming_history(path = 'MySpotifyData'):
    
    '''
    Extracts streaming history from MySpotifyData dump.
    Sptofiy gives this data as multiple json files.
    
    Return: list of dictionaries representing indivual streams containing 
            endTime: time track ended
            artistName: name of artist
            trackName: name of track
            msPlayed: number of milliseconds streamed
            
    '''
    
    files = ['MySpotifyData/' + x for x in os.listdir(path)
             if x.split('.')[0][:-1] == 'StreamingHistory']
    files.sort()
    
    streams = []
    
    for file in files: 
        processed_json = read_json(file)
        streams += [streaming for streaming in processed_json]
            
    return streams


def get_token(username = username, client_id = client_id, client_secret = client_secret,
              redirect_uri = redirect_uri, scope = scope):
    '''
    Collects Spotify API token.
    '''
  
    token = util.prompt_for_user_token(username=username,scope=scope,
                                               client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri)
    return token


def get_api_track_object(track_name, artist, token):
    
    '''
    Queries Spotify API to get the Spotify ID for a track.
    See https://curl.trillworks.com/ for converting between 
    curl requests and python script
    '''

    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token,
    }
    
    params = [
    ('q', track_name + ' artist: ' + artist),
    ('type', 'track')]
    
    try:
        response = requests.get('https://api.spotify.com/v1/search', 
                    headers = headers, params = params, timeout = 5).json()
        
        results = response['tracks']['items']
        # Check if any results were returned, if not try searching without specifying the artist
        if len(results) > 0:
            # Iterate until specific artist appears as first artist of track 
            for result in results:
                if artist.strip() == result['artists'][0]['name'].strip():
                    # Ensure correct track (avoids matching remixes, instrumentals, etc.)
                    if result['name'].strip() == track_name.strip():
                        return result
                    
            # If specific artist not found in results, use the first one
            first_result = response['tracks']['items'][0]
            return first_result
        
        # Search without specifying the artist
        else: 
            params = [
            ('q', track_name),
            ('type', 'track')]

            response = requests.get('https://api.spotify.com/v1/search', 
                        headers = headers, params = params, timeout = 5).json()

            results = response['tracks']['items']

            # Iterate until specific artist appears as first artist of track
            for result in results:
                if artist.strip() == result['artists'][0]['name'].strip():
                    # Ensure correct track (avoids matching remixes, instrumentals, etc.)
                    if result['name'].strip() == track_name.strip():
                        return result
                    
            # If specific artist not found in results, use the first one
            first_result = response['tracks']['items'][0]
            return first_result

    except:
        
        return None
    
def get_api_track_object_from_id(track_id, token):
    
    '''
    Collects the api track object of the track with the track_id given.
    '''
    
    sp = spotipy.Spotify(auth=token)
    try:
        track_object = sp.track(track_id)
        return track_object
    except:
        return None 
    
    
def get_api_audio_features(track_id, token):
    
    '''
    Collects the audio features of the track with the track_id given.
    '''
    
    sp = spotipy.Spotify(auth=token)
    try:
        audio_features = sp.audio_features(track_id)
        return audio_features[0]
    except:
        return None 
    
def get_api_artist_object(artist_id, token):
    '''
    Collects the artist object of the artist with the artist_id given.
    '''
    
    sp = spotipy.Spotify(auth=token)
    try:
        artist_object = sp.artist(artist_id)
        return artist_object
    except:
        return None 
    
def get_api_album_object(album_id, token):
    '''
    Collects the album object of the album with the album_id given.
    '''
    
    sp = spotipy.Spotify(auth=token)
    try:
        album_object = sp.album(album_id)
        return album_object
    except:
        return None 
    
def create_track_dictionary(api_track_object, token):
    '''
    Creates track dictionary containing track name, artist name, album name, track id, artist id, album id,
    artist genres, artist followers, artist popularity, album popularity, track audio features, and track popularity.
    '''
    track_id = api_track_object['id']
    track_name = api_track_object['name']
    track_popularity = api_track_object['popularity']
    preview_url = api_track_object['preview_url']
    if preview_url == None:
        token = get_token()
        sp = spotipy.Spotify(auth = token)
        preview_url = sp.track(track_id, market = 'US')['preview_url']
                
    album = api_track_object['album']
    album_id = album['id']
    album_name = album['name']
                
    artist = api_track_object['artists'][0]
    artist_id = artist['id']
    artist_name = artist['name']
    
    api_artist_object = get_api_artist_object(artist_id, token)
    artist_followers = api_artist_object['followers']['total']
    artist_genres = api_artist_object['genres']
    artist_popularity = api_artist_object['popularity']
    
    api_album_object = get_api_album_object(album_id, token)
    album_popularity = api_album_object['popularity']
    
    
    api_audio_features = get_api_audio_features(track_id, token)
    audio_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                      'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                      'duration_ms', 'time_signature']
    
    track_dictionary = {'track_key' : track_name + '___' + artist_name, 'track_name': track_name, 'artist_name': artist_name, 'album_name': album_name,
                        'track_id': track_id, 'artist_id': artist_id, 'album_id': album_id,
                        'artist_genres': artist_genres, 'artist_followers': artist_followers, 
                        'artist_popularity': artist_popularity, 'album_popularity': album_popularity,
                        'preview_url':preview_url}
    
    for audio_feature in audio_features:
        track_dictionary[audio_feature] = api_audio_features[audio_feature]
        
    track_dictionary['track_popularity'] = track_popularity
    
    return track_dictionary            
    
## Methods for adding queried information from Spotify API to streaming history 

def add_track_key_to_streams(streams):
    
    for stream in streams: 
        track_key = stream['trackName'] + '___' + stream['artistName']
        stream['track_key'] = track_key
    return streams

def extract_features(mp3):
    '''Extracts librosa audio features from 0:45 to 1:15 of an mp3 file'''
    y, sr = librosa.load(mp3)
    # Convert Audio to Mono
    y = librosa.to_mono(y)
    
    # Normalize the raw audio
    y = librosa.util.normalize(y)
    
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    tempo, beat_frames = librosa.beat.beat_track(y_percussive, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)
    mfccs = librosa.feature.mfcc(y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y, sr=sr)
    chroma = librosa.feature.chroma_cqt(y_harmonic, sr=sr)
    tonnetz = librosa.feature.tonnetz(y, sr=sr)
    spectral_flatness = librosa.feature.spectral_flatness(y)
    rms = librosa.feature.rms(y)
    spectral_centroid = librosa.feature.spectral_centroid(y)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y)
    energy = calc_energy(y)

    features = {'tempo_calc':tempo,'zcr':zcr,'mfccs':mfccs,'spectral_contrast':spectral_contrast,'chroma':chroma,
                'tonnetz':tonnetz,'spectral_flatness':spectral_flatness,'rms':rms,'spectral_centroid':spectral_centroid,
                'spectral_bandwidth':spectral_bandwidth, 'energy':energy}
    return features


def calc_energy(x, hop_length=512, frame_length=2048):
    hop_length = hop_length
    frame_length = frame_length
    
    # Calculation for energy
    energy = np.array([
        sum(abs(x[i:i+frame_length]**2))
        for i in range(0, len(x), hop_length)
        ])
    return energy

def collect_rich_features(url):
    
    if url != None: 
        wav = io.BytesIO()

        with urlopen(url) as r:
            r.seek = lambda *args: None  # allow pydub to call seek(0)
            pydub.AudioSegment.from_file(r).export(wav, "wav")

        wav.seek(0)
        feat = extract_features(wav)
        
        

        feat['energy_mean'] = np.mean(feat['energy'])
        feat['energy_var'] = np.var(feat['energy'])
        feat['energy_std'] = np.std(feat['energy'])
        feat['energy_min'] = np.min(feat['energy'])
        feat['energy_max'] = np.max(feat['energy'])
        feat['energy_median'] = np.median(feat['energy'])
        feat['energy_kurt'] = scipy.stats.kurtosis(feat['energy'])
        feat['energy_skew'] = scipy.stats.skew(feat['energy'])
        
        feat['rms_mean'] = np.mean(feat['rms'])
        feat['rms_var'] = np.var(feat['rms'])
        feat['rms_std'] = np.std(feat['rms'])
        feat['rms_min'] = np.min(feat['rms'])
        feat['rms_max'] = np.max(feat['rms'])
        feat['rms_median'] = np.median(feat['rms'])
        feat['rms_kurt'] = scipy.stats.kurtosis(feat['rms'][0])
        feat['rms_skew'] = scipy.stats.skew(feat['rms'][0])
        
        feat['zcr_mean'] = np.mean(feat['zcr'])
        feat['zcr_var'] = np.var(feat['zcr'])
        feat['zcr_std'] = np.std(feat['zcr'])
        feat['zcr_min'] = np.min(feat['zcr'])
        feat['zcr_max'] = np.max(feat['zcr'])
        feat['zcr_median'] = np.median(feat['zcr'])
        feat['zcr_kurt'] = scipy.stats.kurtosis(feat['zcr'][0])
        feat['zcr_skew'] = scipy.stats.skew(feat['zcr'][0])
        
        feat['spec_flat_mean'] = np.mean(feat['spectral_flatness'])
        feat['spec_flat_var'] = np.var(feat['spectral_flatness'])
        feat['spec_flat_std'] = np.std(feat['spectral_flatness'])
        feat['spec_flat_min'] = np.min(feat['spectral_flatness'])
        feat['spec_flat_max'] = np.max(feat['spectral_flatness'])
        feat['spec_flat_median'] = np.median(feat['spectral_flatness'])
        feat['spec_flat_kurt'] = scipy.stats.kurtosis(feat['spectral_flatness'][0])
        feat['spec_flat_skew'] = scipy.stats.skew(feat['spectral_flatness'][0])
        
        feat['spec_cent_mean'] = np.mean(feat['spectral_centroid'])
        feat['spec_cent_var'] = np.var(feat['spectral_centroid'])
        feat['spec_cent_std'] = np.std(feat['spectral_centroid'])
        feat['spec_cent_min'] = np.min(feat['spectral_centroid'])
        feat['spec_cent_max'] = np.max(feat['spectral_centroid'])
        feat['spec_cent_median'] = np.median(feat['spectral_centroid'])
        feat['spec_cent_kurt'] = scipy.stats.kurtosis(feat['spectral_centroid'][0])
        feat['spec_cent_skew'] = scipy.stats.skew(feat['spectral_centroid'][0])
        
        feat['spec_band_mean'] = np.mean(feat['spectral_bandwidth'])
        feat['spec_band_var'] = np.var(feat['spectral_bandwidth'])
        feat['spec_band_std'] = np.std(feat['spectral_bandwidth'])
        feat['spec_band_min'] = np.min(feat['spectral_bandwidth'])
        feat['spec_band_max'] = np.max(feat['spectral_bandwidth'])
        feat['spec_band_median'] = np.median(feat['spectral_bandwidth'])
        feat['spec_band_kurt'] = scipy.stats.kurtosis(feat['spectral_bandwidth'][0])
        feat['spec_band_skew'] = scipy.stats.skew(feat['spectral_bandwidth'][0])
        
        
        
        for j, e in enumerate(feat['mfccs']):
            feat[f'mfcc{j+1}_mean'] = np.mean(e)
            feat[f'mfcc{j+1}_var'] = np.var(e)
            feat[f'mfcc{j+1}_std'] = np.std(e)
            feat[f'mfcc{j+1}_med'] = np.median(e)
            feat[f'mfcc{j+1}_min'] = np.min(e)
            feat[f'mfcc{j+1}_max'] = np.max(e)
            feat[f'mfcc{j+1}_kurt'] = scipy.stats.kurtosis(e)
            feat[f'mfcc{j+1}_skew'] = scipy.stats.skew(e)
        for j, e in enumerate(feat['spectral_contrast']):
            feat[f'spec_cont{j+1}_mean'] = np.mean(e)
            feat[f'spec_cont{j+1}_var'] = np.var(e)
            feat[f'spec_cont{j+1}_std'] = np.std(e)
            feat[f'spec_cont{j+1}_med'] = np.median(e)
            feat[f'spec_cont{j+1}_min'] = np.min(e)
            feat[f'spec_cont{j+1}_max'] = np.max(e)
            feat[f'spec_cont{j+1}_kurt'] = scipy.stats.kurtosis(e)
            feat[f'spec_cont{j+1}_skew'] = scipy.stats.skew(e)
        for j, e in enumerate(feat['chroma']):
            feat[f'chroma{j+1}_mean'] = np.mean(e)
            feat[f'chroma{j+1}_var'] = np.var(e)
            feat[f'chroma{j+1}_std'] = np.std(e)
            feat[f'chroma{j+1}_med'] = np.median(e)
            feat[f'chroma{j+1}_min'] = np.min(e)
            feat[f'chroma{j+1}_max'] = np.max(e)
            feat[f'chroma{j+1}_kurt'] = scipy.stats.kurtosis(e)
            feat[f'chroma{j+1}_skew'] = scipy.stats.skew(e)
        for j, e in enumerate(feat['tonnetz']):
            feat[f'tonnetz{j+1}_mean'] = np.mean(e)
            feat[f'tonnetz{j+1}_var'] = np.var(e)
            feat[f'tonnetz{j+1}_std'] = np.std(e)
            feat[f'tonnetz{j+1}_med'] = np.median(e)
            feat[f'tonnetz{j+1}_min'] = np.min(e)
            feat[f'tonnetz{j+1}_max'] = np.max(e)
            feat[f'tonnetz{j+1}_kurt'] = scipy.stats.kurtosis(e)
            feat[f'tonnetz{j+1}_skew'] = scipy.stats.skew(e)
        
        feat.pop('mfccs')
        feat.pop('zcr')
        feat.pop('spectral_contrast')
        feat.pop('chroma')
        feat.pop('tonnetz')
        feat.pop('spectral_flatness')
        feat.pop('rms')
        feat.pop('spectral_centroid')
        feat.pop('spectral_bandwidth')
        feat.pop('energy')
        
        
    else: 
        feat = {}
        feat['tempo_calc'] = None
    
        feat['energy_mean'] = None
        feat['energy_var'] = None
        feat['energy_std'] = None
        feat['energy_min'] = None
        feat['energy_max'] = None
        feat['energy_median'] = None
        feat['energy_kurt'] = None
        feat['energy_skew'] = None
        
        feat['rms_mean'] = None
        feat['rms_var'] = None
        feat['rms_std'] = None
        feat['rms_min'] = None
        feat['rms_max'] = None
        feat['rms_median'] = None
        feat['rms_kurt'] = None
        feat['rms_skew'] = None
        
        feat['zcr_mean'] = None
        feat['zcr_var'] = None
        feat['zcr_std'] = None
        feat['zcr_min'] = None
        feat['zcr_max'] = None
        feat['zcr_median'] = None
        feat['zcr_kurt'] = None
        feat['zcr_skew'] = None
        
        feat['spec_flat_mean'] = None
        feat['spec_flat_var'] = None
        feat['spec_flat_std'] = None
        feat['spec_flat_min'] = None
        feat['spec_flat_max'] = None
        feat['spec_flat_median'] = None
        feat['spec_flat_kurt'] = None
        feat['spec_flat_skew'] = None
        
        feat['spec_cent_mean'] = None
        feat['spec_cent_var'] = None
        feat['spec_cent_std'] = None
        feat['spec_cent_min'] = None
        feat['spec_cent_max'] = None
        feat['spec_cent_median'] = None
        feat['spec_cent_kurt'] = None
        feat['spec_cent_skew'] = None
        
        feat['spec_band_mean'] = None
        feat['spec_band_var'] = None
        feat['spec_band_std'] = None
        feat['spec_band_min'] = None
        feat['spec_band_max'] = None
        feat['spec_band_median'] = None
        feat['spec_band_kurt'] = None
        feat['spec_band_skew'] = None
        
        
        
        for j in np.arange(20):
            feat[f'mfcc{j+1}_mean'] = None
            feat[f'mfcc{j+1}_var'] = None
            feat[f'mfcc{j+1}_std'] = None
            feat[f'mfcc{j+1}_med'] = None
            feat[f'mfcc{j+1}_min'] = None
            feat[f'mfcc{j+1}_max'] = None
            feat[f'mfcc{j+1}_kurt'] = None
            feat[f'mfcc{j+1}_skew'] = None
        for j in np.arange(7):
            feat[f'spec_cont{j+1}_mean'] = None
            feat[f'spec_cont{j+1}_var'] = None
            feat[f'spec_cont{j+1}_std'] = None
            feat[f'spec_cont{j+1}_med'] = None
            feat[f'spec_cont{j+1}_min'] = None
            feat[f'spec_cont{j+1}_max'] = None
            feat[f'spec_cont{j+1}_kurt'] = None
            feat[f'spec_cont{j+1}_skew'] = None
        for j in np.arange(12):
            feat[f'chroma{j+1}_mean'] = None
            feat[f'chroma{j+1}_var'] = None
            feat[f'chroma{j+1}_std'] = None
            feat[f'chroma{j+1}_med'] = None
            feat[f'chroma{j+1}_min'] = None
            feat[f'chroma{j+1}_max'] = None
            feat[f'chroma{j+1}_kurt'] = None
            feat[f'chroma{j+1}_skew'] = None
        for j in np.arange(6):
            feat[f'tonnetz{j+1}_mean'] = None
            feat[f'tonnetz{j+1}_var'] = None
            feat[f'tonnetz{j+1}_std'] = None
            feat[f'tonnetz{j+1}_med'] = None
            feat[f'tonnetz{j+1}_min'] = None
            feat[f'tonnetz{j+1}_max'] = None
            feat[f'tonnetz{j+1}_kurt'] = None
            feat[f'tonnetz{j+1}_skew'] = None
    
    
    return feat