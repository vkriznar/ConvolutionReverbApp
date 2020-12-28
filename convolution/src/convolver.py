import numpy as np
from src.utility import pcm2float, float2pcm
from scipy.io import wavfile
from scipy.signal import fftconvolve
from pydub import AudioSegment


class MusicConvolver:
    def __init__(self):
        self.filename, self.ir_location = None, None
        self.input_rate, self.input_sig = None, None
        self.ir_rate, self.ir_sig = None, None

    def load_file(self, sound_file_name):
        self.filename = sound_file_name
        if sound_file_name.endswith(".mp3"):
            sound = AudioSegment.from_mp3("../media/music/" + sound_file_name)
            sound.export("../temp/temp.wav", format="wav")
            file_path = "../temp/temp.wav"
        else:
            file_path = "../media/music/" + sound_file_name
        self.input_rate, input_sig = wavfile.read(file_path)
        self.input_sig = pcm2float(input_sig, "float32")

    def load_ir(self, ir_location):
        self.ir_location = ir_location
        self.ir_rate, ir_sig = wavfile.read("../media/signals/{}.wav".format(ir_location))
        self.ir_sig = pcm2float(ir_sig, "float32")

    def convolve(self):
        if self.input_rate != self.ir_rate:
            raise Exception("Sample rates of input file nad IR file don't match!")
        else:
            rate = self.input_rate

        con_len = -1
        out_0 = fftconvolve(self.input_sig[:con_len, 0], self.ir_sig[:con_len, 0])
        out_0 = out_0/np.max(np.abs(out_0))
        out_1 = fftconvolve(self.input_sig[:con_len, 1], self.ir_sig[:con_len, 1])
        out_1 = out_1/np.max(np.abs(out_1))

        out = np.vstack((out_0, out_1)).T
        out_filename = "../{}-{}.wav".format(self.filename.split(".")[0], self.ir_location)
        wavfile.write(out_filename, rate, float2pcm(out, "int16"))

        return out_filename
