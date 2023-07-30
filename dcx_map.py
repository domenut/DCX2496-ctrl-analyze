#!/usr/bin/env python3
import serial
import time
import binascii
from collections import namedtuple
from enum import Enum

'''Interface for DCX2496 via RS232. Chris McDonnell Sept.2020...
   I realise in hindsight that this interface is a stack of shit. I apologise to future me,
   or anyone else who attempts to use it. Nov.2020... It works nice though!
'''
comlink_write_enabled = True
# DEV0075M00C0 (my device_id_number)
DCX_HEAD = b'\xF0\x00\x20\x32\x00\x0E'
DCX_TAIL = b'\xf7'
DCX_DUMP_0 = b'\x50\x01\x00\x00'
DCX_DUMP_1 = b'\x50\x01\x00\x01'
DCX_RX_ENABLE = b'\x3f\x04\x00'
DCX_TX_ENABLE = b'\x3f\x08\x00'
DCX_RTX_ENABLE = b'\x3f\x0c\x00'
DCX_ADJUST = b'\x20\x01' # single parameter. The \x01 can be increased for multiples...
DCX_PING = b'\x44\x00\x00\x00'
#0xF0, 0x00, 0x20, 0x32, 0x20, 0x0E, 0x40, 0xf7

DUMP_0_FILE = 'dcx_dump_0'
DUMP_1_FILE = 'dcx_dump_1'
DUMP_FILE = 'dcx_dump'
PORT_NAME = 'ttyUSB0'


def chNameEnum(index=None):
    vals = (
    'Full-range', 'Subwoofer', 'Low', 'Low-mid', 'Mid', 'Hi-mid', 'Hi', 'Left Full-range', 'Left Subwoofer', 'Left Low', 'Left Low-mid', 'Left Mid', 'Left Hi-mid', 'Left Hi', 'Right Full-range', 'Right Subwoofer', 'Right Low', 'Right Low-mid', 'Right Mid', 'Right Hi-mid', 'Right Hi', 'Center Full-range', 'Center Subwoofer', 'Center Low', 'Center Low-mid', 'Center Mid', 'Center Hi-mid', 'Center Hi'
    )
    try:
        return vals[index]
    except:
        return vals
def freqEnum(index=None):
    vals = (
    20, 20.5, 21, 21.5, 22, 22.5, 23, 23.5, 24, 24.5, 25, 25.5, 26, 27, 27.5, 28, 28.5, 29, 30, 30.5, 31, 32, 32.5, 33, 34, 34.5, 35, 36, 37, 38, 38.5, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 61, 62, 63, 65, 66, 68, 69, 71, 72, 74, 75, 77, 79, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 107, 109, 111, 114, 116, 119, 121, 124, 127, 130, 132, 135, 138, 141, 145, 148, 151, 154, 158, 161, 165, 168, 172, 176, 180, 184, 188, 192, 196, 200, 205, 209, 214, 218, 223, 228, 233, 238, 243, 249, 254, 260, 266, 271, 277, 284, 290, 296, 303, 309, 316, 323, 330, 337, 345, 352, 360, 368, 376, 384, 393, 401, 410, 419, 428, 438, 447, 457, 467, 478, 488, 499, 510, 521, 532, 544, 556, 568, 581, 594, 607, 620, 634, 647, 662, 676, 691, 706, 722, 738, 754, 770, 787, 805, 822, 840, 859, 878, 897, 917, 937, 957, 979, 1000, 1020, 1040, 1070, 1090, 1110, 1140, 1160, 1190, 1210, 1240, 1270, 1290, 1320, 1350, 1380, 1410, 1440, 1470, 1500, 1530, 1570, 1600, 1640, 1670, 1710, 1740, 1780, 1820, 1860, 1900, 1940, 1980, 2030, 2070, 2110, 2160, 2210, 2250, 2300, 2350, 2400, 2460, 2510, 2560, 2620, 2680, 2730, 2790, 2850, 2920, 2980, 3040, 3110, 3180, 3240, 3310, 3390, 3460, 3530, 3610, 3690, 3770, 3850, 3930, 4020, 4110, 4190, 4280, 4380, 4470, 4570, 4670, 4770, 4870, 4980, 5080, 5190, 5310, 5420, 5540, 5660, 5780, 5910, 6030, 6160, 6300, 6430, 6570, 6720, 6860, 7010, 7160, 7320, 7470, 7640, 7800, 7970, 8140, 8320, 8500, 8680, 8870, 9060, 9260, 9460, 9660, 9870, 10100, 10300, 10500, 10800, 11000, 11200, 11500, 11700, 12000, 12200, 12500, 12800, 13000, 13300, 13600, 13900, 14200, 14500, 14800, 15100, 15500, 15800, 16100, 16500, 16900, 17200, 17600, 18000, 18400, 18800, 19200, 19600, 20000
    )
    try:
        return vals[index]
    except:
        return vals
def inABsourceEnum(index=None):
    vals = ('A&B=Analogue', 'A&B=Digital')
    try:
        return vals[index]
    except:
        return vals
def inCsourceEnum(index=None):
    vals = ('line', 'mic')
    try:
        return vals[index]
    except:
        return vals
def inStereoLinkEnum(index=None):
    vals = ('In link: Off', 'In link: A-B', 'In link: A-B-C', 'In link: A-B-C-SUM')
    try:
        return vals[index]
    except:
        return vals
def sumInSelectEnum(index=None):
    vals = ('Sum in: Off', 'Sum in: A', 'Sum in: B', 'Sum in: C', 'Sum in: A+B', 'Sum in: A+C', 'Sum in: B+C')
    try:
        return vals[index]
    except:
        return vals
def lengthUnitEnum(index=None):
    vals = ('mm', 'inch')
    try:
        return vals[index]
    except:
        return vals
def outConfigEnum(index=None):
    vals = ('Independant/mono*', '? LMHLMH ?', '? LLMMHH ?', '? LHLHLH ?')
    try:
        return vals[index]
    except:
        return vals
def eqQ_Enum(index=None):
    vals = (
    0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.33, 0.36, 0.4, 0.43, 0.46, 0.5, 0.6, 0.65, 0.7, 0.8, 0.9, 1.0, 1.1, 1.3, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 2.8, 3.2, 3.5, 4.0, 4.5, 5.0, 5.6, 6.3, 7.1, 7.9, 8.9, 10
    )
    try:
        return vals[index]
    except:
        return vals
def eqTypeEnum(index=None):
    vals = ('lp', 'bp', 'hp')
    try:
        return vals[index]
    except:
        return vals
def eqSlopeEnum(index=None):
    vals = ('6', '12')
    try:
        return vals[index]
    except:
        return vals
def sourcesEnum(index=None):
    vals = ('A', 'B', 'C', 'SUM')
    try:
        return vals[index]
    except:
        return vals
def limitReleaseTimeEnum(index=None):
    vals = (
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 89, 91, 93, 95, 97, 99, 101, 103, 105, 108, 110, 112, 115, 117, 119, 122, 124, 127, 130, 132, 135, 138, 141, 144, 147, 150, 153, 156, 160, 163, 167, 170, 174, 177, 181, 185, 189, 193, 197, 201, 205, 209, 214, 218, 223, 227, 232, 237, 242, 247, 252, 258, 263, 269, 274, 280, 286, 292, 298, 304, 311, 317, 324, 331, 337, 345, 352, 359, 367, 374, 382, 390, 399, 407, 415, 424, 433, 442, 451, 461, 471, 480, 491, 501, 511, 522, 533, 544, 556, 567, 579, 591, 604, 616, 629, 643, 656, 670, 684, 698, 713, 728, 743, 759, 775, 791, 808, 825, 842, 860, 878, 896, 915, 934, 954, 974, 994, 1015, 1036, 1058, 1080, 1103, 1126, 1150, 1174, 1199, 1224, 1249, 1276, 1303, 1330, 1358, 1386, 1415, 1445, 1475, 1506, 1538, 1570, 1603, 1637, 1671, 1706, 1742, 1779, 1816, 1854, 1893, 1933, 1974, 2015, 2057, 2101, 2145, 2190, 2236, 2283, 2330, 2379, 2429, 2480, 2532, 2586, 2640, 2695, 2752, 2810, 2869, 2929, 2990, 3053, 3117, 3183, 3250, 3318, 3387, 3459, 3531, 3605, 3681, 3758, 3837, 3918, 4000
    )
    try:
        return vals[index]
    except:
        return vals
def polarityEnum(index=None):
    vals = ('normal', 'inverted')
    try:
        return vals[index]
    except:
        return vals
def log_zero_to_4000_ms(index=None):
    vals = (
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 89, 91, 93, 95, 97, 99, 101, 103, 105, 108, 110, 112, 115, 117, 119, 122, 124, 127, 130, 132, 135, 138, 141, 144, 147, 150, 153, 156, 160, 163, 167, 170, 174, 177, 181, 185, 189, 193, 197, 201, 205, 209, 214, 218, 223, 227, 232, 237, 242, 247, 252, 258, 263, 269, 274, 280, 286, 292, 298, 304, 311, 317, 324, 331, 337, 345, 352, 359, 367, 374, 382, 390, 399, 407, 415, 424, 433, 442, 451, 461, 471, 480, 491, 501, 511, 522, 533, 544, 556, 567, 579, 591, 604, 616, 629, 643, 656, 670, 684, 698, 713, 728, 743, 759, 775, 791, 808, 825, 842, 860, 878, 896, 915, 934, 954, 974, 994, 1015, 1036, 1058, 1080, 1103, 1126, 1150, 1174, 1199, 1224, 1249, 1276, 1303, 1330, 1358, 1386, 1415, 1445, 1475, 1506, 1538, 1570, 1603, 1637, 1671, 1706, 1742, 1779, 1816, 1854, 1893, 1933, 1974, 2015, 2057, 2101, 2145, 2190, 2236, 2283, 2330, 2379, 2429, 2480, 2532, 2586, 2640, 2695, 2752, 2810, 2869, 2929, 2990, 3053, 3117, 3183, 3250, 3318, 3387, 3459, 3531, 3605, 3681, 3758, 3837, 3918, 4000
    )
    try:
        return vals[index]
    except:
        return vals
def xoCurveEnum(index=None):
    vals = ('off', 'but06', 'but12', 'bes12', 'lr12', 'but18', 'but24', 'bes24', 'lr24', 'but48', 'lr48')
    try:
        return vals[index]
    except:
        return vals
def eqCurveEnum(index=None):
    vals = ('BP', 'LP6', 'LP12', 'HP6', 'HP12')
    try:
        return vals[index]
    except:
        return vals
def xoLinkBool(index=None):
    vals = ('xoLink: Free*', '? xoLink: Lock ?')
    try:
        return vals[index]
    except:
        return vals
def outStereoLinkBool(index=None):
    vals = ('Out Stereo Link:off*', '? Out Stereo Link:on ?')
    try:
        return vals[index]
    except:
        return vals

