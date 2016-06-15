#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/15

@author: Jay
"""
from utest_lib.common import *
from interfaces.dev_server.http_rpc import loc_v1
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET


class APILocTest(unittest.TestCase):
    def test_loc_up_lov_v(self):
        add_device_res = loc_v1(SERVER_IP, gen_test_tk(), APP_SECRET, sn=TEST_SN, payload='{"ts":1465960992,"loc":"{\\"latitude\\":24.480782,\\"longitude\\":118.178511,\\"altitude\\":0,\\"country\\":\\"\xe4\xb8\xad\xe5\x9b\xbd\\",\\"province\\":\\"\xe7\xa6\x8f\xe5\xbb\xba\xe7\x9c\x81\\",\\"city\\":\\"\xe5\x8e\xa6\xe9\x97\xa8\xe5\xb8\x82\\",\\"district\\":\\"\xe6\x80\x9d\xe6\x98\x8e\xe5\x8c\xba\\",\\"road\\":\\"\xe5\x89\x8d\xe5\x9f\x94\xe4\xb8\x9c\xe8\xb7\xaf\\",\\"ad_code\\":\\"350203\\",\\"address\\":\\"\xe7\xa6\x8f\xe5\xbb\xba\xe7\x9c\x81\xe5\x8e\xa6\xe9\x97\xa8\xe5\xb8\x82\xe6\x80\x9d\xe6\x98\x8e\xe5\x8c\xba\xe5\x89\x8d\xe5\x9f\x94\xe4\xb8\x9c\xe8\xb7\xaf\xe9\x9d\xa0\xe8\xbf\x91\xe7\xa6\x8f\xe5\x85\x89\xe5\xa4\xa7\xe5\x8e\xa6\\",\\"loc_type\\":5,\\"provider\\":\\"lbs\\",\\"accuracy\\":55}","soft_version":"5.0","battery":96,"charge":0}')
        self.assertTrue(add_device_res['state'] == 0)