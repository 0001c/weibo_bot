from time import sleep
import requests
import json
import os
from ai_utils import generate_response
import json, requests, re


def get_header():
    with open("weibo_cookie.json",'r') as f:
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
        name = json.loads(requests.get(url=url,headers=get_header()).content.decode('utf-8'))['data']['user']['screen_name']
    except:
        name = uid
    if name == '':
        name = uid
    # 缓存昵称
    cache[uid] = name
    return name


# 初始化已有的mid
def get_mids(uid):
    file_path = 'weibo_mid_'+get_name(uid)+uid+'.json'
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
        print('初始化mid')
        url = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=0'
        try:
            resp = json.loads(requests.get(url=url,headers=get_header()).content.decode('utf-8'))
        except:
            print('请检查uid是否正确')
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
        print(f'初始化mid完成，最新mid：{mids_dict["max_id"]}')
        with open(file_path,'w') as f:
            json.dump(mids_dict,f,ensure_ascii=False,indent=2)
    else:
        print(f'{get_name(uid)}已存在数据')
    return mids_dict

# 获取最新的mid
def get_new_mid(uid):
    mids_dict = get_mids(uid)
    mids = mids_dict['mids']
    max_id = mids_dict['max_id']

    url = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=0'
    try:
        resp = json.loads(requests.get(url=url,headers=get_header()).content.decode('utf-8'))
    except:
        print('请检查uid是否正确')
        reset_uid(uid,'0')
        return None
    list = resp['data']['list']
    print('正在检索是否有更新')
    # 只检查最新的5条微博即可
    for item in list[:5]:
        sleep(1)
        mid = item['id']
        if mid not in mids and mid > max_id:
            create_time = item['created_at']
            print(f'发现新的mid：{mid},创建时间：{create_time}')
            mids_dict['mids'].append(mid)
            
            with open('weibo_mid_'+get_name(uid)+uid+'.json','w') as f:
                mids_dict = {'nickname':get_name(uid),
                            'uid':uid,
                            "mids": mids,
                            'max_id': mid}
                json.dump(mids_dict,f,ensure_ascii=False,indent=2)
            print(f'更新mid完成，最新mid：{mids_dict["max_id"]}')
            
            return mid
    else:
        print('没有新的微博内容')
    


# 通过mid获取帖子的内容
def get_context(mid):
    url = f'https://weibo.com/ajax/statuses/show?id={mid}&locale=zh-CN&isGetLongText=true'
    resp = json.loads(requests.get(url=url,headers=get_header()).content.decode('utf-8'))
    text_raw = resp['text_raw']
    return text_raw

# 调用AI生成回复
def generate_weibo_response(mid):
    context = get_context(mid)
    print(f'微博内容：{context}')
    # 调用AI生成回复
    ai_response = generate_response(context)
    print(f'AI生成的回复：{ai_response}')
    return ai_response

def post_response(mid, comment=''):
    print(f'正在回复：{mid}')
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
            print(f'成功回复mid：{mid}')
        else:
            print(f'回复mid：{mid}失败，错误信息：{resp.get("msg", "未知错误")}')
    except Exception as e:
        print(f'回复mid：{mid}时发生错误：{str(e)}')

def get_config():
    with open('config.json','r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def reset_uid(uid,enabled):
    config = get_config()
    config['uid'][uid] = enabled
    save_config(config)
    
def save_config(config):
    with open('config.json','w', encoding='utf-8') as f:
        json.dump(config,f,ensure_ascii=False,indent=2)


def main():
    while True:
        config = get_config()
        uid_list = config['uid']

        for uid in uid_list.keys():
            enabled = uid_list[uid]
            print(f'用户{uid}的状态：{enabled}')
            nickname = get_name(uid)
            print(f'正在处理用户{nickname}({uid})')
            if enabled == "1":
                if nickname == uid:
                    print(f'用户{nickname}({uid})的昵称与uid相同，已禁用')
                    reset_uid(uid,'0')
                else:
                    # 获取新微博
                    mid = get_new_mid(uid)
                    if mid:
                        # 调用AI生成回复
                        post_response(mid)
                
        # 休眠
        print(f'休眠{config["sleep_time"]}秒')
        sleep(config['sleep_time'])



if __name__ == "__main__":
    main()
    


    
    
