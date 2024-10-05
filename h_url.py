import json
import binascii
import base64
import re
import requests
import h_time

requests.urllib3.disable_warnings()
session = requests.Session()
session.verify = False

github_token_ = ''
github_repo = ''

user_agent_ = 'Dalvik/2.1.0 (Linux; U; Android 11; Pixel 5 Build/RD1A.201105.003.A1)'

# ==== User Info ====
def ReadConf():
    data = json.loads(
        requests.get(
            url=f'https://raw.githubusercontent.com/{github_repo}/main/fg.json', verify=False
        ).text
    )
    global app_ver_, data_ver_, date_ver_, asset_bundle_folder_, data_server_folder_crc_
    app_ver_ = data['global']['appVer']
    data_ver_ = data['global']['dataVer']
    date_ver_ = data['global']['dateVer']
    asset_bundle_folder_ = data['global']['assetbundleFolder']
    data_server_folder_crc_ = data['global']['dataServerFolderCrc']


def WriteConf(data):
    UploadFileToRepo('fg.json', data, 'Update')


def UpdateBundleFolder(assetbundle):
    new_assetbundle = h_enc.MouseInfoMsgPack(base64.b64decode(assetbundle))
    print(f'new_assetbundle: {new_assetbundle}')
    global asset_bundle_folder_, data_server_folder_crc_
    asset_bundle_folder_ = new_assetbundle
    data_server_folder_crc_ = binascii.crc32(new_assetbundle.encode('utf8'))
    return 1


# ===== End =====

# ===== Telegram arguments =====
TelegramBotToken = ''
TelegramAdminId = ''


def SendMessageToAdmin(message):
    if TelegramBotToken != 'nullvalue':
        nowtime = h_time.GetFormattedNowTime()
        url = f'https://api.telegram.org/bot{TelegramBotToken}/sendMessage?chat_id={TelegramAdminId}&parse_mode=markdown&text={message}'
        # print(str(base64.b64encode(url.encode('utf-8')), 'utf-8'))
        result = json.loads(requests.get(url, verify=False).text)
        if not result['ok']:
            print(result)


# ===== End =====


# ===== Github api =====
def UploadFileToRepo(filename, content, commit='updated'):
    url = f'https://api.github.com/repos/{github_repo}/contents/' + filename
    res = requests.get(url=url)
    jobject = json.loads(res.text)
    header = {
        'Content-Type': 'application/json',
        'User-Agent': f'{github_repo}_bot',
        'Authorization': 'token ' + github_token_,
    }
    content = str(base64.b64encode(content.encode('utf-8')), 'utf-8')
    form = {
        'message': commit,
        'committer': {
            'name': f'Charlie',
            'email': 'charlie@stud.im'
        },
        'content': content,
    }
    if 'sha' in jobject:
        form['sha'] = jobject['sha']
    form = json.dumps(form)
    result = requests.put(url, data=form, headers=header)
    print(result.status_code)


# ===== End =====

httpheader = {
    'Accept-Encoding': 'gzip, identity',
    'User-Agent': user_agent_,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'Keep-Alive, TE',
    'TE': 'identity',
}


def NewSession():
    return requests.Session()


def PostReq(s, url, data):
    res = s.post(url, data=data, headers=httpheader, verify=False).json()
    res_code = res['response'][0]['resCode']
    if res_code != '00':
        detail = res['response'][0]['fail']['detail']
        message = f'[ErrorCode: {res_code}]\n{detail}'
        SendMessageToAdmin(message)
        raise Exception(message)
    return res