airTempScale = lambda s=0: (s-20)
gainScale = lambda s=0: ((s-150)/10)
limitThresholdScale = lambda s=0: ((s-240)/10)
phaseScale = lambda s=0: (s*5)
delayShortScale = lambda s=0: (s*2)
Address = namedtuple('Address',('part', 'lo', 'med', 'hi', 'medbit'))
Dcx = namedtuple('Dcx', ['address','cmd',  'detents'])
class Mapper():
    '''Exposes both directions of each control of the dcx: Mapper.[object].[name/chan].[field]
        so eg:      "Mapper.Gain.ch01.cmd" returns 2 byte command to precede 2 byte value to send to DCX:
            Full packet = DCX_HEAD + DCX_ADJUST + [command]+[value] + DCX_TAIL ,
        Whereas eg: "Mapper.Gain.ch01.address" gives page number (part) and indexes (lo, med, hi, medbit ) of dcx memory dump(2 pages)
        for that control. See other methods in this file to generate these pages, ie: cache_dcx_to_files(), or values: _get_cached_value(_item)...
        Also provides pointer to data unit conversion function per control ie: Mapper.Eq1.Q01.detents(int(value)) returns log scaled(value).
  1,678,684,679,1
  '''
    
    class Setup(Dcx, Enum):
        inSumSelect = Dcx(Address(part=0, lo=117, med=0, hi=0, medbit=0), cmd=b'\x00\x02', detents=sumInSelectEnum)
        inSourceAB = Dcx(Address(part=0, lo=119, med=0, hi=0, medbit=0), cmd=b'\x00\x03', detents=inABsourceEnum)
        inSourceC = Dcx(Address(part=0, lo=121, med=0, hi=0, medbit=0), cmd=b'\x00\x04', detents=inCsourceEnum)
        outConfig = Dcx(Address(part=0, lo=123, med=0, hi=0, medbit=0), cmd=b'\x00\x05', detents=outConfigEnum)
        outStereoLink = Dcx(Address(part=0, lo=126, med=0, hi=0, medbit=0), cmd=b'\x00\x06', detents=outStereoLinkBool)
        inStereoLink = Dcx(Address(part=0, lo=128, med=0, hi=0, medbit=0), cmd=b'\x00\x07', detents=inStereoLinkEnum)
        delayLink = Dcx(Address(part=0, lo=130, med=0, hi=0, medbit=0), cmd=b'\x00\x08', detents=bool)
        xoLink = Dcx(Address(part=0, lo=133, med=0, hi=0, medbit=0), cmd=b'\x00\x09', detents=xoLinkBool)
        delayCorrect = Dcx(Address(part=0, lo=135, med=0, hi=0, medbit=0), cmd=b'\x00\x0a', detents=bool)
        airTemp = Dcx(Address(part=0, lo=137, med=0, hi=0, medbit=0), cmd=b'\x00\x0b', detents=airTempScale)
        delayUnit = Dcx(Address(part=0, lo=55, med=0, hi=0, medbit=0), cmd=b'\x00\x14', detents=lengthUnitEnum)
        muteOuts = Dcx(Address(part=0, lo=57, med=0, hi=0, medbit=0), cmd=b'\x00\x15', detents=bool)
        sumInGainA = Dcx(Address(part=0, lo=139, med=140, hi=141, medbit=6), cmd=b'\x00\x16', detents=gainScale)
        sumInGainB = Dcx(Address(part=0, lo=142, med=148, hi=143, medbit=1), cmd=b'\x00\x17', detents=gainScale)
        sumInGainC = Dcx(Address(part=0, lo=144, med=148, hi=145, medbit=3), cmd=b'\x00\x18', detents=gainScale)
    class Gain(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=713, med=716, hi=714, medbit=4), cmd=b'\x05\x02', detents=gainScale)
        ch2 = Dcx(Address(part=0, lo=882, med=884, hi=883, medbit=5), cmd=b'\x06\x02', detents=gainScale)
        ch3 = Dcx(Address(part=1, lo=51, med=52, hi=53, medbit=6), cmd=b'\x07\x02', detents=gainScale)
        ch4 = Dcx(Address(part=1, lo=221, med=228, hi=222, medbit=0), cmd=b'\x08\x02', detents=gainScale)
        ch5 = Dcx(Address(part=1, lo=390, med=396, hi=391, medbit=1), cmd=b'\x09\x02', detents=gainScale)
        ch6 = Dcx(Address(part=1, lo=559, med=564, hi=560, medbit=2), cmd=b'\x0a\x02', detents=gainScale)
        chA = Dcx(Address(part=0, lo=146, med=148, hi=147, medbit=5), cmd=b'\x01\x02', detents=gainScale)
        chB = Dcx(Address(part=0, lo=288, med=292, hi=289, medbit=3), cmd=b'\x02\x02', detents=gainScale)
        chC = Dcx(Address(part=0, lo=430, med=436, hi=431, medbit=1), cmd=b'\x03\x02', detents=gainScale)
        chS = Dcx(Address(part=0, lo=571, med=572, hi=573, medbit=6), cmd=b'\x04\x02', detents=gainScale)
    class Mute(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=715, med=0, hi=0, medbit=0), cmd=b'\x05\x03', detents=bool)
        ch2 = Dcx(Address(part=0, lo=885, med=0, hi=0, medbit=0), cmd=b'\x06\x03', detents=bool)
        ch3 = Dcx(Address(part=1, lo=54, med=0, hi=0, medbit=0), cmd=b'\x07\x03', detents=bool)
        ch4 = Dcx(Address(part=1, lo=223, med=0, hi=0, medbit=0), cmd=b'\x08\x03', detents=bool)
        ch5 = Dcx(Address(part=1, lo=392, med=0, hi=0, medbit=0), cmd=b'\x09\x03', detents=bool)
        ch6 = Dcx(Address(part=1, lo=561, med=0, hi=0, medbit=0), cmd=b'\x0a\x03', detents=bool)
        chA = Dcx(Address(part=0, lo=149, med=0, hi=0, medbit=0), cmd=b'\x01\x03', detents=bool)
        chB = Dcx(Address(part=0, lo=290, med=0, hi=0, medbit=0), cmd=b'\x02\x03', detents=bool)
        chC = Dcx(Address(part=0, lo=432, med=0, hi=0, medbit=0), cmd=b'\x03\x03', detents=bool)
        chS = Dcx(Address(part=0, lo=574, med=0, hi=0, medbit=0), cmd=b'\x04\x03', detents=bool)
    class DelaySw(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=718, med=0, hi=0, medbit=0), cmd=b'\x05\x04', detents=bool)
        ch2 = Dcx(Address(part=0, lo=887, med=0, hi=0, medbit=0), cmd=b'\x06\x04', detents=bool)
        ch3 = Dcx(Address(part=1, lo=56, med=0, hi=0, medbit=0), cmd=b'\x07\x04', detents=bool)
        ch4 = Dcx(Address(part=1, lo=225, med=0, hi=0, medbit=0), cmd=b'\x08\x04', detents=bool)
        ch5 = Dcx(Address(part=1, lo=394, med=0, hi=0, medbit=0), cmd=b'\x09\x04', detents=bool)
        ch6 = Dcx(Address(part=1, lo=563, med=0, hi=0, medbit=0), cmd=b'\x0a\x04', detents=bool)
        chA = Dcx(Address(part=0, lo=151, med=0, hi=0, medbit=0), cmd=b'\x01\x04', detents=bool)
        chB = Dcx(Address(part=0, lo=293, med=0, hi=0, medbit=0), cmd=b'\x02\x04', detents=bool)
        chC = Dcx(Address(part=0, lo=434, med=0, hi=0, medbit=0), cmd=b'\x03\x04', detents=bool)
        chS = Dcx(Address(part=0, lo=576, med=0, hi=0, medbit=0), cmd=b'\x04\x04', detents=bool)
    class EqSwitch(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=722, med=0, hi=0, medbit=0), cmd=b'\x05\x06', detents=bool)
        ch2 = Dcx(Address(part=0, lo=891, med=0, hi=0, medbit=0), cmd=b'\x06\x06', detents=bool)
        ch3 = Dcx(Address(part=1, lo=61, med=0, hi=0, medbit=0), cmd=b'\x07\x06', detents=bool)
        ch4 = Dcx(Address(part=1, lo=230, med=0, hi=0, medbit=0), cmd=b'\x08\x06', detents=bool)
        ch5 = Dcx(Address(part=1, lo=399, med=0, hi=0, medbit=0), cmd=b'\x09\x06', detents=bool)
        ch6 = Dcx(Address(part=1, lo=568, med=0, hi=0, medbit=0), cmd=b'\x0a\x06', detents=bool)
        chA = Dcx(Address(part=0, lo=155, med=0, hi=0, medbit=0), cmd=b'\x01\x06', detents=bool)
        chB = Dcx(Address(part=0, lo=297, med=0, hi=0, medbit=0), cmd=b'\x02\x06', detents=bool)
        chC = Dcx(Address(part=0, lo=439, med=0, hi=0, medbit=0), cmd=b'\x03\x06', detents=bool)
        chS = Dcx(Address(part=0, lo=581, med=0, hi=0, medbit=0), cmd=b'\x04\x06', detents=bool)
    class EqNumber(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=725, med=0, hi=0, medbit=0), cmd=b'\x05\x07', detents=int)
        ch2 = Dcx(Address(part=0, lo=894, med=0, hi=0, medbit=0), cmd=b'\x06\x07', detents=int)
        ch3 = Dcx(Address(part=1, lo=63, med=0, hi=0, medbit=0), cmd=b'\x07\x07', detents=int)
        ch4 = Dcx(Address(part=1, lo=232, med=0, hi=0, medbit=0), cmd=b'\x08\x07', detents=int)
        ch5 = Dcx(Address(part=1, lo=401, med=0, hi=0, medbit=0), cmd=b'\x09\x07', detents=int)
        ch6 = Dcx(Address(part=1, lo=570, med=0, hi=0, medbit=0), cmd=b'\x0a\x07', detents=int)
        chA = Dcx(Address(part=0, lo=158, med=0, hi=0, medbit=0), cmd=b'\x01\x07', detents=int)
        chB = Dcx(Address(part=0, lo=299, med=0, hi=0, medbit=0), cmd=b'\x02\x07', detents=int)
        chC = Dcx(Address(part=0, lo=441, med=0, hi=0, medbit=0), cmd=b'\x03\x07', detents=int)
        chS = Dcx(Address(part=0, lo=583, med=0, hi=0, medbit=0), cmd=b'\x04\x07', detents=int)
    class EqIndex(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=727, med=0, hi=0, medbit=0), cmd=b'\x05\x08', detents=int)
        ch2 = Dcx(Address(part=0, lo=896, med=0, hi=0, medbit=0), cmd=b'\x06\x08', detents=int)
        ch3 = Dcx(Address(part=1, lo=65, med=0, hi=0, medbit=0), cmd=b'\x07\x08', detents=int)
        ch4 = Dcx(Address(part=1, lo=234, med=0, hi=0, medbit=0), cmd=b'\x08\x08', detents=int)
        ch5 = Dcx(Address(part=1, lo=403, med=0, hi=0, medbit=0), cmd=b'\x09\x08', detents=int)
        ch6 = Dcx(Address(part=1, lo=573, med=0, hi=0, medbit=0), cmd=b'\x0a\x08', detents=int)
        chA = Dcx(Address(part=0, lo=160, med=0, hi=0, medbit=0), cmd=b'\x01\x08', detents=int)
        chB = Dcx(Address(part=0, lo=302, med=0, hi=0, medbit=0), cmd=b'\x02\x08', detents=int)
        chC = Dcx(Address(part=0, lo=443, med=0, hi=0, medbit=0), cmd=b'\x03\x08', detents=int)
        chS = Dcx(Address(part=0, lo=585, med=0, hi=0, medbit=0), cmd=b'\x04\x08', detents=int)
    class Eq1(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=752, med=756, hi=753, medbit=3), cmd=b'\x05\x13', detents=freqEnum)
        freq2 = Dcx(Address(part=0, lo=921, med=924, hi=922, medbit=4), cmd=b'\x06\x13', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=90, med=92, hi=91, medbit=5), cmd=b'\x07\x13', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=259, med=260, hi=261, medbit=6), cmd=b'\x08\x13', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=429, med=436, hi=430, medbit=0), cmd=b'\x09\x13', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=598, med=604, hi=599, medbit=1), cmd=b'\x0a\x13', detents=freqEnum)
        freqA = Dcx(Address(part=0, lo=185, med=188, hi=186, medbit=4), cmd=b'\x01\x13', detents=freqEnum)
        freqB = Dcx(Address(part=0, lo=327, med=332, hi=328, medbit=2), cmd=b'\x02\x13', detents=freqEnum)
        freqC = Dcx(Address(part=0, lo=469, med=476, hi=470, medbit=0), cmd=b'\x03\x13', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=610, med=612, hi=611, medbit=5), cmd=b'\x04\x13', detents=freqEnum)

        Q1 = Dcx(Address(part=0, lo=754, med=0, hi=0, medbit=0), cmd=b'\x05\x14', detents=eqQ_Enum)
        Q2 = Dcx(Address(part=0, lo=923, med=0, hi=0, medbit=0), cmd=b'\x06\x14', detents=eqQ_Enum)
        Q3 = Dcx(Address(part=1, lo=93, med=0, hi=0, medbit=0), cmd=b'\x07\x14', detents=eqQ_Enum)
        Q4 = Dcx(Address(part=1, lo=262, med=0, hi=0, medbit=0), cmd=b'\x08\x14', detents=eqQ_Enum)
        Q5 = Dcx(Address(part=1, lo=431, med=0, hi=0, medbit=0), cmd=b'\x09\x14', detents=eqQ_Enum)
        Q6 = Dcx(Address(part=1, lo=600, med=0, hi=0, medbit=0), cmd=b'\x0a\x14', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=187, med=0, hi=0, medbit=0), cmd=b'\x01\x14', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=329, med=0, hi=0, medbit=0), cmd=b'\x02\x14', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=471, med=0, hi=0, medbit=0), cmd=b'\x03\x14', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=613, med=0, hi=0, medbit=0), cmd=b'\x04\x14', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=757, med=764, hi=758, medbit=0), cmd=b'\x05\x15', detents=gainScale)
        gain2 = Dcx(Address(part=0, lo=926, med=932, hi=927, medbit=1), cmd=b'\x06\x15', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=95, med=100, hi=96, medbit=2), cmd=b'\x07\x15', detents=gainScale)
        gain4 = Dcx(Address(part=1, lo=264, med=268, hi=265, medbit=3), cmd=b'\x08\x15', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=433, med=436, hi=434, medbit=4), cmd=b'\x09\x15', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=602, med=604, hi=603, medbit=5), cmd=b'\x0a\x15', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=190, med=196, hi=191, medbit=1), cmd=b'\x01\x15', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=331, med=332, hi=333, medbit=6), cmd=b'\x02\x15', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=473, med=476, hi=474, medbit=4), cmd=b'\x03\x15', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=615, med=620, hi=616, medbit=2), cmd=b'\x04\x15', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=759, med=0, hi=0, medbit=0), cmd=b'\x05\x16', detents=eqTypeEnum)
        type2 = Dcx(Address(part=0, lo=928, med=0, hi=0, medbit=0), cmd=b'\x06\x16', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=97, med=0, hi=0, medbit=0), cmd=b'\x07\x16', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=266, med=0, hi=0, medbit=0), cmd=b'\x08\x16', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=435, med=0, hi=0, medbit=0), cmd=b'\x09\x16', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=605, med=0, hi=0, medbit=0), cmd=b'\x0a\x16', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=192, med=0, hi=0, medbit=0), cmd=b'\x01\x16', detents=eqTypeEnum)
        typeB = Dcx(Address(part=0, lo=334, med=0, hi=0, medbit=0), cmd=b'\x02\x16', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=475, med=0, hi=0, medbit=0), cmd=b'\x03\x16', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=617, med=0, hi=0, medbit=0), cmd=b'\x04\x16', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=761, med=0, hi=0, medbit=0), cmd=b'\x05\x17', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=0, lo=930, med=0, hi=0, medbit=0), cmd=b'\x06\x17', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=99, med=0, hi=0, medbit=0), cmd=b'\x07\x17', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=269, med=0, hi=0, medbit=0), cmd=b'\x08\x17', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=438, med=0, hi=0, medbit=0), cmd=b'\x09\x17', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=607, med=0, hi=0, medbit=0), cmd=b'\x0a\x17', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=194, med=0, hi=0, medbit=0), cmd=b'\x01\x17', detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=336, med=0, hi=0, medbit=0), cmd=b'\x02\x17', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=478, med=0, hi=0, medbit=0), cmd=b'\x03\x17', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=619, med=0, hi=0, medbit=0), cmd=b'\x04\x17', detents=eqSlopeEnum)
    class Eq2(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=763, med=764, hi=765, medbit=6), cmd=b'\x05\x18', detents=freqEnum)
        freq2 = Dcx(Address(part=0, lo=933, med=940, hi=934, medbit=0), cmd=b'\x06\x18', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=102, med=108, hi=103, medbit=1), cmd=b'\x07\x18', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=271, med=276, hi=272, medbit=2), cmd=b'\x08\x18', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=440, med=444, hi=441, medbit=3), cmd=b'\x09\x18', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=609, med=612, hi=610, medbit=4), cmd=b'\x0a\x18', detents=freqEnum)
        freqA = Dcx(Address(part=0, lo=197, med=204, hi=198, medbit=0), cmd=b'\x01\x18', detents=freqEnum)
        freqB = Dcx(Address(part=0, lo=338, med=340, hi=339, medbit=5), cmd=b'\x02\x18', detents=freqEnum)
        freqC = Dcx(Address(part=0, lo=480, med=484, hi=481, medbit=3), cmd=b'\x03\x18', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=622, med=628, hi=623, medbit=1), cmd=b'\x04\x18', detents=freqEnum)

        Q1 = Dcx(Address(part=0, lo=766, med=0, hi=0, medbit=0), cmd=b'\x05\x19', detents=eqQ_Enum)
        Q2 = Dcx(Address(part=0, lo=935, med=0, hi=0, medbit=0), cmd=b'\x06\x19', detents=eqQ_Enum)
        Q3 = Dcx(Address(part=1, lo=104, med=0, hi=0, medbit=0), cmd=b'\x07\x19', detents=eqQ_Enum)
        Q4 = Dcx(Address(part=1, lo=273, med=0, hi=0, medbit=0), cmd=b'\x08\x19', detents=eqQ_Enum)
        Q5 = Dcx(Address(part=1, lo=442, med=0, hi=0, medbit=0), cmd=b'\x09\x19', detents=eqQ_Enum)
        Q6 = Dcx(Address(part=1, lo=611, med=0, hi=0, medbit=0), cmd=b'\x0a\x19', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=199, med=0, hi=0, medbit=0), cmd=b'\x01\x19', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=341, med=0, hi=0, medbit=0), cmd=b'\x02\x19', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=482, med=0, hi=0, medbit=0), cmd=b'\x03\x19', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=624, med=0, hi=0, medbit=0), cmd=b'\x04\x19', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=768, med=772, hi=769, medbit=3), cmd=b'\x05\x1a', detents=gainScale)
        gain2 = Dcx(Address(part=0, lo=937, med=940, hi=938, medbit=4), cmd=b'\x06\x1a', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=106, med=108, hi=107, medbit=5), cmd=b'\x07\x1a', detents=gainScale)
        gain4 = Dcx(Address(part=1, lo=275, med=276, hi=277, medbit=6), cmd=b'\x08\x1a', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=445, med=452, hi=446, medbit=0), cmd=b'\x09\x1a', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=614, med=620, hi=615, medbit=1), cmd=b'\x0a\x1a', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=201, med=204, hi=202, medbit=4), cmd=b'\x01\x1a', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=343, med=348, hi=344, medbit=2), cmd=b'\x02\x1a', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=485, med=492, hi=486, medbit=0), cmd=b'\x03\x1a', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=626, med=628, hi=627, medbit=5), cmd=b'\x04\x1a', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=770, med=0, hi=0, medbit=0), cmd=b'\x05\x1b', detents=eqTypeEnum)
        type2 = Dcx(Address(part=0, lo=939, med=0, hi=0, medbit=0), cmd=b'\x06\x1b', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=109, med=0, hi=0, medbit=0), cmd=b'\x07\x1b', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=278, med=0, hi=0, medbit=0), cmd=b'\x08\x1b', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=447, med=0, hi=0, medbit=0), cmd=b'\x09\x1b', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=616, med=0, hi=0, medbit=0), cmd=b'\x0a\x1b', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=203, med=0, hi=0, medbit=0), cmd=b'\x01\x1b', detents=eqTypeEnum)
        typeB = Dcx(Address(part=0, lo=345, med=0, hi=0, medbit=0), cmd=b'\x02\x1b', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=487, med=0, hi=0, medbit=0), cmd=b'\x03\x1b', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=629, med=0, hi=0, medbit=0), cmd=b'\x04\x1b', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=773, med=0, hi=0, medbit=0), cmd=b'\x05\x1c', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=0, lo=942, med=0, hi=0, medbit=0), cmd=b'\x06\x1c', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=111, med=0, hi=0, medbit=0), cmd=b'\x07\x1c', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=280, med=0, hi=0, medbit=0), cmd=b'\x08\x1c', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=449, med=0, hi=0, medbit=0), cmd=b'\x09\x1c', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=618, med=0, hi=0, medbit=0), cmd=b'\x0a\x1c', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=206, med=0, hi=0, medbit=0), cmd=b'\x01\x1c', detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=347, med=0, hi=0, medbit=0), cmd=b'\x02\x1c', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=489, med=0, hi=0, medbit=0), cmd=b'\x03\x1c', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=631, med=0, hi=0, medbit=0), cmd=b'\x04\x1c', detents=eqSlopeEnum)
    class Eq3(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=775, med=780, hi=776, medbit=2), cmd=b'\x05\x1d', detents=freqEnum)
        freq2 = Dcx(Address(part=0, lo=944, med=948, hi=945, medbit=3), cmd=b'\x06\x1d', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=113, med=116, hi=114, medbit=4), cmd=b'\x07\x1d', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=282, med=284, hi=283, medbit=5), cmd=b'\x08\x1d', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=451, med=452, hi=453, medbit=6), cmd=b'\x09\x1d', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=621, med=628, hi=622, medbit=0), cmd=b'\x0a\x1d', detents=freqEnum)
        freqA = Dcx(Address(part=0, lo=208, med=212, hi=209, medbit=3), cmd=b'\x01\x1d', detents=freqEnum)
        freqB = Dcx(Address(part=0, lo=350, med=356, hi=351, medbit=1), cmd=b'\x02\x1d', detents=freqEnum)
        freqC = Dcx(Address(part=0, lo=491, med=492, hi=493, medbit=6), cmd=b'\x03\x1d', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=633, med=636, hi=634, medbit=4), cmd=b'\x04\x1d', detents=freqEnum)

        Q1 = Dcx(Address(part=0, lo=777, med=0, hi=0, medbit=0), cmd=b'\x05\x1e', detents=eqQ_Enum)
        Q2 = Dcx(Address(part=0, lo=946, med=0, hi=0, medbit=0), cmd=b'\x06\x1e', detents=eqQ_Enum)
        Q3 = Dcx(Address(part=1, lo=115, med=0, hi=0, medbit=0), cmd=b'\x07\x1e', detents=eqQ_Enum)
        Q4 = Dcx(Address(part=1, lo=285, med=0, hi=0, medbit=0), cmd=b'\x08\x1e', detents=eqQ_Enum)
        Q5 = Dcx(Address(part=1, lo=454, med=0, hi=0, medbit=0), cmd=b'\x09\x1e', detents=eqQ_Enum)
        Q6 = Dcx(Address(part=1, lo=623, med=0, hi=0, medbit=0), cmd=b'\x0a\x1e', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=210, med=0, hi=0, medbit=0), cmd=b'\x01\x1e', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=352, med=0, hi=0, medbit=0), cmd=b'\x02\x1e', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=494, med=0, hi=0, medbit=0), cmd=b'\x03\x1e', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=635, med=0, hi=0, medbit=0), cmd=b'\x04\x1e', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=779, med=780, hi=781, medbit=6), cmd=b'\x05\x1f', detents=gainScale)
        gain2 = Dcx(Address(part=0, lo=949, med=956, hi=950, medbit=0), cmd=b'\x06\x1f', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=118, med=124, hi=119, medbit=1), cmd=b'\x07\x1f', detents=gainScale)
        gain4 = Dcx(Address(part=1, lo=287, med=292, hi=288, medbit=2), cmd=b'\x08\x1f', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=456, med=460, hi=457, medbit=3), cmd=b'\x09\x1f', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=625, med=628, hi=626, medbit=4), cmd=b'\x0a\x1f', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=213, med=220, hi=214, medbit=0), cmd=b'\x01\x1f', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=354, med=356, hi=355, medbit=5), cmd=b'\x02\x1f', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=496, med=500, hi=497, medbit=3), cmd=b'\x03\x1f', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=638, med=644, hi=639, medbit=1), cmd=b'\x04\x1f', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=782, med=0, hi=0, medbit=0), cmd=b'\x05\x20', detents=eqTypeEnum)
        type2 = Dcx(Address(part=0, lo=951, med=0, hi=0, medbit=0), cmd=b'\x06\x20', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=120, med=0, hi=0, medbit=0), cmd=b'\x07\x20', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=289, med=0, hi=0, medbit=0), cmd=b'\x08\x20', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=458, med=0, hi=0, medbit=0), cmd=b'\x09\x20', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=627, med=0, hi=0, medbit=0), cmd=b'\x0a\x20', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=215, med=0, hi=0, medbit=0), cmd=b'\x01\x20', detents=eqTypeEnum)
        typeB = Dcx(Address(part=0, lo=357, med=0, hi=0, medbit=0), cmd=b'\x02\x20', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=498, med=0, hi=0, medbit=0), cmd=b'\x03\x20', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=640, med=0, hi=0, medbit=0), cmd=b'\x04\x20', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=784, med=0, hi=0, medbit=0), cmd=b'\x05\x21', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=0, lo=953, med=0, hi=0, medbit=0), cmd=b'\x06\x21', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=122, med=0, hi=0, medbit=0), cmd=b'\x07\x21', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=291, med=0, hi=0, medbit=0), cmd=b'\x08\x21', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=461, med=0, hi=0, medbit=0), cmd=b'\x09\x21', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=630, med=0, hi=0, medbit=0), cmd=b'\x0a\x21', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=217, med=0, hi=0, medbit=0), cmd=b'\x01\x21', detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=359, med=0, hi=0, medbit=0), cmd=b'\x02\x21', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=501, med=0, hi=0, medbit=0), cmd=b'\x03\x21', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=642, med=0, hi=0, medbit=0), cmd=b'\x04\x21', detents=eqSlopeEnum)
    class Eq4(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=786, med=788, hi=787, medbit=5), cmd=b'\x05\x22', detents=freqEnum)
        freq2 = Dcx(Address(part=0, lo=955, med=956, hi=957, medbit=6), cmd=b'\x06\x22', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=125, med=132, hi=126, medbit=0), cmd=b'\x07\x22', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=294, med=300, hi=295, medbit=1), cmd=b'\x08\x22', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=463, med=468, hi=464, medbit=2), cmd=b'\x09\x22', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=632, med=636, hi=633, medbit=3), cmd=b'\x0a\x22', detents=freqEnum)
        freqA = Dcx(Address(part=0, lo=219, med=220, hi=221, medbit=6), cmd=b'\x01\x22', detents=freqEnum)
        freqB = Dcx(Address(part=0, lo=361, med=364, hi=362, medbit=4), cmd=b'\x02\x22', detents=freqEnum)
        freqC = Dcx(Address(part=0, lo=503, med=508, hi=504, medbit=2), cmd=b'\x03\x22', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=645, med=652, hi=646, medbit=0), cmd=b'\x04\x22', detents=freqEnum)

        Q1 = Dcx(Address(part=0, lo=789, med=0, hi=0, medbit=0), cmd=b'\x05\x23', detents=eqQ_Enum)
        Q2 = Dcx(Address(part=0, lo=958, med=0, hi=0, medbit=0), cmd=b'\x06\x23', detents=eqQ_Enum)
        Q3 = Dcx(Address(part=1, lo=127, med=0, hi=0, medbit=0), cmd=b'\x07\x23', detents=eqQ_Enum)
        Q4 = Dcx(Address(part=1, lo=296, med=0, hi=0, medbit=0), cmd=b'\x08\x23', detents=eqQ_Enum)
        Q5 = Dcx(Address(part=1, lo=465, med=0, hi=0, medbit=0), cmd=b'\x09\x23', detents=eqQ_Enum)
        Q6 = Dcx(Address(part=1, lo=634, med=0, hi=0, medbit=0), cmd=b'\x0a\x23', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=222, med=0, hi=0, medbit=0), cmd=b'\x01\x23', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=363, med=0, hi=0, medbit=0), cmd=b'\x02\x23', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=505, med=0, hi=0, medbit=0), cmd=b'\x03\x23', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=647, med=0, hi=0, medbit=0), cmd=b'\x04\x23', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=791, med=796, hi=792, medbit=2), cmd=b'\x05\x24', detents=gainScale)
        gain2 = Dcx(Address(part=0, lo=960, med=964, hi=961, medbit=3), cmd=b'\x06\x24', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=129, med=132, hi=130, medbit=4), cmd=b'\x07\x24', detents=gainScale)
        gain4= Dcx(Address(part=1, lo=298, med=300, hi=299, medbit=5), cmd=b'\x08\x24', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=467, med=468, hi=469, medbit=6), cmd=b'\x09\x24', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=637, med=644, hi=638, medbit=0), cmd=b'\x0a\x24', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=224, med=228, hi=225, medbit=3), cmd=b'\x01\x24', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=366, med=372, hi=367, medbit=1), cmd=b'\x02\x24', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=507, med=508, hi=509, medbit=6), cmd=b'\x03\x24', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=649, med=652, hi=650, medbit=4), cmd=b'\x04\x24', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=793, med=0, hi=0, medbit=0), cmd=b'\x05\x25', detents=eqTypeEnum)
        type2 = Dcx(Address(part=0, lo=962, med=0, hi=0, medbit=0), cmd=b'\x06\x25', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=131, med=0, hi=0, medbit=0), cmd=b'\x07\x25', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=301, med=0, hi=0, medbit=0), cmd=b'\x08\x25', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=470, med=0, hi=0, medbit=0), cmd=b'\x09\x25', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=639, med=0, hi=0, medbit=0), cmd=b'\x0a\x25', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=226, med=0, hi=0, medbit=0), cmd=b'\x01\x25', detents=eqTypeEnum)
        typeB = Dcx(Address(part=0, lo=368, med=0, hi=0, medbit=0), cmd=b'\x02\x25', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=510, med=0, hi=0, medbit=0), cmd=b'\x03\x25', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=651, med=0, hi=0, medbit=0), cmd=b'\x04\x25', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=795, med=0, hi=0, medbit=0), cmd=b'\x05\x26', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=0, lo=965, med=0, hi=0, medbit=0), cmd=b'\x06\x26', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=134, med=0, hi=0, medbit=0), cmd=b'\x07\x26', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=303, med=0, hi=0, medbit=0), cmd=b'\x08\x26', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=472, med=0, hi=0, medbit=0), cmd=b'\x09\x26', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=641, med=0, hi=0, medbit=0), cmd=b'\x0a\x26', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=229, med=0, hi=0, medbit=0), cmd=b'\x01\x26', detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=370, med=0, hi=0, medbit=0), cmd=b'\x02\x26', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=512, med=0, hi=0, medbit=0), cmd=b'\x03\x26', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=654, med=0, hi=0, medbit=0), cmd=b'\x04\x26', detents=eqSlopeEnum)
    class Eq5(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=798, med=804, hi=799, medbit=1), cmd=b'\x05\x27', detents=freqEnum)
        freq2 = Dcx(Address(part=0, lo=967, med=972, hi=968, medbit=2), cmd=b'\x06\x27', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=136, med=140, hi=137, medbit=3), cmd=b'\x07\x27', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=305, med=308, hi=306, medbit=4), cmd=b'\x08\x27', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=474, med=476, hi=475, medbit=5), cmd=b'\x09\x27', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=643, med=644, hi=645, medbit=6), cmd=b'\x0a\x27', detents=freqEnum)
        freqA = Dcx(Address(part=0, lo=231, med=236, hi=232, medbit=2), cmd=b'\x01\x27', detents=freqEnum)
        freqB = Dcx(Address(part=0, lo=373, med=380, hi=374, medbit=0), cmd=b'\x02\x27', detents=freqEnum)
        freqC = Dcx(Address(part=0, lo=514, med=516, hi=515, medbit=5), cmd=b'\x03\x27', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=656, med=660, hi=657, medbit=3), cmd=b'\x04\x27', detents=freqEnum)

        Q1 =  Dcx(Address(part=0, lo=800, med=0, hi=0, medbit=0), cmd=b'\x05\x28', detents=eqQ_Enum)
        Q2 =  Dcx(Address(part=0, lo=969, med=0, hi=0, medbit=0), cmd=b'\x06\x28', detents=eqQ_Enum)
        Q3 =  Dcx(Address(part=1, lo=138, med=0, hi=0, medbit=0), cmd=b'\x07\x28', detents=eqQ_Enum)
        Q4 =  Dcx(Address(part=1, lo=307, med=0, hi=0, medbit=0), cmd=b'\x08\x28', detents=eqQ_Enum)
        Q5 =  Dcx(Address(part=1, lo=477, med=0, hi=0, medbit=0), cmd=b'\x09\x28', detents=eqQ_Enum)
        Q6 =  Dcx(Address(part=1, lo=646, med=0, hi=0, medbit=0), cmd=b'\x0a\x28', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=233, med=0, hi=0, medbit=0), cmd=b'\x01\x28', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=375, med=0, hi=0, medbit=0), cmd=b'\x02\x28', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=517, med=0, hi=0, medbit=0), cmd=b'\x03\x28', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=658, med=0, hi=0, medbit=0), cmd=b'\x04\x28', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=802, med=804, hi=803, medbit=5), cmd=b'\x05\x29', detents=gainScale)
        gain2 = Dcx(Address(part=0, lo=971, med=972, hi=973, medbit=6), cmd=b'\x06\x29', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=141, med=148, hi=142, medbit=0), cmd=b'\x07\x29', detents=gainScale)
        gain4 = Dcx(Address(part=1, lo=310, med=316, hi=311, medbit=1), cmd=b'\x08\x29', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=479, med=484, hi=480, medbit=2), cmd=b'\x09\x29', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=648, med=652, hi=649, medbit=3), cmd=b'\x0a\x29', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=235, med=236, hi=237, medbit=6), cmd=b'\x01\x29', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=377, med=380, hi=378, medbit=4), cmd=b'\x02\x29', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=519, med=524, hi=520, medbit=2), cmd=b'\x03\x29', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=661, med=668, hi=662, medbit=0), cmd=b'\x04\x29', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=805, med=0, hi=0, medbit=0), cmd=b'\x05\x2a', detents=eqTypeEnum)
        type2 = Dcx(Address(part=0, lo=974, med=0, hi=0, medbit=0), cmd=b'\x06\x2a', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=143, med=0, hi=0, medbit=0), cmd=b'\x07\x2a', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=312, med=0, hi=0, medbit=0), cmd=b'\x08\x2a', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=481, med=0, hi=0, medbit=0), cmd=b'\x09\x2a', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=650, med=0, hi=0, medbit=0), cmd=b'\x0a\x2a', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=238, med=0, hi=0, medbit=0), cmd=b'\x01\x2a', detents=eqTypeEnum)
        typeB = Dcx(Address(part=0, lo=379, med=0, hi=0, medbit=0), cmd=b'\x02\x2a', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=521, med=0, hi=0, medbit=0), cmd=b'\x03\x2a', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=663, med=0, hi=0, medbit=0), cmd=b'\x04\x2a', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=807, med=0, hi=0, medbit=0), cmd=b'\x05\x2b', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=0, lo=976, med=0, hi=0, medbit=0), cmd=b'\x06\x2b', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=145, med=0, hi=0, medbit=0), cmd=b'\x07\x2b', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=314, med=0, hi=0, medbit=0), cmd=b'\x08\x2b', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=483, med=0, hi=0, medbit=0), cmd=b'\x09\x2b', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=653, med=0, hi=0, medbit=0), cmd=b'\x0a\x2b', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=240, med=0, hi=0, medbit=0), cmd=b'\x01\x2b', detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=382, med=0, hi=0, medbit=0), cmd=b'\x02\x2b', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=523, med=0, hi=0, medbit=0), cmd=b'\x03\x2b', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=665, med=0, hi=0, medbit=0), cmd=b'\x04\x2b', detents=eqSlopeEnum)
    class Eq6(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=809, med=812, hi=810, medbit=4), cmd=b'\x05\x2c', detents=freqEnum)
        freq2 = Dcx(Address(part=0, lo=978, med=980, hi=979, medbit=5), cmd=b'\x06\x2c', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=147, med=148, hi=149, medbit=6), cmd=b'\x07\x2c', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=317, med=324, hi=318, medbit=0), cmd=b'\x08\x2c', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=486, med=492, hi=487, medbit=1), cmd=b'\x09\x2c', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=655, med=660, hi=656, medbit=2), cmd=b'\x0a\x2c', detents=freqEnum)
        freqA= Dcx(Address(part=0, lo=242, med=244, hi=243, medbit=5), cmd=b'\x01\x2c', detents=freqEnum)
        freqB= Dcx(Address(part=0, lo=384, med=388, hi=385, medbit=3), cmd=b'\x02\x2c', detents=freqEnum)
        freqC= Dcx(Address(part=0, lo=526, med=532, hi=527, medbit=1), cmd=b'\x03\x2c', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=667, med=668, hi=669, medbit=6), cmd=b'\x04\x2c', detents=freqEnum)

        Q1 =  Dcx(Address(part=0, lo=811, med=0, hi=0, medbit=0), cmd=b'\x05\x2d', detents=eqQ_Enum)
        Q2 =  Dcx(Address(part=0, lo=981, med=0, hi=0, medbit=0), cmd=b'\x06\x2d', detents=eqQ_Enum)
        Q3 =  Dcx(Address(part=1, lo=150, med=0, hi=0, medbit=0), cmd=b'\x07\x2d', detents=eqQ_Enum)
        Q4 =  Dcx(Address(part=1, lo=319, med=0, hi=0, medbit=0), cmd=b'\x08\x2d', detents=eqQ_Enum)
        Q5 =  Dcx(Address(part=1, lo=488, med=0, hi=0, medbit=0), cmd=b'\x09\x2d', detents=eqQ_Enum)
        Q6 =  Dcx(Address(part=1, lo=657, med=0, hi=0, medbit=0), cmd=b'\x0a\x2d', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=245, med=0, hi=0, medbit=0), cmd=b'\x01\x2d', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=386, med=0, hi=0, medbit=0), cmd=b'\x02\x2d', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=528, med=0, hi=0, medbit=0), cmd=b'\x03\x2d', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=670, med=0, hi=0, medbit=0), cmd=b'\x04\x2d', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=814, med=820, hi=815, medbit=1), cmd=b'\x05\x2e', detents=gainScale)
        gain2 = Dcx(Address(part=0, lo=983, med=988, hi=984, medbit=2), cmd=b'\x06\x2e', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=152, med=156, hi=153, medbit=3), cmd=b'\x07\x2e', detents=gainScale)
        gain4 = Dcx(Address(part=1, lo=321, med=324, hi=322, medbit=4), cmd=b'\x08\x2e', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=490, med=492, hi=491, medbit=5), cmd=b'\x09\x2e', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=659, med=660, hi=661, medbit=6), cmd=b'\x0a\x2e', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=247, med=252, hi=248, medbit=2), cmd=b'\x01\x2e', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=389, med=396, hi=390, medbit=0), cmd=b'\x02\x2e', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=530, med=532, hi=531, medbit=5), cmd=b'\x03\x2e', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=672, med=676, hi=673, medbit=3), cmd=b'\x04\x2e', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=816, med=0, hi=0, medbit=0), cmd=b'\x05\x2f', detents=eqTypeEnum)
        type2 = Dcx(Address(part=0, lo=985, med=0, hi=0, medbit=0), cmd=b'\x06\x2f', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=154, med=0, hi=0, medbit=0), cmd=b'\x07\x2f', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=323, med=0, hi=0, medbit=0), cmd=b'\x08\x2f', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=493, med=0, hi=0, medbit=0), cmd=b'\x09\x2f', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=662, med=0, hi=0, medbit=0), cmd=b'\x0a\x2f', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=249, med=0, hi=0, medbit=0), cmd=b'\x01\x2f', detents=eqTypeEnum)
        typeB= Dcx(Address(part=0, lo=391, med=0, hi=0, medbit=0), cmd=b'\x02\x2f', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=533, med=0, hi=0, medbit=0), cmd=b'\x03\x2f', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=674, med=0, hi=0, medbit=0), cmd=b'\x04\x2f', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=818, med=0, hi=0, medbit=0), cmd=b'\x05\x30', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=0, lo=987, med=0, hi=0, medbit=0), cmd=b'\x06\x30', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=157, med=0, hi=0, medbit=0), cmd=b'\x07\x30', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=326, med=0, hi=0, medbit=0), cmd=b'\x08\x30', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=495, med=0, hi=0, medbit=0), cmd=b'\x09\x30', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=664, med=0, hi=0, medbit=0), cmd=b'\x0a\x30', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=251, med=0, hi=0, medbit=0), cmd=b'\x01\x30', detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=393, med=0, hi=0, medbit=0), cmd=b'\x02\x30', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=535, med=0, hi=0, medbit=0), cmd=b'\x03\x30', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=677, med=0, hi=0, medbit=0), cmd=b'\x04\x30', detents=eqSlopeEnum)
    class Eq7(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=821, med=828, hi=822, medbit=0), cmd=b'\x05\x31', detents=freqEnum)
        freq2 = Dcx(Address(part=0, lo=990, med=996, hi=991, medbit=1), cmd=b'\x06\x31', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=159, med=164, hi=160, medbit=2), cmd=b'\x07\x31', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=328, med=332, hi=329, medbit=3), cmd=b'\x08\x31', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=497, med=500, hi=498, medbit=4), cmd=b'\x09\x31', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=666, med=668, hi=667, medbit=5), cmd=b'\x0a\x31', detents=freqEnum)
        freqA = Dcx(Address(part=0, lo=254, med=260, hi=255, medbit=1), cmd=b'\x01\x31', detents=freqEnum)
        freqB = Dcx(Address(part=0, lo=395, med=396, hi=397, medbit=6), cmd=b'\x02\x31', detents=freqEnum)
        freqC = Dcx(Address(part=0, lo=537, med=540, hi=538, medbit=4), cmd=b'\x03\x31', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=679, med=684, hi=680, medbit=2), cmd=b'\x04\x31', detents=freqEnum)

        Q1 = Dcx(Address(part=0, lo=823, med=0, hi=0, medbit=0), cmd=b'\x05\x32', detents=eqQ_Enum)
        Q2 = Dcx(Address(part=0, lo=992, med=0, hi=0, medbit=0), cmd=b'\x06\x32', detents=eqQ_Enum)
        Q3 = Dcx(Address(part=1, lo=161, med=0, hi=0, medbit=0), cmd=b'\x07\x32', detents=eqQ_Enum)
        Q4 = Dcx(Address(part=1, lo=330, med=0, hi=0, medbit=0), cmd=b'\x08\x32', detents=eqQ_Enum)
        Q5 = Dcx(Address(part=1, lo=499, med=0, hi=0, medbit=0), cmd=b'\x09\x32', detents=eqQ_Enum)
        Q6 = Dcx(Address(part=1, lo=669, med=0, hi=0, medbit=0), cmd=b'\x0a\x32', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=256, med=0, hi=0, medbit=0), cmd=b'\x01\x32', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=398, med=0, hi=0, medbit=0), cmd=b'\x02\x32', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=539, med=0, hi=0, medbit=0), cmd=b'\x03\x32', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=681, med=0, hi=0, medbit=0), cmd=b'\x04\x32', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=825, med=828, hi=826, medbit=4), cmd=b'\x05\x33', detents=gainScale)
        gain2 = Dcx(Address(part=0, lo=994, med=996, hi=995, medbit=5), cmd=b'\x06\x33', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=163, med=164, hi=165, medbit=6), cmd=b'\x07\x33', detents=gainScale)
        gain4 = Dcx(Address(part=1, lo=333, med=340, hi=334, medbit=0), cmd=b'\x08\x33', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=502, med=508, hi=503, medbit=1), cmd=b'\x09\x33', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=671, med=676, hi=672, medbit=2), cmd=b'\x0a\x33', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=258, med=260, hi=259, medbit=5), cmd=b'\x01\x33', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=400, med=404, hi=401, medbit=3), cmd=b'\x02\x33', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=542, med=548, hi=543, medbit=1), cmd=b'\x03\x33', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=683, med=684, hi=685, medbit=6), cmd=b'\x04\x33', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=827, med=0, hi=0, medbit=0), cmd=b'\x05\x34', detents=eqTypeEnum)
        type2 = Dcx(Address(part=0, lo=997, med=0, hi=0, medbit=0), cmd=b'\x06\x34', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=166, med=0, hi=0, medbit=0), cmd=b'\x07\x34', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=335, med=0, hi=0, medbit=0), cmd=b'\x08\x34', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=504, med=0, hi=0, medbit=0), cmd=b'\x09\x34', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=679, med=0, hi=0, medbit=0), cmd=b'\x0a\x34', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=261, med=0, hi=0, medbit=0), cmd=b'\x01\x34', detents=eqTypeEnum)
        typeB = Dcx(Address(part=0, lo=402, med=0, hi=0, medbit=0), cmd=b'\x02\x34', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=544, med=0, hi=0, medbit=0), cmd=b'\x03\x34', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=686, med=0, hi=0, medbit=0), cmd=b'\x04\x34', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=830, med=0, hi=0, medbit=0), cmd=b'\x05\x35', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=0, lo=999, med=0, hi=0, medbit=0), cmd=b'\x06\x35', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=168, med=0, hi=0, medbit=0), cmd=b'\x07\x35', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=337, med=0, hi=0, medbit=0), cmd=b'\x08\x35', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=506, med=0, hi=0, medbit=0), cmd=b'\x09\x35', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=675, med=0, hi=0, medbit=0), cmd=b'\x0a\x35', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=263, med=0, hi=0, medbit=0), cmd=b'\x01\x35', detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=405, med=0, hi=0, medbit=0), cmd=b'\x02\x35', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=546, med=0, hi=0, medbit=0), cmd=b'\x03\x35', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=688, med=0, hi=0, medbit=0), cmd=b'\x04\x35', detents=eqSlopeEnum)
    class Eq8(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=832, med=836, hi=833, medbit=3), cmd=b'\x05\x36', detents=freqEnum)
        freq2 = Dcx(Address(part=0, lo=1001, med=1004, hi=1002, medbit=4), cmd=b'\x06\x36', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=170, med=172, hi=171, medbit=5), cmd=b'\x07\x36', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=339, med=340, hi=341, medbit=6), cmd=b'\x08\x36', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=509, med=516, hi=510, medbit=0), cmd=b'\x09\x36', detents=freqEnum)
        # freq6 = Dcx(Address(part=1, lo=678, med=684, hi=679, medbit=1), cmd=b'\x0a\x36', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=678, med=684, hi=679, medbit=1), cmd=b'\x0a\x36', detents=freqEnum)
        freqA = Dcx(Address(part=0, lo=265, med=268, hi=266, medbit=4), cmd=b'\x01\x36', detents=freqEnum)
        freqB = Dcx(Address(part=0, lo=407, med=412, hi=408, medbit=2), cmd=b'\x02\x36', detents=freqEnum)
        freqC = Dcx(Address(part=0, lo=549, med=556, hi=550, medbit=0), cmd=b'\x03\x36', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=690, med=692, hi=691, medbit=5), cmd=b'\x04\x36', detents=freqEnum)

        Q1 = Dcx(Address(part=0, lo=834, med=0, hi=0, medbit=0), cmd=b'\x05\x37', detents=eqQ_Enum)
        Q2 = Dcx(Address(part=0, lo=1003, med=0, hi=0, medbit=0), cmd=b'\x06\x37', detents=eqQ_Enum)
        Q3 = Dcx(Address(part=1, lo=173, med=0, hi=0, medbit=0), cmd=b'\x07\x37', detents=eqQ_Enum)
        Q4 = Dcx(Address(part=1, lo=342, med=0, hi=0, medbit=0), cmd=b'\x08\x37', detents=eqQ_Enum)
        Q5 = Dcx(Address(part=1, lo=511, med=0, hi=0, medbit=0), cmd=b'\x09\x37', detents=eqQ_Enum)
        Q6 = Dcx(Address(part=1, lo=680, med=0, hi=0, medbit=0), cmd=b'\x0a\x37', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=267, med=0, hi=0, medbit=0), cmd=b'\x01\x37', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=409, med=0, hi=0, medbit=0), cmd=b'\x02\x37', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=551, med=0, hi=0, medbit=0), cmd=b'\x03\x37', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=693, med=0, hi=0, medbit=0), cmd=b'\x04\x37', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=837, med=844, hi=838, medbit=0), cmd=b'\x05\x38', detents=gainScale)
        gain2 = Dcx(Address(part=0, lo=1006, med=1012, hi=1007, medbit=1), cmd=b'\x06\x38', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=175, med=180, hi=176, medbit=2), cmd=b'\x07\x38', detents=gainScale)
        gain4 = Dcx(Address(part=1, lo=344, med=348, hi=345, medbit=3), cmd=b'\x08\x38', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=513, med=516, hi=514, medbit=4), cmd=b'\x09\x38', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=682, med=684, hi=683, medbit=5), cmd=b'\x0a\x38', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=270, med=276, hi=271, medbit=1), cmd=b'\x01\x38', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=411, med=412, hi=413, medbit=6), cmd=b'\x02\x38', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=553, med=556, hi=554, medbit=4), cmd=b'\x03\x38', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=695, med=700, hi=696, medbit=2), cmd=b'\x04\x38', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=839, med=0, hi=0, medbit=0), cmd=b'\x05\x39', detents=eqTypeEnum)
        type2 = Dcx(Address(part=0, lo=1008, med=0, hi=0, medbit=0), cmd=b'\x06\x39', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=177, med=0, hi=0, medbit=0), cmd=b'\x07\x39', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=346, med=0, hi=0, medbit=0), cmd=b'\x08\x39', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=515, med=0, hi=0, medbit=0), cmd=b'\x09\x39', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=685, med=0, hi=0, medbit=0), cmd=b'\x0a\x39', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=272, med=0, hi=0, medbit=0), cmd=b'\x01\x39', detents=eqTypeEnum)
        typeB = Dcx(Address(part=0, lo=414, med=0, hi=0, medbit=0), cmd=b'\x02\x39', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=555, med=0, hi=0, medbit=0), cmd=b'\x03\x39', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=697, med=0, hi=0, medbit=0), cmd=b'\x04\x39', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=841, med=0, hi=0, medbit=0), cmd=b'\x05\x3a', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=0, lo=1010, med=0, hi=0, medbit=0), cmd=b'\x06\x3a', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=179, med=0, hi=0, medbit=0), cmd=b'\x07\x3a', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=349, med=0, hi=0, medbit=0), cmd=b'\x08\x3a', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=518, med=0, hi=0, medbit=0), cmd=b'\x09\x3a', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=687, med=0, hi=0, medbit=0), cmd=b'\x0a\x3a', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=274, med=0, hi=0, medbit=0), cmd=b'\x01\x3a', detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=416, med=0, hi=0, medbit=0), cmd=b'\x02\x3a', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=558, med=0, hi=0, medbit=0), cmd=b'\x03\x3a', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=699, med=0, hi=0, medbit=0), cmd=b'\x04\x3a', detents=eqSlopeEnum)
    class Eq9(Dcx, Enum):
        freq1 = Dcx(Address(part=0, lo=843, med=844, hi=845, medbit=6), cmd=b'\x05\x3b', detents=freqEnum)
        freq2 = Dcx(Address(part=1, lo=13, med=20, hi=14, medbit=0), cmd=b'\x06\x3b', detents=freqEnum)
        freq3 = Dcx(Address(part=1, lo=182, med=188, hi=183, medbit=1), cmd=b'\x07\x3b', detents=freqEnum)
        freq4 = Dcx(Address(part=1, lo=351, med=356, hi=352, medbit=2), cmd=b'\x08\x3b', detents=freqEnum)
        freq5 = Dcx(Address(part=1, lo=520, med=524, hi=521, medbit=3), cmd=b'\x09\x3b', detents=freqEnum)
        freq6 = Dcx(Address(part=1, lo=689, med=692, hi=690, medbit=4), cmd=b'\x0a\x3b', detents=freqEnum)
        freqA = Dcx(Address(part=0, lo=277, med=284, hi=278, medbit=0), cmd=b'\x01\x3b', detents=freqEnum)
        freqB = Dcx(Address(part=0, lo=418, med=420, hi=419, medbit=5), cmd=b'\x02\x3b', detents=freqEnum)
        freqC = Dcx(Address(part=0, lo=560, med=564, hi=561, medbit=3), cmd=b'\x03\x3b', detents=freqEnum)
        freqS = Dcx(Address(part=0, lo=702, med=708, hi=703, medbit=1), cmd=b'\x04\x3b', detents=freqEnum)

        Q1 = Dcx(Address(part=0, lo=846, med=0, hi=0, medbit=0), cmd=b'\x05\x3c', detents=eqQ_Enum)
        Q2 = Dcx(Address(part=1, lo=15, med=0, hi=0, medbit=0), cmd=b'\x06\x3c', detents=eqQ_Enum)
        Q3 = Dcx(Address(part=1, lo=184, med=0, hi=0, medbit=0), cmd=b'\x07\x3c', detents=eqQ_Enum)
        Q4 = Dcx(Address(part=1, lo=353, med=0, hi=0, medbit=0), cmd=b'\x08\x3c', detents=eqQ_Enum)
        Q5 = Dcx(Address(part=1, lo=522, med=0, hi=0, medbit=0), cmd=b'\x09\x3c', detents=eqQ_Enum)
        Q6 = Dcx(Address(part=1, lo=691, med=0, hi=0, medbit=0), cmd=b'\x0a\x3c', detents=eqQ_Enum)
        QA = Dcx(Address(part=0, lo=279, med=0, hi=0, medbit=0), cmd=b'\x01\x3c', detents=eqQ_Enum)
        QB = Dcx(Address(part=0, lo=421, med=0, hi=0, medbit=0), cmd=b'\x02\x3c', detents=eqQ_Enum)
        QC = Dcx(Address(part=0, lo=562, med=0, hi=0, medbit=0), cmd=b'\x03\x3c', detents=eqQ_Enum)
        QS = Dcx(Address(part=0, lo=704, med=0, hi=0, medbit=0), cmd=b'\x04\x3c', detents=eqQ_Enum)

        gain1 = Dcx(Address(part=0, lo=848, med=852, hi=849, medbit=3), cmd=b'\x05\x3d', detents=gainScale)
        gain2 = Dcx(Address(part=1, lo=17, med=20, hi=18, medbit=4), cmd=b'\x06\x3d', detents=gainScale)
        gain3 = Dcx(Address(part=1, lo=186, med=188, hi=187, medbit=5), cmd=b'\x07\x3d', detents=gainScale)
        gain4 = Dcx(Address(part=1, lo=355, med=356, hi=357, medbit=6), cmd=b'\x08\x3d', detents=gainScale)
        gain5 = Dcx(Address(part=1, lo=525, med=532, hi=526, medbit=0), cmd=b'\x09\x3d', detents=gainScale)
        gain6 = Dcx(Address(part=1, lo=694, med=700, hi=695, medbit=1), cmd=b'\x0a\x3d', detents=gainScale)
        gainA = Dcx(Address(part=0, lo=281, med=284, hi=282, medbit=4), cmd=b'\x01\x3d', detents=gainScale)
        gainB = Dcx(Address(part=0, lo=423, med=428, hi=424, medbit=2), cmd=b'\x02\x3d', detents=gainScale)
        gainC = Dcx(Address(part=0, lo=565, med=572, hi=566, medbit=0), cmd=b'\x03\x3d', detents=gainScale)
        gainS = Dcx(Address(part=0, lo=706, med=708, hi=707, medbit=5), cmd=b'\x04\x3d', detents=gainScale)

        type1 = Dcx(Address(part=0, lo=850, med=0, hi=0, medbit=0), cmd=b'\x05\x3e', detents=eqTypeEnum)
        type2 = Dcx(Address(part=1, lo=19, med=0, hi=0, medbit=0), cmd=b'\x06\x3e', detents=eqTypeEnum)
        type3 = Dcx(Address(part=1, lo=189, med=0, hi=0, medbit=0), cmd=b'\x07\x3e', detents=eqTypeEnum)
        type4 = Dcx(Address(part=1, lo=358, med=0, hi=0, medbit=0), cmd=b'\x08\x3e', detents=eqTypeEnum)
        type5 = Dcx(Address(part=1, lo=527, med=0, hi=0, medbit=0), cmd=b'\x09\x3e', detents=eqTypeEnum)
        type6 = Dcx(Address(part=1, lo=696, med=0, hi=0, medbit=0), cmd=b'\x0a\x3e', detents=eqTypeEnum)
        typeA = Dcx(Address(part=0, lo=283, med=0, hi=0, medbit=0), cmd=b'\x01\x3e', detents=eqTypeEnum)
        typeB = Dcx(Address(part=0, lo=425, med=0, hi=0, medbit=0), cmd=b'\x02\x3e', detents=eqTypeEnum)
        typeC = Dcx(Address(part=0, lo=567, med=0, hi=0, medbit=0), cmd=b'\x03\x3e', detents=eqTypeEnum)
        typeS = Dcx(Address(part=0, lo=709, med=0, hi=0, medbit=0), cmd=b'\x04\x3e', detents=eqTypeEnum)

        slope1 = Dcx(Address(part=0, lo=853, med=0, hi=0, medbit=0), cmd=b'\x05\x3f', detents=eqSlopeEnum)
        slope2 = Dcx(Address(part=1, lo=22, med=0, hi=0, medbit=0), cmd=b'\x06\x3f', detents=eqSlopeEnum)
        slope3 = Dcx(Address(part=1, lo=191, med=0, hi=0, medbit=0), cmd=b'\x07\x3f', detents=eqSlopeEnum)
        slope4 = Dcx(Address(part=1, lo=360, med=0, hi=0, medbit=0), cmd=b'\x08\x3f', detents=eqSlopeEnum)
        slope5 = Dcx(Address(part=1, lo=529, med=0, hi=0, medbit=0), cmd=b'\x09\x3f', detents=eqSlopeEnum)
        slope6 = Dcx(Address(part=1, lo=698, med=0, hi=0, medbit=0), cmd=b'\x0a\x3f', detents=eqSlopeEnum)
        slopeA = Dcx(Address(part=0, lo=286, med=0, hi=0, medbit=0), cmd=b'\x01\x3f',detents=eqSlopeEnum)
        slopeB = Dcx(Address(part=0, lo=427, med=0, hi=0, medbit=0), cmd=b'\x02\x3f', detents=eqSlopeEnum)
        slopeC = Dcx(Address(part=0, lo=569, med=0, hi=0, medbit=0), cmd=b'\x03\x3f', detents=eqSlopeEnum)
        slopeS = Dcx(Address(part=0, lo=711, med=0, hi=0, medbit=0), cmd=b'\x04\x3f', detents=eqSlopeEnum)
    class ChNames(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=855, med=0, hi=0, medbit=0), cmd=b'\x05\x40', detents=chNameEnum)
        ch2 = Dcx(Address(part=1, lo=24, med=0, hi=0, medbit=0), cmd=b'\x06\x40', detents=chNameEnum)
        ch3 = Dcx(Address(part=1, lo=193, med=0, hi=0, medbit=0), cmd=b'\x07\x40', detents=chNameEnum)
        ch4 = Dcx(Address(part=1, lo=362, med=0, hi=0, medbit=0), cmd=b'\x08\x40', detents=chNameEnum)
        ch5 = Dcx(Address(part=1, lo=531, med=0, hi=0, medbit=0), cmd=b'\x09\x40', detents=chNameEnum)
        ch6 = Dcx(Address(part=1, lo=701, med=0, hi=0, medbit=0), cmd=b'\x0a\x40', detents=chNameEnum)
    class Sources(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=857, med=0, hi=0, medbit=0), cmd=b'\x05\x41', detents=sourcesEnum)
        ch2 =  Dcx(Address(part=1, lo=26, med=0, hi=0, medbit=0), cmd=b'\x06\x41', detents=sourcesEnum)
        ch3 = Dcx(Address(part=1, lo=195, med=0, hi=0, medbit=0), cmd=b'\x07\x41', detents=sourcesEnum)
        ch4 = Dcx(Address(part=1, lo=365, med=0, hi=0, medbit=0), cmd=b'\x08\x41', detents=sourcesEnum)
        ch5 = Dcx(Address(part=1, lo=534, med=0, hi=0, medbit=0), cmd=b'\x09\x41', detents=sourcesEnum)
        ch6 = Dcx(Address(part=1, lo=703, med=0, hi=0, medbit=0), cmd=b'\x0a\x41', detents=sourcesEnum)
    class Crossover(Dcx, Enum):
        hpCurve01 = Dcx(Address(part=0, lo=859, med=0, hi=0, medbit=0), cmd=b'\x05\x42', detents=xoCurveEnum)
        hpCurve02 = Dcx(Address(part=1, lo=29, med=0, hi=0, medbit=0), cmd=b'\x06\x42', detents=xoCurveEnum)
        hpCurve03 = Dcx(Address(part=1, lo=198, med=0, hi=0, medbit=0), cmd=b'\x07\x42', detents=xoCurveEnum)
        hpCurve04 = Dcx(Address(part=1, lo=367, med=0, hi=0, medbit=0), cmd=b'\x08\x42', detents=xoCurveEnum)
        hpCurve05 = Dcx(Address(part=1, lo=536, med=0, hi=0, medbit=0), cmd=b'\x09\x42', detents=xoCurveEnum)
        hpCurve06 = Dcx(Address(part=1, lo=705, med=0, hi=0, medbit=0), cmd=b'\x0a\x42', detents=xoCurveEnum)

        hpFreq01 = Dcx(Address(part=0, lo=862, med=868, hi=863, medbit=1), cmd=b'\x05\x43', detents=freqEnum)
        hpFreq02 = Dcx(Address(part=1, lo=31, med=36, hi=32, medbit=2), cmd=b'\x06\x43', detents=freqEnum)
        hpFreq03 = Dcx(Address(part=1, lo=200, med=204, hi=201, medbit=3), cmd=b'\x07\x43', detents=freqEnum)
        hpFreq04 = Dcx(Address(part=1, lo=369, med=372, hi=370, medbit=4), cmd=b'\x08\x43', detents=freqEnum)
        hpFreq05 = Dcx(Address(part=1, lo=538, med=540, hi=539, medbit=5), cmd=b'\x09\x43', detents=freqEnum)
        hpFreq06 = Dcx(Address(part=1, lo=707, med=708, hi=709, medbit=6), cmd=b'\x0a\x43', detents=freqEnum)

        lpCurve01 = Dcx(Address(part=0, lo=864, med=0, hi=0, medbit=0), cmd=b'\x05\x44', detents=xoCurveEnum)
        lpCurve02 = Dcx(Address(part=1, lo=33, med=0, hi=0, medbit=0), cmd=b'\x06\x44', detents=xoCurveEnum)
        lpCurve03 = Dcx(Address(part=1, lo=202, med=0, hi=0, medbit=0), cmd=b'\x07\x44', detents=xoCurveEnum)
        lpCurve04 = Dcx(Address(part=1, lo=371, med=0, hi=0, medbit=0), cmd=b'\x08\x44', detents=xoCurveEnum)
        lpCurve05 = Dcx(Address(part=1, lo=541, med=0, hi=0, medbit=0), cmd=b'\x09\x44', detents=xoCurveEnum)
        lpCurve06 = Dcx(Address(part=1, lo=710, med=0, hi=0, medbit=0), cmd=b'\x0a\x44', detents=xoCurveEnum)

        lpFreq01 = Dcx(Address(part=0, lo=866, med=868, hi=867, medbit=5), cmd=b'\x05\x45', detents=freqEnum)
        lpFreq02 = Dcx(Address(part=1, lo=35, med=36, hi=37, medbit=6), cmd=b'\x06\x45', detents=freqEnum)
        lpFreq03 = Dcx(Address(part=1, lo=205, med=212, hi=206, medbit=0), cmd=b'\x07\x45', detents=freqEnum)
        lpFreq04 = Dcx(Address(part=1, lo=374, med=380, hi=375, medbit=1), cmd=b'\x08\x45', detents=freqEnum)
        lpFreq05 = Dcx(Address(part=1, lo=543, med=548, hi=544, medbit=2), cmd=b'\x09\x45', detents=freqEnum)
        lpFreq06 = Dcx(Address(part=1, lo=712, med=716, hi=713, medbit=3), cmd=b'\x0a\x45', detents=freqEnum)
    class Limit(Dcx, Enum):
        ## Limiter stuff, probably not used. Put here, just in case...
        sw01 = Dcx(Address(part=0 ,lo=869, med=0, hi=0, medbit=0), cmd=b'\x05\x46', detents=bool)
        sw02 = Dcx(Address(part=1 ,lo=38, med=0, hi=0, medbit=0), cmd=b'\x06\x46', detents=bool)
        sw03 = Dcx(Address(part=1 ,lo=207, med=0, hi=0, medbit=0), cmd=b'\x07\x46', detents=bool)
        sw04 = Dcx(Address(part=1 ,lo=376, med=0, hi=0, medbit=0), cmd=b'\x08\x46', detents=bool)
        sw05 = Dcx(Address(part=1 ,lo=545, med=0, hi=0, medbit=0), cmd=b'\x09\x46', detents=bool)
        sw06 = Dcx(Address(part=1 ,lo=714, med=0, hi=0, medbit=0), cmd=b'\x0a\x46', detents=bool)

        threshold01 = Dcx(Address(part=0 ,lo=871, med=876, hi=0, medbit=2), cmd=b'\x05\x47', detents=limitThresholdScale)
        threshold02 = Dcx(Address(part=1 ,lo=40, med=44, hi=0, medbit=3), cmd=b'\x06\x47', detents=limitThresholdScale)
        threshold03 = Dcx(Address(part=1 ,lo=209, med=212, hi=0, medbit=4), cmd=b'\x07\x47', detents=limitThresholdScale)
        threshold04 = Dcx(Address(part=1 ,lo=378, med=380, hi=0, medbit=5), cmd=b'\x08\x47', detents=limitThresholdScale)
        threshold05 = Dcx(Address(part=1 ,lo=547, med=548, hi=0, medbit=6), cmd=b'\x09\x47', detents=limitThresholdScale)
        threshold06 = Dcx(Address(part=1 ,lo=717, med=724, hi=0, medbit=0), cmd=b'\x0a\x47', detents=limitThresholdScale)

        release01 = Dcx(Address(part=0 ,lo=873, med=876, hi=0, medbit=4), cmd=b'\x05\x48', detents=limitReleaseTimeEnum)
        release02 = Dcx(Address(part=1 ,lo=42, med=44, hi=0, medbit=5), cmd=b'\x06\x48',   detents=limitReleaseTimeEnum)
        release03 = Dcx(Address(part=1 ,lo=211, med=212, hi=0, medbit=6), cmd=b'\x07\x48', detents=limitReleaseTimeEnum)
        release04 = Dcx(Address(part=1 ,lo=381, med=388, hi=0, medbit=0), cmd=b'\x08\x48', detents=limitReleaseTimeEnum)
        release05 = Dcx(Address(part=1 ,lo=550, med=556, hi=0, medbit=1), cmd=b'\x09\x48', detents=limitReleaseTimeEnum)
        release06 = Dcx(Address(part=1 ,lo=719, med=724, hi=0, medbit=2), cmd=b'\x0a\x48', detents=limitReleaseTimeEnum)
    class Align(Dcx, Enum):
        polarity01 = Dcx(Address(part=0, lo=875, med=0, hi=0, medbit=0), cmd=b'\x05\x49', detents=polarityEnum)
        polarity02 = Dcx(Address(part=1, lo=45, med=0, hi=0, medbit=0), cmd=b'\x06\x49', detents=polarityEnum)
        polarity03 = Dcx(Address(part=1, lo=214, med=0, hi=0, medbit=0), cmd=b'\x07\x49', detents=polarityEnum)
        polarity04 = Dcx(Address(part=1, lo=383, med=0, hi=0, medbit=0), cmd=b'\x08\x49', detents=polarityEnum)
        polarity05 = Dcx(Address(part=1, lo=552, med=0, hi=0, medbit=0), cmd=b'\x09\x49', detents=polarityEnum)
        polarity06 = Dcx(Address(part=1, lo=721, med=0, hi=0, medbit=0), cmd=b'\x0a\x49', detents=polarityEnum)

        phase01 = Dcx(Address(part=0, lo=878, med=0, hi=0, medbit=0), cmd=b'\x05\x4a', detents=phaseScale)
        phase02 = Dcx(Address(part=1, lo=47, med=0, hi=0, medbit=0), cmd=b'\x06\x4a', detents=phaseScale)
        phase03 = Dcx(Address(part=1, lo=216, med=0, hi=0, medbit=0), cmd=b'\x07\x4a', detents=phaseScale)
        phase04 = Dcx(Address(part=1, lo=385, med=0, hi=0, medbit=0), cmd=b'\x08\x4a', detents=phaseScale)
        phase05 = Dcx(Address(part=1, lo=554, med=0, hi=0, medbit=0), cmd=b'\x09\x4a', detents=phaseScale)
        phase06 = Dcx(Address(part=1, lo=723, med=0, hi=0, medbit=0), cmd=b'\x0a\x4a', detents=phaseScale)

        delayShort01 = Dcx(Address(part=0, lo=880, med=884, hi=881, medbit=3), cmd=b'\x05\x4b', detents=delayShortScale)
        delayShort02 = Dcx(Address(part=1, lo=49, med=52, hi=50, medbit=4), cmd=b'\x06\x4b', detents=delayShortScale)
        delayShort03 = Dcx(Address(part=1, lo=218, med=220, hi=219, medbit=5), cmd=b'\x07\x4b', detents=delayShortScale)
        delayShort04 = Dcx(Address(part=1, lo=387, med=388, hi=389, medbit=6), cmd=b'\x08\x4b', detents=delayShortScale)
        delayShort05 = Dcx(Address(part=1, lo=557, med=564, hi=558, medbit=0), cmd=b'\x09\x4b', detents=delayShortScale)
        delayShort06 = Dcx(Address(part=1, lo=726, med=732, hi=727, medbit=1), cmd=b'\x0a\x4b', detents=delayShortScale)
    class DelayLong(Dcx, Enum):
        ch1 = Dcx(Address(part=0, lo=153, med=156, hi=154, medbit=4), cmd=b'\x05\x05', detents=int)
        ch2 = Dcx(Address(part=0, lo=295, med=300, hi=296, medbit=2), cmd=b'\x06\x05', detents=int)
        ch3 = Dcx(Address(part=0, lo=437, med=444, hi=438, medbit=0), cmd=b'\x07\x05', detents=int)
        ch4 = Dcx(Address(part=0, lo=578, med=580, hi=579, medbit=5), cmd=b'\x08\x05', detents=int)
        ch5 = Dcx(Address(part=0, lo=720, med=724, hi=721, medbit=3), cmd=b'\x09\x05', detents=int)
        ch6 = Dcx(Address(part=0, lo=889, med=892, hi=890, medbit=4), cmd=b'\x0a\x05', detents=int)
        chA = Dcx(Address(part=1, lo=58, med=60, hi=59, medbit=5), cmd=b'\x01\x05', detents=int)
        chB = Dcx(Address(part=1, lo=227, med=228, hi=229, medbit=6), cmd=b'\x02\x05', detents=int)
        chC = Dcx(Address(part=1, lo=397, med=404, hi=398, medbit=0), cmd=b'\x03\x05', detents=int)
        chS = Dcx(Address(part=1, lo=566, med=572, hi=567, medbit=1), cmd=b'\x04\x05', detents=int)



