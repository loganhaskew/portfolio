import numpy as np
import pandas as  pd
import os
import csv
import librosa

def fft_to_csv() -> None:
    '''writes line by line to csv of frequency data to fft_frame.csv'''
    wav_path = '/Users/loganhaskew/Documents/data/key_data/audio_wav/'
    for j, clip in enumerate(os.listdir(wav_path)):
        print(f"Converting {j+1} of {len(os.listdir(wav_path))}")
        data, sr = librosa.load(wav_path + clip)
        td_data = librosa.effects.harmonic(data, margin=2.0)
        n = len(td_data)
        fft = np.fft.fft(td_data, n)
        freqs = (1/(1/sr*n)) * np.arange(n)
        binned_fft = []
        for index, freq in enumerate(freqs):
            if index == 0:
                freq_round_prev = 10
                freq_sum = 0

            freq_round = round(freq)
            if freq_round > 8000:
                break
            elif freq_round < 10:
                continue
            else:
                if freq_round == freq_round_prev:
                    freq_sum += np.abs(fft[index])
                elif freq_round > freq_round_prev:
                    binned_fft.append(freq_sum)
                    freq_sum = np.abs(fft[index])
                    freq_round_prev = freq_round

        key_path = '/Users/loganhaskew/Documents/data/key_data/key/'
        with open(key_path + clip[:-4] + '.key', 'r') as f:
            key = f.readline()
            binned_fft.append(key)

        with open('fft_frame.csv', 'a') as doc:
            writer = csv.writer(doc)
            writer.writerow(binned_fft)
    return

if __name__ == "__main__":
    fft_to_csv()