import wave
import random
import array
import struct
import math

NOTE_LEN_SEC = 5.0
SAMPLES_PER_SEC = 44100.0
NUM_CHANNELS = 1
SAMPLE_BYTE_WIDTH = 2

# functions that generate ready-to-store toness
def gen_tone(sample_indices, freq, amplitude):
  return [int(amplitude * math.sin((2 * math.pi)*i*(float(freq)/SAMPLES_PER_SEC))) for i in i_range]

def gen_ramped_tone(sample_indices, freq, amplitude):
  return [int(amplitude * (1.0 - float(i) / len(sample_indices)) * math.sin((2 * math.pi)*i*(float(freq)/SAMPLES_PER_SEC))) for i in i_range]

def gen_exp_tone(sample_indices, freq, amplitude):
  return [int(amplitude * ((1.0 - float(i) / len(sample_indices))**3) * math.sin((2 * math.pi)*i*(float(freq)/SAMPLES_PER_SEC))) for i in i_range]

# functions that generate arrays of floats, which must be truncated prior to storage
def gen_float_tone(sample_indices, freq, phase_rad=0):
  return [math.sin(phase_rad + (2 * math.pi)*i*(float(freq)/SAMPLES_PER_SEC)) for i in i_range]

# Memberwise multiply of two equal-size arrays
def mix_signals(a,b):
  return [a_s * b_s for a_s,b_s in zip(a, b)]

# Multiply an array by a scalar
def multiply_signal(scalar, signal):
  return [scalar * s for s in signal]

# Multiply and shift an array by scalars
def shift_multiply_signal(coeff, offset, signal):
  return [coeff * s + offset for s in signal]

note_output = wave.open('note.wav', 'w')

note_output.setparams((NUM_CHANNELS, SAMPLE_BYTE_WIDTH, int(SAMPLES_PER_SEC), 0, 'NONE', 'not compressed'))

# for i in range(0, SAMPLE_LEN):
        # # value = random.randint(-32767, 32767)
        # value = 1000 * math.sin((2 * math.pi)*i*(440.0/44100.0))
        # packed_value = struct.pack('h', value)
        # note_output.writeframes(packed_value)
        # note_output.writeframes(packed_value)

def db_to_ratio(db):
  return 10**(db / 10.0)

def ratio_to_db(ratio):
  return 10 * math.log10(ratio)

# Frequency profiles
i_range = range(0, int(SAMPLES_PER_SEC * NOTE_LEN_SEC))
harmonics = range(1,12)

violin_hs_db = [75,67,42,53,64,47,60,47,41,37,41,39] # from the Da Vinci stradivarius, according to http://www.nagyvaryviolins.com/
violin_hs_ratio = [db_to_ratio(h) for h in violin_hs_db]
violin_hs_ratio_normalized = multiply_signal(1.0 / max(violin_hs_ratio), violin_hs_ratio)

guitar_hs_ratio_normalized = [0.21, 1, 0.4, 0.19, 0.09, 0.08, 0.15, 0.08, 0.02, 0.09, 0.02, 0.08]# copied from http://img37.imageshack.us/img37/5249/e2fftanalysis.png

# Amplitude profile
swell_time = 2
burst_time = 0.5
fade_time = NOTE_LEN_SEC - swell_time
swell_samples = int(swell_time * SAMPLES_PER_SEC)
burst_samples = int(burst_time * SAMPLES_PER_SEC)
fade_samples = int(fade_time * SAMPLES_PER_SEC)
swell_ramp = [(x / float(swell_samples)     )**3 for x in range(0, swell_samples)] \
                  + [1 for x in range(0, burst_samples)] \
                  + [(1 - (x / float(fade_samples)))**3 for x in range(0, fade_samples)]


base_f = 196 # G3
tremolo_f = 8
a_violin = 3000.0
a_guitar = 3000.0

# Generate instruments
violin_tones = [gen_tone(i_range, base_f * h, a_violin * hs) for h,hs in zip(harmonics,violin_hs_ratio_normalized)]
guitar_tones = [gen_tone(i_range, base_f * h, a_guitar * hs) for h,hs in zip(harmonics,guitar_hs_ratio_normalized)]

violin_sound = [sum(column) for column in zip(*violin_tones)]
guitar_sound = [sum(column) for column in zip(*guitar_tones)]
note = mix_signals(swell_ramp, violin_sound)

# Save to file
packed_values = array.array('h', [int(s) for s in note])
note_output.writeframes(packed_values.tostring())


note_output.close()