def comPorts():
    from serial.tools.list_ports import comports
    com_ports_list = list(comports())
    return com_ports_list

port = None
def port_connect():
    global port
    port = serial.Serial('/dev/' + PORT_NAME, baudrate=38400, timeout=0.4, write_timeout=2)
    port.write(DCX_HEAD + DCX_RX_ENABLE + DCX_TAIL)
    return port


if __name__ == "dcx_map":
    pass
    port_connect()

def sync_cache_from_dcx(port=port):
    tries = 0
    freshDumpBuffer=None
    while tries < 5:
        verify=0
        tries +=1
        # print('dcx_map.py.sync_cache_from_dcx(port), tries:', tries)
        port.write(DCX_HEAD + DCX_DUMP_0 + DCX_TAIL)
        time.sleep(0.05)
        port.write(DCX_HEAD + DCX_DUMP_1 + DCX_TAIL)
        dump0 = port.read(1015)
        dump1 = port.read(911)
        if dump0[0:1] == b'\xf0'and dump0[1014:1015] == DCX_TAIL:
            verify += 1
        if dump1[0:1] == b'\xf0' and dump1[910:911] == DCX_TAIL:
            verify += 1
        if verify == 2:
            with open(DUMP_FILE, 'wb+') as f:
                write = f.write(dump0 + dump1)
            freshDumpBuffer = (dump0, dump1)
            break
        time.sleep(0.01)
    return freshDumpBuffer

