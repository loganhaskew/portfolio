import os
import numpy as np
import librosa
import librosa.display
import pandas as pd
import csv
from pydub import AudioSegment
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


def mp3_converter(file, mp3_path):
    '''convert input mp3 file to wav file'''
    wav_path = '/Users/loganhaskew/Documents/data/key_data/audio_wav/'

    input_file = mp3_path + file
    output_file = wav_path + file[:-4] + '.wav'

    audio = AudioSegment.from_mp3(input_file)
    audio.export(output_file, format='wav')
    return output_file

def get_harmonic_spec(audio_path):
    amp_data, sr = librosa.load(audio_path)
    td_data = librosa.effects.harmonic(amp_data, margin=3.0)
    H = librosa.stft(td_data, n_fft=16384)
    return td_data, H

def png_generator(audio_path, H):
    '''from input wav file, generate png of its spectrogram'''
    image_path = '/Users/loganhaskew/Documents/data/key_data/spectrograms/'
    
    fig, ax = plt.subplots()
    ref = np.max(np.abs(H))
    img = librosa.display.specshow(librosa.amplitude_to_db(np.abs(H), ref=ref), sr=22050,
                                   x_axis='time', y_axis='log', ax=ax, hop_length=4096)
    ax.set(ylim=[0, 8000])
    plt.axis('off')
    fig_path = image_path + audio_path[:-4] + '.png'
    plt.savefig(fig_path, dpi=100, bbox_inches='tight', transparent=True, pad_inches=0)
    return fig_path

def build_pitch_bins():
    '''build dataframe for pitch binning'''
    pitch_labels = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
    octave = list(range(9))
    min_freq = []
    max_freq = []
    center_freq = []

    # define ratio between semitones
    half_step = 10**(np.log10(2)/12)

    for i in range(len(pitch_labels)*len(octave)):
            if i == 0:
                note_center = 16.35
                note_min = 0
                note_max = (note_center*half_step + note_center)/2
                center_freq.append(note_center)
                min_freq.append(note_min)
                max_freq.append(note_max)
            else:
                note_min = note_max
                note_center = note_center*half_step
                note_max = (note_center*half_step + note_center)/2
                center_freq.append(note_center)
                min_freq.append(note_min)
                max_freq.append(note_max)

    df = pd.DataFrame({'pitch': pitch_labels*9, 'octave': octave*12, 'min_freq': min_freq,
                       'max_freq': max_freq, 'center_freq': center_freq})
    return df

def get_spec_series(data):
    '''get spectrum to be analyzed as a series with frequency as index'''
    n = len(data)
    harm = np.fft.fft(data, n)
    PSD_h = (harm*np.conj(harm))/n
    freq_h = 1/(1/22050*n) * np.arange(n)
    spec_clean = pd.Series(data=np.abs(PSD_h), index=freq_h)
    # significantly speed up code in build_song_df by filtering clearly negligible freqs
    spec_clean = spec_clean[(spec_clean>0.05) & (spec_clean.index>10)]
    return spec_clean

def build_song_df(df, spec_clean, file):
    '''build dataframe with frequencies binned on pitch and weight on power'''
    pitch_labels = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
    df_song = df
    df_song['power'] = 0

    for freq, power in spec_clean.items():
        for index, row in df_song.iterrows():
            if freq > row['min_freq'] and freq < row['max_freq']:
                df_song.at[index, 'power'] += power 

    df_song = df_song[df_song.power > 0]

    df_song.pitch = df_song.pitch.astype('category')
    df_song.pitch.cat.set_categories(pitch_labels, inplace=True)
    df_song.sort_values(['pitch'], inplace=True)
    df_song = df_song.groupby('pitch').sum()
    df_song.reset_index(inplace=True)
    df_song = df_song[['pitch', 'power']]

    row_list = list(df_song['power'])
    key_path = '/Users/loganhaskew/Documents/data/key_data/key/'
    with open(key_path + file[:-4] + '.key', 'r') as f:
        key = f.readline()
    row_list.append(key)
    row_list.append(file)

    with open('PSD_data.csv', 'a') as doc:
        writer = csv.writer(doc)
        writer.writerow(row_list)
    return

if __name__ == "__main__":
    mp3_path = '/Users/loganhaskew/Documents/data/key_data/audio/'
    already_conv_df = pd.read_csv('PSD_data.csv')
    files_exist = list(already_conv_df['file_name'])
    leftovers = []

    for clip in os.listdir(mp3_path):
        if clip not in files_exist:
            leftovers.append(clip)

    num_of_clips = len(leftovers)
    df = build_pitch_bins()

    for index, clip in enumerate(leftovers):
        print(f"Converting {index+1} of {num_of_clips}")
        wav = mp3_converter(clip, mp3_path)
        td_data, H = get_harmonic_spec(wav)
        fig_path = png_generator(clip, H)
        print(f"png {index+1} generated")
        spec_clean = get_spec_series(td_data)
        build_song_df(df, spec_clean, clip)
        del wav, td_data, fig_path, spec_clean
        print('new line written to csv')