#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-18

@author: Jay
"""
from lib.common import *
from utils.crypto import XXTEACrypto, UrlCrypto
from utils.crypto import xxtea


class SignTest(unittest.TestCase):

    @unittest_adaptor()
    def test_checksign(self):
        server_name = "server1"

        signed_data = sign(server_name)
        self.assertTrue(checksign(signed_data, server_name))
        self.assertFalse(checksign(signed_data, "server11"))
        self.assertFalse(checksign(signed_data, "server"))

    @unittest_adaptor()
    def test_checksign_dict(self):
        dic = {"server": 1,
               "test": [2,3]}

        dic2 = {"test": [2,3],
                "server": 1}

        signed_data = sign(str(dic))
        self.assertTrue(checksign(signed_data, str(dic2)))

    @unittest_adaptor()
    def test_check_signer(self):
        kwargs1 = {'service_type': 'bridge', 'ip': '10.24.6.170'}
        signed_data = Signer().gen_sign(**kwargs1)
        kwargs2 = {'ip': '10.24.6.170','service_type': 'bridge'}
        self.assertTrue(Signer().check_sign(signed_data, **kwargs2))
        kwargs3 = {u'service_type': u'bridge', u'ip': u'10.24.6.170'}
        self.assertTrue(Signer().check_sign(signed_data, **kwargs3))
        kwargs3 = {u'service_type': u'bridge1', u'ip': u'10.24.6.170'}
        self.assertFalse(Signer().check_sign(signed_data, **kwargs3))

    @unittest_adaptor()
    def test_check_signer_dic_list(self):
        params = {"service_type": "register",
                  "rdm_type": RT_HASH_RING,
                  "rdm_param": ["aaaaaaaaaaa"]}
        signed_data = Signer().gen_sign(**params)
        self.assertTrue(Signer().check_sign(signed_data, **params))

class XXTEACryptoTest(unittest.TestCase):
    x = XXTEACrypto("A~3c0(@8$B65Wb<9")

    def test_encode_decode_normal(self):
        url = "https://10.15.2.111:55952/gllive:sa/authenticate?password=123456"
        self.assertTrue(self.x.decrypt(self.x.encrypt(url)) == url)

    def test_encode_decode_abnormal(self):
        url = "https://10.15.2.111:55952/gllive:sa/authenticate?password=123456"
        self.assertFalse(self.x.decrypt(self.x.encrypt(url)) == url + "1234")

    def test_print(self):
        print self.x.encrypt("login?user_name=device1&password=123456&type=2")
        print self.x.encrypt("register")
        print self.x.decrypt("pN%2A%2AT-ScQlwUnP%2AX5jsobyiXtAXReyfcNVBjbdbR%2A5eecG2uX8FPZOJzMX%2A2K5FwCa%2ATV9lQv13zE30%2Apaix3uRr6w4MiT-Q8k9x%2A6Jc17d%2AendvOLA7sJ2VKYkhU1d2fSs-5LWCsemm2hOzrQOSlmzYqupxRUwm9pplOdmxWM-W%2A3CYmGkbpSNSbbuTX%2AiMkbWvrT2M%2ALbW7qOLHaKtLMxG4LoftySOvPgUk1H5zWVgKyVfXOD8YD%2ATRG%2AG7zup54t5CFKq5IdWfk4dSWTZs1eIt9SZwo-QT3fHcYMScIapre6hyQ-cIiZ%2A3GOHmjbuoOJzBo1jS9lmPUxzW2UyfO-ZgaCchHQUTvFmHKGj5KeiulyrEIF-oKITyvuqgi0S0uSVGdAuAEXIO4OD-H2%2A-yjPzH23IJ5RfM5BVEVBD7RDa8u2ODGp1gwgTnP317cA9Qh4RupERoaDbfu03YKqwqqhF5YnqhRbd51Z1yYan-aLhJzPlESR0hy5pG6k3SW6V%2AeRwtIyoC3japcSkEasV3H8Gj28eDjF%2AvHLaHshvJZ5cOrWAPOvv8kS1leFIZ0ve-fth2lGVyF-fh3vcTnSjYDU8DBLs9IaTChGugcQNq8Ai%2AWHZZ-nA%2ACFtsBJ-ZEoSnMroXtLeuzJdVJPpwkCXAZRrmmyg7OcubyEzyzBvABIIvndStl3Q3HHU%2Aj4Dx5wZUCD3AbYhBlGjTqDHf7kbQ%3D%3D")
        print self.x.encrypt("login")
        print self.x.encrypt("user_name=device1&password=123456&type=2")
        print self.x.decrypt("dHi5OIy2aq9ozRIbA-QeKjsmntVSL7ny3kYg7eY%252A%252A8pA9Y-0VXjSqzvcbasN44AE5P5FpF3IQlZQh2hzwboQzOqGqy-N9GUfiuIBue062dikJXbKPSI9L-pmUn-0KjDC-Sj6xsBDdClg0GDZ1ESwX0kIyGdfvSb7ulSI9zTyejltpZKDGM3qN-JdDldUMsD5k3wQOLAXCMcyx-sn2SKiSAZ7iFhxsUGsUnCT1SxKcp4EdBds%252A067CtBoo4oB9DzSbM1QaqU38kn5S0q7SKBHrrcOKCVovhh-3isbp6CZ-8fW6XEuy2dYN1HSIRC%252A3vbc8ktaQHvaKYG4pKLig9FBi7wVwugx%252AIKLY-fV11UW82a7iUYvU1rsF2SSLy0GAAHWb43VT-ZmkbCWBBvJmABj0hAlANM%252At20HOS338R-oNO%252A1UFgmMlXhXcyIdorvTM2ZFDpoVslWe5twm86EX41-1bBAda0pX8xMKLH73HgiQvXQSq8qpOW9bBPX2kaAp3t8D1euWE99E74SHF33S%252AYzJ7fw3k%252A-AB2aqbZJ5l5UK9nryBFmDbhwjDoT7vv5aLjXCtJm9ewd0o5rk07nmzkScFjUEXwv%252Ao8C%252A5kDV0AzupTx4bDga9%252AdGqq6pT1dVhpHtDqMtKHZaDuAZ9QbPWKP7EDDUtj0RL-VABGzj9hY5zBNEF0Vyj46YmRN1eyelpd6FaRd12lQEV%252ASz5jRKYD%252AoA%253D%253D")
        print self.x.decrypt("odk73pmdUDtAR-ZNA4-m2nlm06xTkBF9IOmmZF9O0LTa5WsraGuLgM1FmTOgkBzJZ5gxgnl8cz2zcYQ7-mNK35ncsLeFiFCoFkJHrTR47xacvvyx-ve%2AYSbOlA0tTNvrvmXwUMHWGp8XMWtouobQQnCPUWFDRNEavgzXMDu-mwr9o3GMu%2AVRVUvVIcflUZo0AHXXw-Sq1DfVviueej2rNZmdcZk5zJevLy8SA5I3QAPz-hNdPSnERHeYBqD2hzEiOdLLQ5O9Ow2O9tDlaadr%2A64Gm3n6kvDz0uruDTDmruBgoeIEUIjYEP%2A6uhiRnHVV5al4FCQIRnaPJqQCxtxNZ3WQLyOTsTHMeldPs-WH37GJS8w49ZZIS5pJGv7EUFXcO47uCqPf06n7sQ1iJrxT0cTJFQickoF8cmGJuq7XLovHKivMWS1K4Ivls5RJ2XDEU32pGsY5h-dkBgJYmr-n-n6Le6pT7%2Awwahc5bu4tN0rsr8iX-68K9287wvkqVECeFiMqBJhg1oFHw83Ymf9vM5gj-D4PlbuSnQk5SUY9D35DYPmikREqhSd-WKwg5b%2AI4xoPNpueAUH51FejZSl1RGOujmjtdYV3YE9tRmFrlffFosGkJiNPovJPAKakPCdyle1FaU1S1-F7CGexhpkS9LOWOo5SudT9-%2AbmenY9qyWl%2ATt%2AqdhhBQjVzABH%2AtjQce7h3pST1YPuJyOxhxBgKA%3D%3D")
        print self.x.encrypt("user_name=詹陈锦&password=123456&type=2")
        print self.x.decrypt("jN%2AIvgD6hK1EJSOfxop9vfjDzzHwnqH1pqbvuJVYEBLx19i37zpPMscklHDgVDe6v1eolzdAH0hWYURJgDhah%2AWJ0fHFMrsj70Wdl5g8Rs31RVq0x2MlQUW%2A8ho--XAWuwTe1DI5F6YdpJkNTeI2DjbXy1b%2AICGai08D6sHWIl95CjoQQbOD0lwnG38h6nF8SLECJoQ2VLoryhFQ8uIL8D-xCT2RdW1rAWpJSTbU%2A-58yYWPOuiPiSe9jDe4j7GQNLEOaX1ttridZsYThW2Pfti1L-BBbPT1wdiw0f0NDTDvz2xykal1fAhatfkj%2AKRgA6iQCVE44UBoJk9ytXgy6io2luazePOIqoQxKJqdbOjXXdH2kQyYh9wXpJxLNTeWO8P1T%2AnKer4W%2AsfVHDUFh7yQ9DbQGwBqFRxzufykojVHP2Hw3elFRF1yznJHCnrZ0ohd1nNWNDxxyPsoubTCM9L3nOD5d8p-jquUTwgCdD-ReJ3q1v6U5oGBw3P7hEUnysatzdsYdTNu3sSWLDZ75tpb6wZnuQsfxFD7HWalJrfWZDffe%2AoGgsTjEePVdYjk8%2AAw3H1WpeNYUm7r19uDvXYaDcx67E1atd9DZjhwK6zDf5rvmagl1lqtpUnUXoFrFdjc4fSk%2AB%2AbMwiUeVFaYwsAWKazs91MZvqlj1rSOIA-d1oJ8oNEd14DomMrwQ84u97UZUn6vENE1nGn")


class UrlCryptoTest(unittest.TestCase):
    u = UrlCrypto()

    def test_encode_decode_normal(self):
        url = "https://10.15.2.111:55952/gllive:sa/authenticate?password=123456"
        self.assertTrue(self.u.decrypt(self.u.encrypt(url)) == url)

    def test_encode_decode_abnormal(self):
        url = "https://10.15.2.111:55952/gllive:sa/authenticate?password=123456"
        self.assertFalse(self.u.decrypt(self.u.encrypt(url)) == url + "1234")

class XXTEATest(unittest.TestCase):
    def setUp(self):
        self.x = xxtea.XXTEA("A~3c0(@8$B65Wb<9")
        self.url = "/authorize?client_id=148%3A50718%3Av0.0.1%3Aios&username=sa&password=123&credential_type=gllive&scope=auth"

    def test_init(self):
        x = xxtea.XXTEA("A~3c0(@8$B65Wb<9")
        self.assertEqual(len(x.key) % 4, 0)

    def test_init_invalid_key(self):
        key = "A~3c0(@8$"
        self.assertRaises(xxtea.XXTEAException, xxtea.XXTEA, key)
        key = (1, 2, 3, 4, 5, 6, 7, 8, 9, 0)
        self.assertRaises(xxtea.XXTEAException, xxtea.XXTEA, key)

    def test_encrypt_decrypt_normal(self):
        enUrl = self.x.encrypt(self.url)
        deUrl = self.x.decrypt(enUrl)
        self.assertEqual(deUrl, self.url)

    def test_encrypt_decrypt_abnormal(self):
        enUrl = self.x.encrypt(self.url)
        deUrl = self.x.decrypt(enUrl + "AAA")
        self.assertNotEqual(deUrl, self.url)