def _modify_cached_value(control_item, new_val):
    # print('dcx_map:_modify_cached_value(): ', control_item )
    _item = eval('Mapper.' + control_item)
    part, lo_addr, med_addr, hi_addr, med_bit_pos = [ind for ind in _item.address]
    _file = DUMP_FILE
    address_shift = (part * 1015)

    if med_addr == 0:
        with open(_file, "rb+") as fo:
            fo.seek(lo_addr + address_shift)
            fo.write(new_val.to_bytes(1, byteorder='big'))
        return
    else:
        hi = (new_val >> 8)
        with open(_file, "rb+") as fo:
            fo.seek(hi_addr + address_shift)
            fo.write(hi.to_bytes(1, byteorder='big'))

        med = ((new_val) >> 7) - (hi << 1)

        with open(_file, "rb+") as fo:
            fo.seek(med_addr + address_shift)
            old = fo.read(1)
        old_int = int.from_bytes(old, byteorder='big')
        if med == 0:
            new = (old_int & ~(1 << med_bit_pos)).to_bytes(1, byteorder='big')
        else:
            new = (old_int | (1 << med_bit_pos)).to_bytes(1, byteorder='big')
        with open(_file, "rb+") as fo:
            fo.seek(med_addr + address_shift)
            fo.write(new)

        low = (new_val - ((128*med)+(256*hi)))
        with open(_file, "rb+") as fo:
            fo.seek(lo_addr + address_shift)
            fo.write(low.to_bytes(1, byteorder='big'))

