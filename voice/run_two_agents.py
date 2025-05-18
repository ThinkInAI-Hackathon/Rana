from agents import Agent, Runner, set_default_openai_client, set_default_openai_api, set_tracing_disabled
from openai import AsyncOpenAI
from tts import text_to_speech
import threading
import time
import queue
from playsound import playsound
from config import QNAIGC_API_KEY
key = QNAIGC_API_KEY

prior_prompt_filename = r"E:\Project\Rana\voice\prior_prompt1.txt"
with open(prior_prompt_filename, 'r', encoding='utf-8') as file:
    prior_prompt1 = file.read()  # 读取整个文件内容为一个字符串

prior_prompt_filename = r"E:\Project\Rana\voice\prior_prompt2.txt"
with open(prior_prompt_filename, 'r', encoding='utf-8') as file:
    prior_prompt2 = file.read()  # 读取整个文件内容为一个字符串

# 配置 七牛 API（请替换为实际的 API Key）
custom_client = AsyncOpenAI(base_url="https://api.qnaigc.com/v1", api_key=key)
set_default_openai_client(custom_client)
# 下面两行很重要，含泪踩过的坑！
set_default_openai_api("chat_completions")
set_tracing_disabled(True) 

# Agent 定义示例
agent_black = Agent(
    name="xiaohei",
    model="deepseek-v3",  # 使用实际部署的模型名称
    instructions=prior_prompt1
)
agent_white = Agent(
    name="xiaobai",
    model="deepseek-v3",  # 使用实际部署的模型名称
    instructions=prior_prompt2
)

# 创建一个事件对象，用于控制生成线程和播放线程的同步
audio_ready = threading.Event()

# 创建一个队列，用于存储音频文件路径
audio_queue = queue.Queue()

# 生成对话和语音的函数
def generate_conversation(instruction, rounds=5):
    current_instruction = instruction
    
    for i in range(rounds):
        # 小黑回复
        result_black = Runner.run_sync(agent_black, current_instruction)
        black_response = result_black.final_output
        print(f"回合 {i+1} - 小黑：", black_response)
        
        # 生成小黑的语音文件
        black_audio_file = text_to_speech(black_response, voice_type="zh_female_wanwanxiaohe_moon_bigtts", 
                                        save_file=True, play_immediately=False, speed_ratio=1.0)
        
        # 将小黑的音频文件路径添加到队列
        audio_queue.put(black_audio_file)
        
        # 如果是第一轮，通知播放线程可以开始播放
        if i == 0:
            audio_ready.set()
        
        # 更新指令，让小白回复
        current_instruction = black_response
        
        # 小白回复
        result_white = Runner.run_sync(agent_white, current_instruction)
        white_response = result_white.final_output
        print(f"回合 {i+1} - 小白：", white_response)
        
        # 生成小白的语音文件
        white_audio_file = text_to_speech(white_response, voice_type="ICL_zh_male_shaonianjiangjun_tob", 
                                        save_file=True, play_immediately=False, speed_ratio=1.0)
        
        # 将小白的音频文件路径添加到队列
        audio_queue.put(white_audio_file)
        
        # 更新指令，准备下一轮
        current_instruction = white_response
    
    # 所有对话生成完成后，添加一个结束标记
    audio_queue.put(None)

# 播放音频的函数
def play_audio():
    # 等待第一个音频文件生成完成
    audio_ready.wait()
    
    while True:
        # 从队列中获取音频文件路径
        audio_file = audio_queue.get()
        
        # 如果收到结束标记，退出循环
        if audio_file is None:
            break
        
        try:
            print(f"正在播放: {audio_file}")
            playsound(audio_file)
            print(f"播放完成: {audio_file}")
        except Exception as e:
            print(f"播放音频时出错: {str(e)}")
        
        # 标记任务完成
        audio_queue.task_done()

def main():
    print("=== AI宠物猫对话系统 ===")
    
    # 初始指令
    init_instruction = "你和另一个AI宠物猫相遇了，和对方打个招呼吧。通过多轮对话，逐步了解对方主人的情况。"
    
    # 创建并启动播放线程
    play_thread = threading.Thread(target=play_audio)
    play_thread.daemon = True
    play_thread.start()
    
    # 生成对话和语音
    generate_conversation(init_instruction)
    
    # 等待所有音频播放完成
    audio_queue.join()
    
    print("对话完成！")

if __name__ == "__main__":
    main()
