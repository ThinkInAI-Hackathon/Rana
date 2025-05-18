import os
import time
import wave
import pyaudio
import json
import requests
from datetime import datetime
from config import QNAIGC_API_KEY
from stt import tencent_speech2text
from tts import text_to_speech

# 录音参数设置
FORMAT = pyaudio.paInt16  # 音频格式
CHANNELS = 1  # 单声道
RATE = 16000  # 采样率 16kHz (腾讯云语音识别要求)
CHUNK = 1024  # 数据块大小
RECORD_SECONDS = 5  # 默认录音时长
WAVE_OUTPUT_FILENAME = "temp_recording.wav"  # 临时录音文件名

# 创建输出目录
if not os.path.exists("output"):
    os.makedirs("output")

def record_audio(seconds=RECORD_SECONDS):
    """录制音频并保存为WAV文件"""
    print(f"准备录音，将录制 {seconds} 秒...")
    time.sleep(1)  # 给用户准备的时间
    print("开始录音，请说话...")
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("录音结束!")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # 保存录音文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output/recording_{timestamp}.wav"
    
    # 同时保存为临时文件和带时间戳的文件
    for filename in [WAVE_OUTPUT_FILENAME, output_filename]:
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    
    print(f"录音已保存为: {output_filename}")
    return WAVE_OUTPUT_FILENAME

def chat_with_llm(text):
    """与大语言模型对话"""
    url = "https://api.qnaigc.com/v1/chat/completions"
    
    payload = {
        "stream": False,
        "model": "qwq-32b",
        "messages": [
            {
                "role": "system",
                "content": "你是一个友好的AI助手，请用简洁自然的语言回答问题。"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {QNAIGC_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("正在发送请求到大语言模型...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            print(f"AI回复: {reply}")
            return reply
        else:
            print(f"无法解析AI回复: {result}")
            return "抱歉，我无法理解您的问题。"
    
    except Exception as e:
        print(f"请求AI时出错: {str(e)}")
        return "抱歉，连接AI服务时出现问题。"

def main():
    print("=== AI语音对话系统 ===")
    print("说'再见'或'退出'可以结束对话")
    
    conversation_history = []
    
    while True:
        # 1. 录制音频
        audio_file = record_audio()
        
        # 2. 语音转文字
        user_text = tencent_speech2text(audio_file)
        if not user_text:
            print("无法识别您的语音，请重试。")
            # text_to_speech("抱歉，我没有听清楚，请再说一次。", voice_type="zh_male_naiqimengwa_mars_bigtts")
            continue
        
        print(f"您说: {user_text}")
        
        # 检查是否结束对话
        if any(keyword in user_text for keyword in ["再见", "退出", "结束", "拜拜"]):
            # text_to_speech("再见，期待下次与您交流！", voice_type="zh_male_naiqimengwa_mars_bigtts")
            print("对话结束，再见！")
            break
        
        # 3. 发送到大语言模型
        ai_response = chat_with_llm(user_text)
        
        # 4. 文字转语音并播放
        text_to_speech(ai_response, voice_type="zh_male_naiqimengwa_mars_bigtts")
        
        # 保存对话历史
        conversation_history.append({"user": user_text, "ai": ai_response})

if __name__ == "__main__":
    main()