def _get_local_cache():
    with open(DUMP_FILE, 'rb') as f:
        all_data = f.read()
    local_cache = (all_data)
    return local_cache

def _get_cached_value(control_item):
    # print("_get_cached_value")
    ''' control_item examples: Eq1.gainA , Gain.ChB, ChNames.ch03 , etc. returns tuple: (int(raw value), contextialy appropriate value) '''
    part, lo_addr, med_addr, hi_addr, med_bit_pos = [ind for ind in control_item.address]
    local_cache = _get_local_cache()
    l_val = local_cache[lo_addr + (part * 1015)]
    if med_addr > 0:
        m_byt = local_cache[med_addr + (part * 1015)]
        med_val = ((m_byt >> med_bit_pos) & 1) * 128
        h_val = local_cache[hi_addr + (part * 1015)] * 256
    else:
        med_val = 0
        h_val = 0
    val = l_val + med_val + h_val
    # print("_get_cached_value: ", control_item, ': ', val, ', ', control_item.detents(val))
    return val, control_item.detents(val)

def get_setting(control_item):
    '''call cached dcx value by string (or possibly object), ie: get_setting('Eq1.freq01') , returns int representation of value or index.
    '''
    try:
        control_item = control_item.replace('_', '.')
        if control_item[-2:-1] == '.':
            control_item = control_item[:-2]
        if 'Eq' and 'curve' in control_item:
            val = get_eq_curve(control_item)
            return val
        _item = eval('Mapper.' + control_item)
        val = _get_cached_value(_item)
    except:
        try:
            val = _get_cached_value(control_item)
        except:
            return None
    return val

