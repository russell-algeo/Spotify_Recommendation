# Spotify_Recommendation

This repository contains a Spotify exploration and track recommendation tool to assist user in music discovery. It also contains files used for extraction of data from the Spotify API. In order to use, replace 

- `spotify_exploration_and_recommnedation.ipynb`: reads in `saved_tracks.csv` and `processed_streams.csv` as generated by `extract_saved_tracks_data.ipynb` and `extract_streaming_history_data.ipynb` to identify the user's most popular tracks, binge worthy tracks, and dependable tracks. Contains recommendation tool that allows the user to query for recommendations of single songs, recommendations of tracks that represent the "average" of two tracks, or recommendations of tracks that represent the "difference" of two tracks.
- `spotify_playlist_boost.ipynb`: reads in playlist data from `/output/playlists` and `saved_tracks.csv` as generated in `extract_saved_tracks_data.ipynb` to recommend songs from a users saved tracks that should be added to that users playlists.
- `extract_saved_tracks_data.ipynb`: extracts saved tracks data (track list, Spotify API audio features, calculated rich audio features) for a user by connecting to Spotify API. Exports data as `saved_tracks.csv` to `/output`.
- `extract_streaming_history_data.ipynb`: extracts streaming history (track list, Spotify API audio features, calculated rich audio features) from .json files provided by Spotify data dump. Exports data as `processed_streams.csv` to `/output`.
- `extract_playlist_data.ipynb`: extracts playlist data (track list, Spotify API audio features, calculated rich audio features) for a users playlist. Exports playlist data to `/output/playlists` as .csv files.
-`utils.py`: contains various utility functions used throughout other files.
- `config.py`: contains space to enter Spotify API credentials. Insert your local API credentials here for rest of repository to be able to access Spotify API for data collection.

Due to file upload size limits, I cannot directly upload the .csv files refrenced above. Here is a link to a google drive folder from where they can be downloaded:
https://drive.google.com/drive/folders/1QIBsoJ4wbtgYiuP2Yrzh1qSdOkCLcnNG?usp=sharing
