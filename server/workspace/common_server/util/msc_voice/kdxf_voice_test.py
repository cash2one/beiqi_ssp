# coding:utf-8
#!/usr/bin/python
import time
from ctypes import *
import os
libiat = cdll.LoadLibrary('./libkdxf_voice.so')
libiat.voice_2_text.restype = c_char_p
libiat.voice_2_text.argtypes=[c_char_p, c_long, c_int]
libiat.text_2_voice.restype = c_int
libiat.text_2_voice.argtypes=[c_char_p, c_char_p]
libiat.msp_login.restype = c_int

ret = libiat.msp_login()
assert ret == 0

wav_file = "iflytek02.wav"

s1time = time.time()
file_data = open(wav_file, 'rb').read()
print len(file_data)
e1time = time.time()
print "use file time:",e1time - s1time

for i in xrange(10):
    stime = time.time()
    iat_str = libiat.voice_2_text(c_char_p(file_data), c_long(len(file_data)), c_int(0))
    print "iat_str,",iat_str
    etime = time.time()
    print "voice_2_text use time:",etime - stime

text = "测试"
file="%s.wav"%(time.time())

for i in xrange(10):
    stime = time.time()
    libiat.text_2_voice(c_char_p(text), c_char_p(file))
    etime = time.time()
    print "text_2_voice use time:",etime - stime

stime = time.time()
file_data = open(file).read()
etime = time.time()
print "get file use time:",etime - stime

stime = time.time()
os.remove(file)
etime = time.time()
print "remove file use time:",etime - stime

#ret = libiat.msp_logout()
