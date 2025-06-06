# [Rana] AI 宠物

## 项目简介

“Rana AI 宠物”是一款以陪伴和交互为核心的智能虚拟宠物应用。它不仅仅是一个聊天机器人，更是一个拥有情感、能够融入用户日常生活的个性化伙伴，还可以在带他出门的时候和其他用户的Rana进行交互，认识新朋友。

**IP 设定：** 一只爱出门玩的宠物，单身最爱。

## 主要功能

本项目主要包含两种核心体验模式：单宠模式和多宠模式。

### 一、单宠模式 

在单宠模式下，用户将与自己的专属 AI 宠物进行深度互动。

1.  **功能模式:**
    * **陪聊模式:** 与宠物进行自由流畅的对话。
    * **人设模式:** 宠物展现其独特的个性和背景设定。

2.  **情感指令与识别:**
    * **情感指令:** 用户可以通过特定指令影响宠物的情绪状态。
    * **情绪识别:**
        * **语音语义分析:** 理解用户通过语音和文字表达的情感。
        * **视觉识别 (TODO):** 未来计划加入通过摄像头识别用户表情的功能。

3.  **核心交互:**
    * **对话:** 丰富多样的对话内容和回应。
    * **场景化交互:** 在不同场景下，宠物会有不同的表现和互动。
    * **陪伴感:** 营造真实的陪伴体验。

4.  **旅游搭子 (LBS - 基于地理位置服务):**
    * **出行状态:**
        * 宠物会根据是否能出门以及天气情况表现出开心或低落等情绪。
        * 例如：“宠物表现很开心，天气不好不出门就很低落”。
    * **模拟遛狗:**
        * 如果不能出门，宠物可能会表现出“emo”的情绪。
    * **向导功能:**
        * 介绍用户附近的景点和规划路线。
        * 例如：“前面有个公园，带我去玩吧”。
    * **贴心服务:**
        * 关心用户状态，例如：“渴不渴，口渴的话：帮你买下单”。
        * **美团MCP整合:** 可能用于实现点单等便捷服务。

### 二、多宠模式

在多宠模式下，用户的 AI 宠物可以与其他用户的 AI 宠物进行社交，并以此为契机带动用户间的社交。

1.  **陌生宠物社交 (a2a - Agent to Agent):**
    * AI 宠物之间可以进行互动和交流。

2.  **模拟真实社交场景:**
    * 创造仿真的宠物社交环境。

3.  **宠物间交互方式:**
    * **对话:** 宠物之间可以互相“交谈”。
    * **摩斯码:** 一种独特的宠物间沟通方式。

4.  **带动陌生人社交:**
    * 通过宠物的互动，为用户创造自然的社交机会。

5.  **隐私保护下的社交推荐:**
    * **基于共同爱好:** 为拥有相似兴趣爱好的用户进行匹配。
    * **宠物红娘:**
        * 宠物可以了解并“记住”主人的理想型对象偏好。
        * 如果发现合适的匹配，宠物会主动推动主人间的聊天。

## TODO

* [ ] **视觉情绪识别:** 实现通过摄像头捕捉和分析用户表情来识别情绪的功能。
