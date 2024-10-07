import numpy as np
import os

segy_binary_header_dtype = np.dtype([
    ('jobid', 'i4'),
    ('lino', 'i4'),
    ('reno', 'i4'),
    ('ntrpr', 'i2'),  # mandatory (prestack)
    ('nart', 'i2'),  # mandatory (prestack)
    ('hdt', 'u2'),  # mandatory (all)
    ('dto', 'u2'),
    ('hns', 'u2'),  # mandatory (all)
    ('nso', 'u2'),
    ('format', 'i2'),  # mandatory (all)
    ('fold', 'i2'),  # strongly recommended
    ('tsort', 'i2'),  # strongly recommended
    ('vscode', 'i2'),
    ('hsfs', 'i2'),
    ('hsfe', 'i2'),
    ('hslen', 'i2'),
    ('hstyp', 'i2'),
    ('schn', 'i2'),
    ('hstas', 'i2'),
    ('hstae', 'i2'),
    ('htatyp', 'i2'),
    ('hcorr', 'i2'),
    ('bgrcv', 'i2'),
    ('rcvm', 'i2'),
    ('mfeet', 'i2'),  # strongly recommended
    ('polyv', 'i2'),
    ('vpol', 'i2'),
    ('unassigned_1', 'i4'),
    ('unassigned_2', 'i4'),
    ('unassigned_3', 'i4'),
    ('unassigned_4', 'i4'),
    ('unassigned_5', 'i4'),
    ('unassigned_6', 'i4'),
    ('unassigned_7', 'i4'),
    ('unassigned_8', 'i4'),
    ('unassigned_9', 'i4'),
    ('unassigned_10', 'i4'),
    ('unassigned_11', 'i4'),
    ('unassigned_12', 'i4'),
    ('unassigned_13', 'i4'),
    ('unassigned_14', 'i4'),
    ('unassigned_15', 'i4'),
    ('unassigned_16', 'i4'),
    ('unassigned_17', 'i4'),
    ('unassigned_18', 'i4'),
    ('unassigned_19', 'i4'),
    ('unassigned_20', 'i4'),
    ('unassigned_21', 'i4'),
    ('unassigned_22', 'i4'),
    ('unassigned_23', 'i4'),
    ('unassigned_24', 'i4'),
    ('unassigned_25', 'i4'),
    ('unassigned_26', 'i4'),
    ('unassigned_27', 'i4'),
    ('unassigned_28', 'i4'),
    ('unassigned_29', 'i4'),
    ('unassigned_30', 'i4'),
    ('unassigned_31', 'i4'),
    ('unassigned_32', 'i4'),
    ('unassigned_33', 'i4'),
    ('unassigned_34', 'i4'),
    ('unassigned_35', 'i4'),
    ('unassigned_36', 'i4'),
    ('unassigned_37', 'i4'),
    ('unassigned_38', 'i4'),
    ('unassigned_39', 'i4'),
    ('unassigned_40', 'i4'),
    ('unassigned_41', 'i4'),
    ('unassigned_42', 'i4'),
    ('unassigned_43', 'i4'),
    ('unassigned_44', 'i4'),
    ('unassigned_45', 'i4'),
    ('unassigned_46', 'i4'),
    ('unassigned_47', 'i4'),
    ('unassigned_48', 'i4'),
    ('unassigned_49', 'i4'),
    ('unassigned_50', 'i4'),
    ('unassigned_51', 'i4'),
    ('unassigned_52', 'i4'),
    ('unassigned_53', 'i4'),
    ('unassigned_54', 'i4'),
    ('unassigned_55', 'i4'),
    ('unassigned_56', 'i4'),
    ('unassigned_57', 'i4'),
    ('unassigned_58', 'i4'),
    ('unassigned_59', 'i4'),
    ('unassigned_60', 'i4'),
    ('segyrev', 'i2'),
    ('fixedlen', 'i2'),
    ('numhdr', 'i2'),
    ('unassigned_61', 'i4'),
    ('unassigned_62', 'i4'),
    ('unassigned_63', 'i4'),
    ('unassigned_64', 'i4'),
    ('unassigned_65', 'i4'),
    ('unassigned_66', 'i4'),
    ('unassigned_67', 'i4'),
    ('unassigned_68', 'i4'),
    ('unassigned_69', 'i4'),
    ('unassigned_70', 'i4'),
    ('unassigned_71', 'i4'),
    ('unassigned_72', 'i4'),
    ('unassigned_73', 'i4'),
    ('unassigned_74', 'i4'),
    ('unassigned_75', 'i4'),
    ('unassigned_76', 'i4'),
    ('unassigned_77', 'i4'),
    ('unassigned_78', 'i4'),
    ('unassigned_79', 'i4'),
    ('unassigned_80', 'i4'),
    ('unassigned_81', 'i4'),
    ('unassigned_82', 'i4'),
    ('unassigned_83', 'i4'),
    ('unassigned_84', 'i2'),
])

##guess EBCDIC encoding
ASCII = 'ascii'
EBCDIC = 'cp500'
SUPPORTED_ENCODINGS = (ASCII, EBCDIC)

def is_supported_encoding(encoding):
    return encoding in SUPPORTED_ENCODINGS
COMMON_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:_- '
COMMON_EBCDIC_CHARS = set(COMMON_CHARS.encode(EBCDIC))
COMMON_ASCII_CHARS = set(COMMON_CHARS.encode(ASCII))

def guess_encoding(bs, threshold=0.5):
    ebcdic_count = 0
    ascii_count = 0
    null_count = 0
    count = 0
    for b in bs:
        if b in COMMON_EBCDIC_CHARS:
            ebcdic_count +=1
        if b in COMMON_ASCII_CHARS:
            ascii_count +=1
        if b == 0:
            null_count += 1
        count += 1
    if count == 0:
        return None

    ebcdic_freq = ebcdic_count / count
    ascii_freq = ascii_count / count
    null_freq = null_count / count

    if null_freq == 1.0:
        return ASCII  # Doesn't matter

    if ebcdic_freq < threshold <= ascii_freq:
        return ASCII

    if ebcdic_freq >= threshold > ascii_freq:
        return EBCDIC

    return None


def read_ebcdic(_file):
    with open(_file, 'rb') as f:
        header = np.fromfile(f, dtype='u2', count=int(3200 / 2))
        if np.any(np.diff(header)):
            f.seek(0)
            baca = f.read(3200)
            tebak = guess_encoding(baca)

            if tebak == 'ascii':
                ebcdic = baca.decode('EBCDIC-CP-BE').encode('cp500')
            else:
                ebcdic = baca.decode('EBCDIC-CP-BE').encode('utf8')
            return ebcdic
        else:
            return None


def read_bheader(_file):
    with open(_file, 'rb') as fil:
        fil.seek(3200)
        binary = np.fromstring(fil.read(400), dtype=segy_binary_header_dtype)
        try:
            assert 0 < binary['format'] < 9
        except AssertionError:
            binary = binary.byteswap()
        return binary


def num_traces(_file, ns1):
    with open(_file, 'rb') as fil:
        fil.seek(0, os.SEEK_END)
        size = fil.tell()
        print(size)
        nt = (size - 3600.0) / (240.0 + ns1 * 4.0)
        assert nt % 1 == 0
    return nt