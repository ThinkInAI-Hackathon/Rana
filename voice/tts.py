# Text-to-Speech
# 中文语音合成
import requests
import json
import os
import tempfile
import base64
from datetime import datetime
import time
from config import Qiniu_API_KEY
from playsound import playsound

API_KEY = Qiniu_API_KEY
url = 'https://api.qnaigc.com/v1/voice/tts'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

def text_to_speech(text, voice_type="en_female_anna_mars_bigtts", 
                  encoding="mp3", speed_ratio=1.0, play_immediately=True, save_file=True):
    """
    将文本转换为语音并直接播放
    
    参数:
        text (str): 要转换的文本
        voice_type (str): 语音类型
        encoding (str): 输出音频格式
        speed_ratio (float): 语音速度比例
        play_immediately (bool): 是否立即播放
        save_file (bool): 是否同时保存文件（用于调试）
    
    返回:
        bool: 是否成功播放
    """
    # 准备请求数据
    data = {
        "audio": {
            "voice_type": voice_type,
            "encoding": encoding,
            "speed_ratio": speed_ratio
        },
        "request": {
            "text": text
        }
    }
    
    try:
        # 发送请求
        print(f"正在发送请求到 {url}...")
        response = requests.post(url, headers=headers, json=data)
        
        # 检查响应状态
        print(f"收到响应: 状态码 {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败: 状态码 {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        # 解析JSON响应
        try:
            json_response = response.json()
            print("成功解析JSON响应")
            
            raw_data_field = json_response.get('data', '')
            print("输出json:", raw_data_field)
            

            base64_data = raw_data_field

            # 如果找到了base64编码的数据，进行解码
            if base64_data:
                # 检查并移除可能的base64前缀（如data:audio/mp3;base64,）
                if ',' in base64_data:
                    base64_data = base64_data.split(',', 1)[1]
                
                try:
                    # 解码base64数据
                    audio_data = base64.b64decode(base64_data)
                    print(f"成功解码base64音频数据，大小: {len(audio_data)} 字节")
                except Exception as decode_error:
                    print(f"解码base64数据时出错: {str(decode_error)}")
            else:
                print("无法在JSON响应中找到音频数据。")
                # print(json.dumps(json_response, ensure_ascii=False, indent=2))
                return False
            
            # 处理音频数据
            if save_file:
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"{output_dir}/tts_debug_{timestamp}.{encoding}"
                
                with open(debug_filename, 'wb') as f:
                    f.write(audio_data)
                print(f"已保存音频文件: {debug_filename}")
                return debug_filename
            if play_immediately:
                # 创建临时文件
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{encoding}')
                temp_filename = temp_file.name
                temp_file.close()
                
                try:
                    with open(temp_filename, 'wb') as f:
                        f.write(audio_data)
                    
                    print(f"临时文件已创建: {temp_filename}")
                    print(f"正在播放语音...")
                    
                    time.sleep(0.5)
                    
                    try:
                        playsound(temp_filename)
                        print(f"语音播放完成")
                        return True
                    except Exception as play_error:
                        print(f"播放音频时出错: {str(play_error)}")
                        return False
                finally:
                    time.sleep(1)
                    try:
                        if os.path.exists(temp_filename):
                            os.unlink(temp_filename)
                            print(f"临时文件已删除")
                    except Exception as e:
                        print(f"删除临时文件时出错: {str(e)}")
            
            return True
            
        except json.JSONDecodeError:
            print("响应不是JSON格式，尝试作为二进制音频数据处理")
            
            # 处理二进制响应
            if save_file:
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"{output_dir}/tts_debug_{timestamp}.{encoding}"
                
                with open(debug_filename, 'wb') as f:
                    f.write(response.content)
                print(f"已保存调试文件: {debug_filename}")
            
            if play_immediately:
                # 创建临时文件
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{encoding}')
                temp_filename = temp_file.name
                temp_file.close()
                
                try:
                    with open(temp_filename, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"临时文件已创建: {temp_filename}")
                    print(f"正在播放语音...")
                    
                    time.sleep(0.5)
                    
                    try:
                        playsound(temp_filename)
                        print(f"语音播放完成")
                        return True
                    except Exception as play_error:
                        print(f"播放音频时出错: {str(play_error)}")
                        return False
                finally:
                    time.sleep(1)
                    try:
                        if os.path.exists(temp_filename):
                            os.unlink(temp_filename)
                            print(f"临时文件已删除")
                    except Exception as e:
                        print(f"删除临时文件时出错: {str(e)}")
            
            return True
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

# 示例使用
if __name__ == "__main__":
    # 测试默认参数，同时保存调试文件
    text_to_speech("我是你的AI宠物，你今天心情怎么样？", voice_type="zh_male_naiqimengwa_mars_bigtts",save_file=True)
    # text_to_speech("Meow Meow", speed_ratio=0.6, voice_type="en_female_anna_mars_bigtts", save_file=True)
    # 可以尝试不同的参数
    # text_to_speech("这是一段测试语音。", voice_type="zh_female_M398_conversation_wvae_bigtts", speed_ratio=1.2)