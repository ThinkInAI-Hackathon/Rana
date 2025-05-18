from agents import Agent, Runner, set_default_openai_client, set_default_openai_api, set_tracing_disabled
from openai import AsyncOpenAI
from config import Qiniu_API_KEY
key = Qiniu_API_KEY
from tts import text_to_speech

prior_prompt_filename = r"E:\Project\Rana\voice\prior_prompt1.txt"
with open(prior_prompt_filename, 'r', encoding='utf-8') as file:
    prior_prompt1 = file.read()  # 读取整个文件内容为一个字符串

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

for i in range(5):
    instruction = input("请输入对话：")
    print(f"你好，{instruction}")  # 输出结果

    result_black = Runner.run_sync(agent_black, instruction)
    print("小黑：", result_black.final_output)
    text_to_speech(result_black.final_output, voice_type="zh_female_wanwanxiaohe_moon_bigtts", 
                                        save_file=False, play_immediately=True, speed_ratio=1.0)
     
