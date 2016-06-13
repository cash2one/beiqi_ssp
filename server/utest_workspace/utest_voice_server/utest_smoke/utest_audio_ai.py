#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/20

@author: Jay
"""
from utest_lib.common import *
from interfaces.voice_server.http_rpc import audio_ai
from utest_lib.service import VoiceSvrHttpRpcClt


class VoiceAudioAITest(unittest.TestCase):
    def test_audio_ai(self):
        wav_file= "iflytek02.wav"
        wav_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), wav_file)

        file_object = open(wav_file, 'rb')
        file_data = file_object.read()

        stime = time.time()
        resp = audio_ai(VoiceSvrHttpRpcClt, file_data)
        print len(resp)

        etime = time.time()
        print "diff time:%s" % (etime - stime)