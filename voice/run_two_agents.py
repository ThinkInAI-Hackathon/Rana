from agents import Agent, Runner, set_default_openai_client, set_default_openai_api, set_tracing_disabled
from openai import AsyncOpenAI
from tts import text_to_speech
key="sk-f229205ebb8205eed80025aee0c96954ecaf7323f462bc0796093a8a13f6f199"

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
    model="deepseek-r1",  # 使用实际部署的模型名称
    instructions=prior_prompt1
)
agent_white = Agent(
    name="xiaobai",
    model="deepseek-r1",  # 使用实际部署的模型名称
    instructions=prior_prompt2
)

init_instruction = "你和另一个AI宠物猫相遇了，和对方打个招呼吧。通过多轮对话，逐步了解对方主人的情况。"
instruction = init_instruction
for i in range(5):
    # 小黑
    result_black = Runner.run_sync(agent_black, instruction)
    print("小黑：", result_black.final_output)
    # 使用台妹语音
    text_to_speech(result_black.final_output, voice_type="zh_female_wanwanxiaohe_moon_bigtts",save_file=True)
    instruction = result_black.final_output
    # 小白
    result_white = Runner.run_sync(agent_white, instruction)
    print("小白：", result_white.final_output)
    # 使用男性语音，暂时使用儿童音色
    text_to_speech(result_white.final_output, voice_type="zh_male_tiancaitongsheng_mars_bigtts",save_file=True, speed_ratio=1.2)
    instruction = result_white.final_output