def _sevenbit(int_val):
    lo = (int_val - (int(int_val/128) * 128)).to_bytes(1, byteorder='big', signed=True)
    hi = int(int_val/128).to_bytes(1, byteorder='big', signed=True)
    out = hi + lo
    return out

def set_setting(control_item, value):
    '''call dcx by string like this, ie: set_setting('Eq1.freq1', value) '''
    if 'Gain' in control_item or 'gain' in control_item:
        if(value > 15.0):value = 15
        if(value < -15.0):value = -15
        value = int( (value+15)*10 )
        #print('\ndcx_map_987: val: ', value, ' typ:', str(type(value)), ' ', control_item)
    #elif 'gain' in control_item:
        #value = int( (value+15)*10 )
    elif 'Eq' and 'Q' in control_item:
        value = int(value)
    else:
        value = int(value)
        pass
    
    if comlink_write_enabled:
        control_item = control_item.replace('_', '.')
        if control_item[-2:-1] == '.':
            control_item = control_item[:-2]
        if 'Eq' and 'curve' in control_item:
            _set_eq_curve(control_item, value)
        else:
            _modify_cached_value(control_item, value)
            try:
                _item = eval('Mapper.' + control_item)
            except:
                print('exception(info)  dcx_map.set_setting(', control_item, ')')
                return None
            command =  _item.cmd + _sevenbit(value)
            try:
                port.write(DCX_HEAD + DCX_RX_ENABLE + DCX_TAIL)
                port.write(DCX_HEAD + DCX_ADJUST + command + DCX_TAIL)
            except:
                print('dcx_map.set_setting : port.write error')
    else:
        pass
        # print('dcx_map.set_setting : comlink_write_enabled = False')

