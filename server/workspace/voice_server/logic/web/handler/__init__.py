#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-17

@author: Jay
"""
import time
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from lib.recognise import kdxf_msc_voice2text, kdxf_msc_text2voice, tuling_ai
from setting import AI_DEFAULT_ANSWER


@route(r'/audio_ai')
class AudioAIHandler(HttpRpcHandler):
    @web_adaptor(use_json_dumps=False)
    def post(self):
        # 语音识别
        s_vop_voice2text_time = time.time()
        logger.debug('AudioAIHandler::AudioAIHandler body_len:%s' % (len(self.request.body)))
        recognise_text = kdxf_msc_voice2text(self.request.body)
        e_vop_voice2text_time = time.time()
        logger.debug('AudioAIHandler::AudioAIHandler voice2text use time=%s' % (e_vop_voice2text_time - s_vop_voice2text_time))
        logger.debug('AudioAIHandler::AudioAIHandler recognise_text=%r' % recognise_text)

        # 语音AI
        s_tuling_ai_time = time.time()
        ai_text = tuling_ai(recognise_text) if recognise_text else AI_DEFAULT_ANSWER
        e_tuling_ai_time = time.time()
        logger.debug('AudioAIHandler::AudioAIHandler tuling_ai use time=%s' % (e_tuling_ai_time - s_tuling_ai_time))
        logger.debug('AudioAIHandler::AudioAIHandler ai_text=%r' % ai_text)

        # 文本转语音
        s_vop_text2voice_time = time.time()
        media_file, ai_voice_data = kdxf_msc_text2voice(ai_text)
        e_vop_text2voice_time = time.time()
        logger.debug('AudioAIHandler::AudioAIHandler baidu_vop_text2voice use time=%s, voice_data_length:%s' % (e_vop_text2voice_time - s_vop_text2voice_time, len(ai_voice_data)))

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Length', len(ai_voice_data))
        self.set_header('Content-Disposition', 'attachment; filename=%s' % media_file)
        return ai_voice_data
