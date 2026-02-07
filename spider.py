from time import sleep
import time
import requests
import json
import os
from ai_utils import generate_response
import json, requests, re
from log_manager import add_log


def get_header():
    with open(r"Config\weibo_cookie.json",'r') as f:
        header=json.loads(f.read())
        cookie = header['Cookie']
        header["x-xsrf-token"] = re.findall(r'XSRF-TOKEN=([^;]+)', cookie)[0]
        # 加上Referer
        header['referer']='https://weibo.com/'
    return header

cache = {}
# 获取用户的昵称
def get_name(uid):
    # 从缓存中获取昵称
    if uid in cache:
        return cache[uid]
    try:
        url = f"https://weibo.com/ajax/profile/info?custom={uid}"
        resp = requests.get(url=url,headers=get_header())
        if resp.status_code != 200:
            add_log('ERROR',f'获取用户{uid}的昵称时出错，状态码：{resp.status_code}，检查cookie是否过期')
            print(f'获取用户{uid}的昵称时出错，状态码：{resp.status_code}，检查cookie是否过期')
            name = uid
            return name
        name = json.loads(resp.content.decode('utf-8'))['data']['user']['screen_name']
        print(f'获取用户{uid}的昵称：{name}')
    except:
        print(f'获取用户{uid}的昵称时出错')
        name = uid
    if name == '':
        print(f'获取用户{uid}的昵称时为空')
        name = uid
    # 缓存昵称
    cache[uid] = name
    return name


# 初始化已有的mid
def get_mids(uid):
    file_path = r'Cache\weibo_mid_'+get_name(uid)+uid+'.json'
    if not os.path.exists(file_path):
        # 创建空的JSON文件
        with open(file_path,'w') as f:
            json.dump({'mids':[],'max_id':0},f,ensure_ascii=False,indent=2)
            
    try:
        with open(file_path,'r') as f:
            mids_dict = json.load(f)
            mids = mids_dict['mids']
    except:
        mids_dict = {'nickname':get_name(uid),
                    'uid':uid,'mids':[],'max_id':0}
    if len(mids) == 0:
        add_log('INFO',f'初始化mid，uid：{uid}，昵称：{get_name(uid)}')
        print(f'初始化mid，uid：{uid}，昵称：{get_name(uid)}')
        url = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=0'
        try:
            resp = json.loads(requests.get(url=url,headers=get_header()).content.decode('utf-8'))
        except:
            add_log('ERROR',f'初始化mid时出错，uid：{uid}，昵称：{get_name(uid)}')
            print(f'初始化mid时出错，uid：{uid}，昵称：{get_name(uid)}')
            reset_uid(uid,'0')
            return mids_dict
        list = resp['data']['list']
        for item in list:
            sleep(1)
            mid = item['id']
            mids.append(mid)
        
        mids_dict = {'nickname':get_name(uid),
                    'uid':uid,
                    "mids": mids,
                    'max_id': mid}
        add_log('INFO',f'初始化mid完成，最新帖子mid：{mids_dict["max_id"]}')
        with open(file_path,'w') as f:
            json.dump(mids_dict,f,ensure_ascii=False,indent=2)
    else:
        add_log('INFO',f'{get_name(uid)}已存在数据')
    return mids_dict

