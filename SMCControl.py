import requests

import base64
import json

from tools.iLog import ilog

log = ilog('smc.log', 'smc').get_logger()


class SMCAuth:
    def __init__(self, user='smartconf', password='cqep.12345'):
        self.user = user
        self.passwrod = password
        self.smc_prefix = 'https://29.64.1.156/conf-portal'
        self.token = self.get_token()

    def get_token(self):
        # 待编码的数据
        # data = b"smartconf:cqep.12345"
        data = f'{self.user}:{self.passwrod}'

        # 进行base64编码
        encoded_data = base64.b64encode(bytes(data, 'utf-8'))
        deconded_data = encoded_data.decode()
        url = self.smc_prefix + '/tokens'
        #   'https://29.64.1.156/conf-portal/tokens?clientType=smcportal'
        # T                     /conf-portal/tokens?clientType=smcportal
        # GET /sys-portal/tokens?clientType=smcportal HTTP/1.1
        # Authorization: Basic YWRtaW46YWRtaW5AMTIzNA==
        # log.info(encoded_data)
        params = {'clientType': 'smcportal'}

        rr = requests.get(url, verify=False, params=params,
                          headers={'Authorization': f'Basic {deconded_data}'})
        # print(rr.text)
        rd = json.loads(rr.text)
        token = rd['uuid']
        print(token)
        if token:
            log.info(token)
            return token

        else:
            raise ValueError('token is wrong!')

    def get_session(self):

        s = requests.Session()

        # url='https://29.64.1.156/sys-portal/tokens'
        # pre = 'https://29.64.1.156/conf-portal'
        # url='https://29.64.1.156/conf-portal/tokens'
        #   'https://29.64.1.156/conf-portal/tokens?clientType=smcportal'
        # T                     /conf-portal/tokens?clientType=smcportal
        # GET /sys-portal/tokens?clientType=smcportal HTTP/1.1
        # Authorization: Basic YWRtaW46YWRtaW5AMTIzNA==

        params = {'clientType': 'smcportal'}

        # req=Request('GET', url,params=params)

        # prepped = s.prepare_request(req)

        # prepped.headers['Authorization']='Basic c21hcnRjb25mOmNxZXAuMTIzNA=='

        # s.auth=('Authorization','Basic c21hcnRjb25mOmNxZXAuMTIzNDU=')
        # settings = s.merge_environment_settings(prepped.url, {}, {'verify':False}, None,None)
        # s.headers['Authorization']='Basic c21hcnRjb25mOmNxZXAuMTIzNDU='
        s.headers['Token'] = self.token
        resp = s.get(self.smc_prefix, verify=False, params=params)

        # resp = s.send(prepped, **settings)
        log.info(resp.status_code)
        return s


class SMCCmd:
    '''
    用于发送smc的控制指令

    '''

    def __init__(self):

        ##
        smc = SMCAuth()

        self.smc_prefix = smc.smc_prefix

        self.session = smc.get_session()

        self.conferenceId = self.get_conferenceId()

    def get_conferenceId(self):
        '''当前正在召开的会议id
        多个会议时，应该可以选择
        '''
        cmd = '/conferences/conditions'
        data = {
            "active": 'true',
            "keyword": "",
            "organizationId": "",
            "startTime": "",
            "endTime": "",
            "showCurrentOrg": '1'
        }
        param = {'page': '0',
                 'size': '20'
                 }
        r = self.exe_cmd('post', cmd, data, params=param)

        rr = json.loads(r.text)

        return rr['content'][0]['id']

    def exe_cmd(self, verb, cmd, data=None, params=None):
        url = self.smc_prefix + cmd
        # 接受API反馈
        res = ''
        if verb == 'get':
            res = self.session.get(url, json=data, params=params)
        elif verb == 'post':
            res = self.session.post(url, json=data, params=params)
        elif verb == 'patch':
            res = self.session.patch(url, json=data, params=params)

        return res

    def get_chairmanId(self):
        #         GET /online/conferences/{conferenceId}/detail
        cmd = f'/online/conferences/{self.conferenceId}/detail'
        r = self.exe_cmd('get', cmd)

        r1 = json.loads(r.text)

        return r1['conferenceState']['chairmanId']

    def get_participants_list(self):
        cmd = f'/conferences/{self.conferenceId}/participants'
        params = {
            'page': '0',
            'size': '1000'

        }
        r = self.exe_cmd('get', cmd, params=params)
        r = json.loads(r.text)
        return r['content']

    def stop_chairman_poll(self):
        #         POST
        cmd = f'/online/conferences/{self.conferenceId}/participants/participantMultiPicPoll'
        data = {
            "participantId": "",
            "chairmanPoll": 'true',
            "multiPicPollDto": {
                "pollStatus": "STOP"
            }
        }

        r = self.exe_cmd('post', cmd, data)

        return r.text

    def broadcast_participant(self, participantId):
        cmd = f'/online/conferences/{self.conferenceId}/status'
        data = {
            'broadcaster': participantId
        }
        r = self.exe_cmd('patch', cmd, data)
        return r.text

    def mute_conferences(self):
        '''
        除主席外，全部静音
        '''
        cmd = f'/online/conferences/{smccmd.get_conferenceId()}/status'
        data = {
            "isMute": 'true'
        }
        r = self.exe_cmd('patch', cmd, data)

        return r.text

    def view_participant(self, view_participantId, viewed_participantId, isMute='true'):
        # PATCH /online/conferences/{conferenceId}/participants/{participantId}/status
        cmd1 = f'/online/conferences/{self.conferenceId}/participants/{view_participantId}/status'
        data1 = {

            "multiPicInfo": {
                "picNum": 1,
                "mode": 1,
                "subPicList": [
                    {
                        "participantId": viewed_participantId,
                        "streamNumber": 0
                    }
                ]
            }
        }
        cmd2 = f'/online/conferences/{self.conferenceId}/participants/{viewed_participantId}/status'

        data2 = {

            "isMute": isMute,

        }

        self.mute_conferences()
        r1 = self.exe_cmd('patch', cmd1, data1)
        r2 = self.exe_cmd('patch', cmd2, data2)

        return (r1.text, r2.text)

if __name__=='__main__':

    smccmd=SMCCmd()
    print(smccmd.get_participants_list())
