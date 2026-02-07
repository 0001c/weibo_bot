import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# 加载.env文件中的环境变量,文件路径为Config\.env
load_dotenv(r'Config\.env')

# 从环境变量中获取您的API KEY，配置方法见：https://www.volcengine.com/docs/82379/1399008
api_key = os.getenv('ARK_API_KEY')
if not api_key:
    raise ValueError("ARK_API_KEY 环境变量未设置")
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=api_key,
)

# 从config.json中读取prompt
with open(r'Config\config.json','r', encoding='utf-8') as f:
    config = json.load(f)
    prompt = config['prompt']

def generate_response(text_raw):
    """
    根据微博内容生成回复
    
    Args:
        text_raw: 微博原始文本内容
    
    Returns:
        str: 生成的回复内容
    """
    try:
        response = client.responses.create(
            model="doubao-seed-1-6-flash-250828",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"{prompt}{text_raw}"
                        },
                    ],
                }
            ]
        )
        
        # 从响应中提取实际的回复内容
        if hasattr(response, 'output') and len(response.output) > 1:
            output_message = response.output[1]
            if hasattr(output_message, 'content') and len(output_message.content) > 0:
                output_text = output_message.content[0]
                if hasattr(output_text, 'text'):
                    return output_text.text
        # 如果以上结构不匹配，尝试其他可能的结构
        elif hasattr(response, 'choices') and len(response.choices) > 0:
            if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                return response.choices[0].message.content
            elif hasattr(response.choices[0], 'text'):
                return response.choices[0].text
        elif hasattr(response, 'text'):
            return response.text
        return "生成回复失败：无法提取回复内容"
    except Exception as e:
        print(f"AI生成回复时出错: {e}")
        return f"生成回复失败: {str(e)}"