# 获取最新的mid
def get_new_mid(uid):
    file_path = r'Cache\weibo_mid_'+get_name(uid)+uid+'.json'
    mids_dict = get_mids(uid)
    mids = mids_dict['mids']
    max_id = mids_dict['max_id']

    url = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=0'
    try:
        resp = json.loads(requests.get(url=url,headers=get_header()).content.decode('utf-8'))
    except:
        add_log('ERROR',f'初始化mid时出错，uid：{uid}，昵称：{get_name(uid)}')
        reset_uid(uid,'0')
        return None
    list = resp['data']['list']
    add_log('INFO',f'正在检索是否有更新，uid：{uid}，昵称：{get_name(uid)}，当前时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
    # 只检查最新的5条微博即可
    for item in list[:5]:
        sleep(1)
        mid = item['id']
        if mid not in mids and mid > max_id:
            create_time = item['created_at']
            add_log('INFO',f'发现新的mid：{mid},创建时间：{create_time}')
            print(f'发现新的mid：{mid},创建时间：{create_time}')
            mids_dict['mids'].append(mid)
            
            with open(file_path,'w') as f:
                mids_dict = {'nickname':get_name(uid),
                            'uid':uid,
                            "mids": mids,
                            'max_id': mid}
                json.dump(mids_dict,f,ensure_ascii=False,indent=2)
            add_log('INFO',f'更新mid完成，最新帖子mid：{mids_dict["max_id"]}，当前时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
            
            return mid
    else:
        add_log('INFO',f'没有新的微博内容，uid：{uid}，昵称：{get_name(uid)}，当前时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
    


# 通过mid获取帖子的内容
def get_context(mid):
    url = f'https://weibo.com/ajax/statuses/show?id={mid}&locale=zh-CN&isGetLongText=true'
    resp = json.loads(requests.get(url=url,headers=get_header()).content.decode('utf-8'))
    text_raw = resp['text_raw']
    return text_raw

# 调用AI生成回复
def generate_weibo_response(mid):
    context = get_context(mid)
    add_log('INFO',f'微博内容：{context}')
    # 调用AI生成回复
    ai_response = generate_response(context)
    add_log('INFO',f'AI生成的回复：{ai_response}')
    return ai_response

def post_response(mid, comment=''):

    add_log('INFO',f'正在回复{nickname}({uid})：{mid}')
    url = f'https://weibo.com/ajax/comments/create'
    # 如果没有提供comment，则调用AI生成回复
    if not comment:
        comment = generate_weibo_response(mid)
    data = {
        'id': mid,
        'comment': comment,
        'pic_id': '',
        'is_repost': '0',
        'comment_ori': '0',
        'is_comment': '0'
    }
    try:
        print(data)
        response = requests.post(url=url, headers=get_header(), data=data)
        print(f'请求状态码：{response.status_code}')
        # print(f'响应内容：{response.content.decode("utf-8")}')
        resp = json.loads(response.content.decode('utf-8'))
        if resp.get('ok') == 1:
            add_log('INFO',f'成功回复mid：{mid}')
        else:
            add_log('ERROR',f'回复mid：{mid}失败，错误信息：{resp.get("msg", "未知错误")}')
    except Exception as e:
        add_log('ERROR',f'回复mid：{mid}时发生错误：{str(e)}')

def get_config():
    with open(r'Config\config.json','r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def reset_uid(uid,enabled):
    config = get_config()
    config['uid'][uid] = enabled
    save_config(config)
    
def save_config(config):
    with open(r'Config\config.json','w', encoding='utf-8') as f:
        json.dump(config,f,ensure_ascii=False,indent=2)


def main():
    while True:
        config = get_config()
        uid_list = config['uid']

        for uid in uid_list.keys():
            enabled = True if uid_list[uid] == "1" else False
            
            print(f'用户{uid}的状态：{enabled}')
            add_log('INFO',f'用户{uid}的状态：{enabled}')
            
            
            if enabled:
                global nickname
                nickname = get_name(uid)
                add_log('INFO',f'正在处理用户{nickname}({uid})')
                if nickname == uid:
                    add_log('INFO',f'用户{nickname}({uid})的昵称与uid相同，已禁用')
                    print(f'用户{nickname}({uid})的昵称与uid相同，已禁用')
                    reset_uid(uid,'0')
                else:
                    # 获取新微博
                    mid = get_new_mid(uid)
                    if mid:
                        # 调用AI生成回复
                        post_response(mid)
                
        # 休眠
        add_log('INFO',f'休眠{config["sleep_time"]}秒')
        print(f'休眠{config["sleep_time"]}秒')
        sleep(config['sleep_time'])



if __name__ == "__main__":
    main()
    


    
    