def set_settings(*control_val_pairs):
    '''call dcx by string like this, ie: set_settings(['Eq1.freq1', 34], ['Eq1.freq01', value]) '''
    if comlink_write_enabled:
        num_of_commands = len(control_val_pairs).to_bytes(1, byteorder='big')
        commands = b'\x20' + num_of_commands
        try:
            for pair in (control_val_pairs):
                _item = eval('Mapper.' + pair[0])
                commands += _item.cmd + _sevenbit(pair[1])
                _modify_cached_value(pair[0], pair[1])
            port.write(DCX_HEAD + DCX_RX_ENABLE + DCX_TAIL)
            port.write(DCX_HEAD + commands + DCX_TAIL)
        except:
            print('dcx_map.set_settings : port.write err:', control_val_pairs)
    else:
        pass
        # print('dcx_map.set_settings : comlink_write_enabled = False')

def _set_eq_curve(control_item, value):
    # Consolidates setting Eq[n].type[chan], and Eq[n].slope[chan], into one control.
    band = control_item[2:3]
    channel = control_item[-1:]
    if value == 0: # Bandpass
        _type = 'Eq' + band + '.type' + channel
        set_settings([_type, 1])
    else:
        if value == 1: # Lowpass 6dboct
            _type = ['Eq' + band + '.type' + channel, 0]
            _slope = ['Eq' + band + '.slope' + channel, 0]
        elif value == 2: # Lowpass 12dboct
            _type = ['Eq' + band + '.type' + channel, 0]
            _slope = ['Eq' + band + '.slope' + channel, 1]
        elif value == 3: # Lowpass 6dboct
            _type = ['Eq' + band + '.type' + channel, 2]
            _slope = ['Eq' + band + '.slope' + channel, 0]
        elif value == 4: # Lowpass 12dboct
            _type = ['Eq' + band + '.type' + channel, 2]
            _slope = ['Eq' + band + '.slope' + channel, 1]
        set_settings(_type, _slope)

def get_eq_curve(control_item):
    band = control_item[2:3]
    channel = control_item[-1:]
    _type = get_setting(eval('Mapper.' + 'Eq' + band + '.type' + channel))[0]
    _slope = get_setting(eval('Mapper.' + 'Eq' + band + '.slope' + channel))[0]
    if _type == 1: # Bandpass
        val = (0, )
    else:
        val = (1 + _type + _slope, )
    return val

def get_live_levels():
    DCX_MSG = b'\x50\x00\x00\x00'
    port.write(DCX_HEAD + DCX_RTX_ENABLE + DCX_TAIL)
    port.write(DCX_HEAD + DCX_PING  + DCX_TAIL)
    time.sleep(0.05)
    recvd = port.read_until(b'\x0E')
    recvd = port.read_until(b'\x10')
    levels = port.read(9)
    if len(levels) == 9:
        return levels

    else:
        return None

def set_rts_line(state=None):
    if state != None:
        port.rts = state
        print('set_rts_line:' , port.rts)
    else:
        print('set_rts_line:, Nothing to do...')

def set_dtr_line(state=None):
    if state != None:
        port.dtr = state
        print('set_dtr_line:' , port.dtr)
    else:
        print('set_dtr_line:, Nothing to do...')

def pull_setting(control_item, saved_cache):
    '''(from file(s)), call cached dcx value by string (or possibly object), ie: pull_setting('Eq1.freq01') , returns int representation of value or index.
    '''
    try:
        _item = eval('Mapper.' + control_item)
        part, lo_addr, med_addr, hi_addr, med_bit_pos = [ind for ind in _item.address]
        address_shift = (part * 1015)
        l_val = saved_cache[lo_addr + address_shift]
        if med_addr > 0:
            m_byt = saved_cache[med_addr + address_shift]
            med_val = ((m_byt >> med_bit_pos) & 1) * 128
            h_val = saved_cache[hi_addr + address_shift] * 256
        else:
            med_val = 0
            h_val = 0
        val = l_val + med_val + h_val

    except:
        return None
    return val, _item.detents(val)

def push_setting(control_item, value):
    '''(To DCX) call dcx by string like this, ie: set_setting('Eq1.freq1', value) '''

    if comlink_write_enabled:
        try:
            _item = eval('Mapper.' + control_item)
        except:
            print('exception(info)  dcx_map.set_setting(', control_item, ')')
            return None
        command =  _item.cmd + _sevenbit(value)
        # print("comand:", command)
        try:
            port.write(DCX_HEAD + DCX_ADJUST + command + DCX_TAIL)
        except:
            print('dcx_map.set_setting : port.write error')
    else:
        print('dcx_map.set_setting : comlink_write_enabled = False')

