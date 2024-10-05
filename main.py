import json
import os
import re
from datetime import datetime, timezone

import requests
import h_time
import h_url

h_url.github_token_ = os.environ['GithubToken']
h_url.github_repo = os.environ['GithubRepo']
h_url.TelegramBotToken = os.environ['TGBotToken']
h_url.TelegramAdminId = os.environ['TGAdminId']



def main():

    utc_now = datetime.now(timezone.utc).timestamp()
    print(f'Starting jobs at {utc_now}')
    msg = ''
    msg += mainTicket(utc_now)
    msg += mainGacha(utc_now)
    msg += '***数据已更新***'
    print(msg)
    h_url.SendMessageToAdmin(msg)



def mainTicket(utc_now):
    # get json data
    url = 'https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/JP/master/mstShop.json'
    response = requests.get(url)
    fdata = response.json()
    fshops = []
    msg = '**兑换活动:**\n'
    for item in fdata:
        if 4001 in item.get('targetIds', []) and item.get('flag') == 4096:
            closeAtTime = item.get('closedAt')
            if closeAtTime > utc_now:
                fshops.append(item)
                detail = item.get('detail')
                limitNum = item.get('limitNum')
                msg += f'- `[常驻] 可兑换` ***{limitNum}*** `个`  \n'
        if 4001 in item.get('targetIds', []) and item.get('flag') == 2048:
            closeAtTime = item.get('closedAt')
            if closeAtTime > utc_now:
                fshops.append(item)
                detail = item.get('detail')
                limitNum = item.get('limitNum')
                match = re.search(r'【(.*?)】', detail)
                base_name_ss = match.group(1)
                print(f'hit: {detail}')
                msg += f'- `[活动]` **{base_name_ss}** `, 可兑换` ***{limitNum}*** `个`  \n'
    hjson = json.dumps(fshops, ensure_ascii=False, indent=4)
    h_url.UploadFileToRepo('fshops.json', hjson, h_time.GetNowTimeFileName())
    return msg



def mainGacha(utc_now):
    # get json data
    url = 'https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/JP/master/mstGacha.json'
    response = requests.get(url)
    fdata = response.json()
    fgacha = []
    msg = '**开放卡池:**\n'
    for item in fdata:
        closeAtTime = item.get('closedAt')
        if closeAtTime > utc_now:
            fgacha.append(item)
            name = item.get('name')
            type = item.get('type')
            match type:
                case 1:
                    # PU
                    imsg = '- `'
                case 3:
                    # FP
                    imsg = '- `'
                    continue
                case 7:
                    # Pay Only Gacha
                    imsg = '- `'
                case _:
                    imsg = f'- [{type}] `'
            name = simplifyGacha(isCool(name))
            if name != 'ストーリー召喚' and name != 'ストーリー':
                imsg += name
                msg += f'{imsg}`  \n'
    hjson = json.dumps(fgacha, ensure_ascii=False, indent=4)
    h_url.UploadFileToRepo('fgacha.json', hjson, h_time.GetNowTimeFileName())
    return msg

def isCool(text):
    coolSvts = ["シャルルマーニュ", "千子村正", "ボイジャー"]
    pattern = r"(\s)([^\s]+?)(ピックアップ)"
    
    def coolCheck(match):
        name = match.group(2)
        if not name:
            return match.group(0)
        wrapped_name = f"*%23{name}*"
        
        if name in coolSvts:
            wrapped_name = f"**{wrapped_name}**👍"
        return f"` {wrapped_name} `PU"
    
    result = re.sub(pattern, coolCheck, text)
    
    return result


def simplifyGacha(original_str):
    rStrs = ["記念", "ostbelt N", "キャンペーン", "召喚"]
    for rStr in rStrs:
        original_str = original_str.replace(rStr, '')
    original_str = original_str.replace('&', '%26')
    return original_str



if __name__ == '__main__':
    main()