def transmit_set(basename='dcx_dump'):
    with open(basename, 'rb') as f:
        all_data = f.read()
        saved_cache = (all_data)

    port.write(DCX_HEAD + DCX_RX_ENABLE + DCX_TAIL)

    loading_order = [
        'Setup',
        'Gain',
        'Mute',
        'EqSwitch',
        'EqIndex',
        'EqNumber',
        'Eq1','Eq2','Eq3','Eq4','Eq5','Eq6','Eq7','Eq8','Eq9',
        'Crossover','Align',
        'Sources',
        'ChNames'
        ]

    for  st in loading_order:
        enums = [enum for enum in dir(Mapper) if (enum.startswith(st)) ]
        for item in enums:
            classname = getattr(Mapper, item)
            for name, member in classname.__members__.items():
                value = pull_setting(str(member), saved_cache) # (from file)
                # print(str(member), ' : ', value )
                push_setting(str(member), value[0]) # (to DCX)
                time.sleep(0.008)
    print("Transmission: DONE")




if __name__ == "__main__":
    ## Temporary Test tools follow:     #########################################################
    port = serial.Serial("/dev/ttyUSB0", baudrate=38400, timeout=0.4, write_timeout=2)

    def sync_cache_from_dcx(port=port):
        tries = 0
        freshDumpBuffer=None
        while tries < 5:
            verify=0
            tries +=1
            print('dcx_map.py.sync_cache_from_dcx(port), tries:', tries)
            port.write(DCX_HEAD + DCX_DUMP_0 + DCX_TAIL)
            time.sleep(0.05)
            port.write(DCX_HEAD + DCX_DUMP_1 + DCX_TAIL)
            dump0 = port.read(1015)
            dump1 = port.read(911)
            if dump0[0:1] == b'\xf0'and dump0[1014:1015] == DCX_TAIL:
                with open(DUMP_0_FILE, 'wb+') as f:
                    write = f.write(dump0)
                    verify += 1
            if dump1[0:1] == b'\xf0' and dump1[910:911] == DCX_TAIL:
                with open(DUMP_1_FILE, 'wb+') as f:
                    write = f.write(dump1)
                    verify += 1
            if verify == 2:
                freshDumpBuffer = (dump0, dump1)
                print('Buffer filled')
                break
        return freshDumpBuffer

    def get_control(item_str, control_str):
        objekt = getattr(dcx_map, item_str)
        func = getattr(objekt, control_str)
        print('name:', control_str,'  cmd:',func.cmd, '  address:', func.address)
        return func

    def text_to_file(text, filename):
        with open(filename, 'w+') as f:
            write = f.write(text)

    def read_byte_file(filename):
        with open(filename, 'rb') as f:
            read = f.read()
        return read

    def parse_to_hex(byte_data):
            rcvd = byte_data.hex()
            hex_text = ' '.join(rcvd[i:i+2] for i in range(0, len(rcvd), 2))
            return hex_text

    def map_tests(classname):
        for name, member in classname.__members__.items():
            print('Map test:', name,';',member, member.cmd)
        #x =[c.name for c in Eq1]
        #print((x[0]))
        #command = EqNumber.ch01.cmd + b'\x00\x04'
        #port.write(DCX_HEAD + DCX_RX_ENABLE + DCX_TAIL)
        #port.write(DCX_HEAD + DCX_ADJUST + command + DCX_TAIL)
    #map_tests(dcx_map.Mapper.Gain)

    def ping_test(port):
        DCX_MSG = b'\x50\x00\x00\x00'

        port.write(DCX_HEAD + DCX_RTX_ENABLE + DCX_TAIL)
        #port.write(DCX_HEAD + DCX_PING  + DCX_TAIL)
        time.sleep(0.05)
        #recvd = port.read(13)
        recvd = port.read_until(b'\x0E')
        recvd = port.read(2)
        recvd2 = parseport.read_until(10)
        print('Ch3:', str(recvd2))
    #port = serial.Serial("/dev/ttyUSB0", baudrate=38400, timeout=0.4, write_timeout=2)
    #for x in range(0, 6):
        #ping_test(port)
        #time.sleep(0.4)

    def invert_mapper():
        ''' Returns Dict, where you recieve callsign from binary command.
            (Instead of vice-versa).
        '''
        reppam={}
        enums = [enum for enum in dir(Mapper) if enum.startswith('__') is False]
        for item in enums:
            classname = getattr(Mapper, item)
            for name, member in classname.__members__.items():
                reppam[member.cmd] = member
                print('invert_mapper:', str(member))
        return reppam

    # control = invert_mapper()
    # print('invert_mapper:', str(control))
    # print('invert_mapper:', str(control[b'\x05\x02']))
    # enums = [enum for enum in dir(Mapper) if enum.startswith('__') is False]
    # enums = [enum for enum in dir(Mapper) if enum.startswith('__') is False]
    # print(enums)
    # print(type(enums[0]))



    def search_test():
        #{0xF0, 0x00, 0x20, 0x32, 0x20, 0x0E, 0x40, TERMINATOR}
        DCX_SEARCH = b'\xF0\x00\x20\x32\x20\x0E\x40\xf7'
        port.write(DCX_HEAD + DCX_TX_ENABLE + DCX_TAIL)
        port.write(DCX_SEARCH + DCX_TAIL)
        #time.sleep(0.05)
        #recvd = port.read_until(b'\xf7')
        start = port.read(4) # skip to meat.
        device_id_num = port.read(1)
        end = port.read_until(b'\xf7')

        print('search_test[start]:', parse_to_hex(start))
        print('search_test [dev.]:', parse_to_hex(device_id_num))
        print('search_test  [end]:', parse_to_hex(end))
    port = serial.Serial("/dev/ttyUSB0", baudrate=38400, timeout=0.4, write_timeout=2)
    # search_test()
    
    
    def list_com_ports():
        from serial.tools.list_ports import comports
        com_ports_list = list(comports())
        for port in com_ports_list:
            name = port.name
            print('ports:', name)
    #list_com_ports()
    
    def multi_set_test():
        # 0xF0, 0x00, 0x20, 0x32, 0x20, 0x0E, 0x40, 0xf7
        print("Bonghus")
        DCX_ADJ = b'\x20\x10'
        DCX_TEST = b'\x50\x01\x01\x00'
        T = b'\x01\x03\x00\x01\x02\x03\x00\x01\x03\x03\x00\x01\x04\x03\x00\x01\x05\x03\x00\x01\x06\x03\x00\x01\x07\x03\x00\x01\x08\x03\x00\x01'
        T0 = b'\x01\x03\x00\x00\x02\x03\x00\x00\x03\x03\x00\x00\x04\x03\x00\x00\x05\x03\x00\x00\x06\x03\x00\x00\x07\x03\x00\x00\x08\x03\x00\x00'
        T1 = b'\x01\x03\x00\x01'
        T2 = b'\x02\x03\x00\x01'
        port.write(DCX_HEAD + DCX_RX_ENABLE + DCX_TAIL)
        port.write(DCX_HEAD + DCX_ADJ + T0 + T + DCX_TAIL)
    # multi_set_test()


    def _get_saved_value(control_item, saved_cache):
        ''' control_item examples: Eq1.gainA , Gain.ChB, ChNames.ch03 , etc. returns tuple: (int(raw value), contextually appropriate value) '''
        part, lo_addr, med_addr, hi_addr, med_bit_pos = [ind for ind in control_item.address]
        l_val = saved_cache[part][lo_addr]
        if med_addr > 0:
            m_byt = saved_cache[part][med_addr]
            med_val = ((m_byt >> med_bit_pos) & 1) * 128
            h_val = saved_cache[part][hi_addr] * 256
        else:
            med_val = 0
            h_val = 0
        val = l_val + med_val + h_val
        return val, control_item.detents(val)


    def pull_setting(control_item, saved_cache):
        '''(from file(s)), call cached dcx value by string (or possibly object), ie: pull_setting('Eq1.freq01') , returns int representation of value or index.
        '''
        try:
            _item = eval('Mapper.' + control_item)
            part, lo_addr, med_addr, hi_addr, med_bit_pos = [ind for ind in _item.address]
            l_val = saved_cache[part][lo_addr]
            if med_addr > 0:
                m_byt = saved_cache[part][med_addr]
                med_val = ((m_byt >> med_bit_pos) & 1) * 128
                h_val = saved_cache[part][hi_addr] * 256
            else:
                med_val = 0
                h_val = 0
            val = l_val + med_val + h_val

        except:
            return None
        return val, _item.detents(val)

    def push_setting(control_item, value):
        '''(To DCX) call dcx by string like this, ie: set_setting('Eq1.freq1', value) '''

        if comlink_write_enabled:
            try:
                _item = eval('Mapper.' + control_item)
            except:
                print('exception(info)  dcx_map.set_setting(', control_item, ')')
                return None
            command =  _item.cmd + _sevenbit(value)
            # print("comand:", command)
            try:
                port.write(DCX_HEAD + DCX_ADJUST + command + DCX_TAIL)
            except:
                print('dcx_map.set_setting : port.write error')
        else:
            print('dcx_map.set_setting : comlink_write_enabled = False')
    # push_setting('Mute.chA', int(0))

    def transmit_set(basename='dumpwatch'):
        with open(basename+'_0', 'rb') as f:
            read0 = f.read()
        with open(basename+'_1', 'rb') as f:
            read1 = f.read()
            saved_cache = (read0, read1)

        port.write(DCX_HEAD + DCX_RX_ENABLE + DCX_TAIL)

        loading_order = [
            'Setup',
            'Gain',
            'Mute',
            'EqSwitch',
            'EqIndex',
            'EqNumber',
            'Eq1','Eq2','Eq3','Eq4','Eq5','Eq6','Eq7','Eq8','Eq9',
            'Crossover','Align',
            'Sources',
            'ChNames'
            ]

        for  st in loading_order:
            enums = [enum for enum in dir(Mapper) if (enum.startswith(st)) ]
            for item in enums:
                classname = getattr(Mapper, item)
                for name, member in classname.__members__.items():
                    # if ('slope') not in str(member):
                    value = pull_setting(str(member), saved_cache) # (from file)
                    # print(str(member), ' : ', value )
                    push_setting(str(member), value[0]) # (to DCX)
                    time.sleep(0.008)



    # sync_cache_from_dcx()
    # transmit_set('Saved_binary/FLAT_')
    # transmit_set()

    # push_setting('Gain.chA', 50)
    # test = get_setting('Eq8.freq6')
    # test = Mapper.Eq8.freq6.detents(43)
    # test = Mapper.Eq8.freq6.value
    # print(">> ", test)

''' 
Outputs from DCX follow... (for decoding / refernence only)

search_test: b'\xf0\x00 2\x00\x0e\x00\x01\x11DCX2496         \xf7'
search_test: b'\xf0\x00 2\x01\x0e\x00\x01\x11DCX2496         \xf7'
search_test: b'\xf0\x00 2\x02\x0e\x00\x01\x11DCX2496         \xf7'

#   "Ping" gets a readout of signal levels according to this lot:
All channels. Signal = 0db:
ping_test: b'\xf0\x00 2\x00\x0e\x04\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$\x00\x00\xf7'
ping_test: b'\xf0\x00 2\x00\x0e\x04\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$\x00\x00\xf7'

B+C, 6chs = same, (-20db(approx))
ping_test: b'\xf0\x00 2\x00\x0e\x04\x10\x00\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00$\x00\x00\xf7'
ping_test: b'\xf0\x00 2\x00\x0e\x04\x10\x00\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00$\x00\x00\xf7'

B+C, chs3-6 = same, (-10db(approx)), chs1+2: 0db:
ping_test: b'\xf0\x00 2\x00\x0e\x04\x10\x00\x02\x02\x00\x00\x02\x02\x02\x02\x00\x00\x00\x00$\x00\x00\xf7'
ping_test: b'\xf0\x00 2\x00\x0e\x04\x10\x00\x02\x02\x00\x00\x02\x02\x02\x02\x00\x00\x00\x00$\x00\x00\xf7'
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ChA\ChB\ChC\Ch1\Ch2\Ch3\Ch4\Ch5\Ch6\
These values = no of led db indicators lit.

########
transmitted from DCX on adjusting :
Gain:
ChA: b'\xf0\x00 2\x00\x0e \x01\x01\x02\x01\x18\xf7'
ChA: b'\xf0\x00 2\x00\x0e \x01\x01\x02\x01\x19\xf7'
ChB: b'\xf0\x00 2\x00\x0e \x01\x02\x02\x02\x13\xf7'
ChB: b'\xf0\x00 2\x00\x0e \x01\x02\x02\x02\x1b\xf7'
ChC: b'\xf0\x00 2\x00\x0e \x01\x03\x02\x01\x08\xf7'
ChC: b'\xf0\x00 2\x00\x0e \x01\x03\x02\x01\x0b\xf7'
ChSum?:\\\\\\\\\\\\\\\\\\\\\\\\x04\ Guessing!
Ch1: b'\xf0\x00 2\x00\x0e \x01\x05\x02\x02\x06\xf7'
Ch1: b'\xf0\x00 2\x00\x0e \x01\x05\x02\x02\x0b\xf7'
Ch2: b'\xf0\x00 2\x00\x0e \x01\x06\x02\x01\x17\xf7'
Ch2: b'\xf0\x00 2\x00\x0e \x01\x06\x02\x01\x18\xf7'


head:b'\xf0\x00\x20\x32\x00\x0e'


'''
