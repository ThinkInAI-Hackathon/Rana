# Speech-to-Text 千牛的语音识别效果似乎不太好
import asyncio
import gzip
import json
import time
import uuid
import websockets
import pyaudio

# -------------------- 协议相关常量和函数 --------------------

PROTOCOL_VERSION = 0b0001

# Message Types
FULL_CLIENT_REQUEST = 0b0001
AUDIO_ONLY_REQUEST = 0b0010
FULL_SERVER_RESPONSE = 0b1001
SERVER_ACK = 0b1011
SERVER_ERROR_RESPONSE = 0b1111

# Message Type Specific Flags
NO_SEQUENCE = 0b0000
POS_SEQUENCE = 0b0001
NEG_SEQUENCE = 0b0010
NEG_WITH_SEQUENCE = 0b0011

# 序列化和压缩方式
NO_SERIALIZATION = 0b0000
JSON_SERIALIZATION = 0b0001
NO_COMPRESSION = 0b0000
GZIP_COMPRESSION = 0b0001
from config import Qiniu_API_KEY
API_KEY = Qiniu_API_KEY

def generate_header(message_type=FULL_CLIENT_REQUEST,
                    message_type_specific_flags=NO_SEQUENCE,
                    serial_method=JSON_SERIALIZATION,
                    compression_type=GZIP_COMPRESSION,
                    reserved_data=0x00):
    header = bytearray()
    header_size = 1
    header.append((PROTOCOL_VERSION << 4) | header_size)
    header.append((message_type << 4) | message_type_specific_flags)
    header.append((serial_method << 4) | compression_type)
    header.append(reserved_data)
    return header

def generate_before_payload(sequence: int):
    before_payload = bytearray()
    before_payload.extend(sequence.to_bytes(4, 'big', signed=True))
    return before_payload

def parse_response(res):
    """
    如果 res 是 bytes，则按协议解析；
    如果 res 是 str，则直接返回文本内容，避免出现位移操作错误。
    """
    if not isinstance(res, bytes):
        return {'payload_msg': res}
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0f
    serialization_method = res[2] >> 4
    message_compression = res[2] & 0x0f
    payload = res[header_size * 4:]
    result = {}
    if message_type_specific_flags & 0x01:
        seq = int.from_bytes(payload[:4], "big", signed=True)
        result['payload_sequence'] = seq
        payload = payload[4:]
    result['is_last_package'] = bool(message_type_specific_flags & 0x02)
    if message_type == FULL_SERVER_RESPONSE:
        payload_size = int.from_bytes(payload[:4], "big", signed=True)
        payload_msg = payload[4:]
    elif message_type == SERVER_ACK:
        seq = int.from_bytes(payload[:4], "big", signed=True)
        result['seq'] = seq
        if len(payload) >= 8:
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload_msg = payload[8:]
        else:
            payload_msg = b""
    elif message_type == SERVER_ERROR_RESPONSE:
        code = int.from_bytes(payload[:4], "big", signed=False)
        result['code'] = code
        payload_size = int.from_bytes(payload[4:8], "big", signed=False)
        payload_msg = payload[8:]
    else:
        payload_msg = payload

    if message_compression == GZIP_COMPRESSION:
        try:
            payload_msg = gzip.decompress(payload_msg)
        except Exception as e:
            pass
    if serialization_method == JSON_SERIALIZATION:
        try:
            payload_text = payload_msg.decode("utf-8")
            payload_msg = json.loads(payload_text)
        except Exception as e:
            pass
    else:
        payload_msg = payload_msg.decode("utf-8", errors="ignore")
    result['payload_msg'] = payload_msg
    return result

# -------------------- 基于麦克风采集 PCM 数据的 ASR 测试客户端 --------------------

class AsrMicClient:
    def __init__(self, token, ws_url, seg_duration=100, sample_rate=16000, channels=1, bits=16, format="pcm", **kwargs):
        """
        :param token: 鉴权 token
        :param ws_url: ASR websocket 服务地址
        :param seg_duration: 分段时长，单位毫秒
        :param sample_rate: 采样率（Hz）
        :param channels: 通道数（一般单声道为 1）
        :param bits: 采样位数（16 表示 16 位）
        :param format: 音频格式，这里设为 "pcm"
        """
        self.token = token
        self.ws_url = ws_url
        self.seg_duration = seg_duration  # 毫秒
        self.sample_rate = sample_rate
        self.channels = channels
        self.bits = bits
        self.format = format
        self.uid = kwargs.get("uid", "test")
        self.codec = kwargs.get("codec", "raw")
        self.streaming = kwargs.get("streaming", True)

    def construct_request(self, reqid):
        req = {
            "user": {"uid": self.uid},
            "audio": {
                "format": self.format,
                "sample_rate": self.sample_rate,
                "bits": self.bits,
                "channel": self.channels,
                "codec": self.codec,
            },
            "request": {"model_name": "asr", "enable_punc": True}
        }
        return req

    async def stream_mic(self):
        """
        异步生成麦克风采集的 PCM 数据段，
        使用 pyaudio 读取数据时设置 exception_on_overflow=False 避免输入溢出异常。
        """
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024)
        bytes_per_frame = self.channels * (self.bits // 8)
        frames_needed = int(self.sample_rate * self.seg_duration / 1000)
        bytes_needed = frames_needed * bytes_per_frame
        frames = []
        while True:
            try:
                data = await asyncio.to_thread(stream.read, 1024, False)
            except Exception as e:
                print("麦克风读取错误:", e)
                continue
            frames.append(data)
            if sum(len(f) for f in frames) >= bytes_needed:
                segment = b"".join(frames)[:bytes_needed]
                yield segment
                frames = []

    async def execute(self):
        reqid = str(uuid.uuid4())
        seq = 1
        request_params = self.construct_request(reqid)
        payload_bytes = json.dumps(request_params).encode("utf-8")
        payload_bytes = gzip.compress(payload_bytes)
        # 构造初始配置信息请求
        full_client_request = bytearray(generate_header(message_type_specific_flags=POS_SEQUENCE))
        full_client_request.extend(generate_before_payload(sequence=seq))
        full_client_request.extend((len(payload_bytes)).to_bytes(4, "big"))
        full_client_request.extend(payload_bytes)
        headers = {"Authorization": "Bearer " + self.token}
        # 用于记录上一次满足条件的响应文本与时间
        begin_time = time.time()
        print(f"开始时间：{begin_time}")

        try:
            async with websockets.connect(self.ws_url, extra_headers=headers, max_size=1000000000) as ws:
                await ws.send(full_client_request)
                try:
                    res = await asyncio.wait_for(ws.recv(), timeout=10.0)
                except asyncio.TimeoutError:
                    print(f"{time.time() - begin_time}毫秒等待配置信息响应超时")
                    return
                result = parse_response(res)
                print(f"{time.time() - begin_time}毫秒配置响应：", result)

                # 开始采集麦克风音频并分段发送
                async for chunk in self.stream_mic():
                    seq += 1
                    audio_only_request = bytearray(
                        generate_header(message_type=AUDIO_ONLY_REQUEST,
                                        message_type_specific_flags=POS_SEQUENCE))
                    audio_only_request.extend(generate_before_payload(sequence=seq))
                    compressed_chunk = gzip.compress(chunk)
                    audio_only_request.extend((len(compressed_chunk)).to_bytes(4, "big"))
                    audio_only_request.extend(compressed_chunk)
                    await ws.send(audio_only_request)
                    try:
                        res = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        result = parse_response(res)
                        print(f"{time.time() - begin_time}毫秒接收响应：", result)
                        
                    except asyncio.TimeoutError:
                        pass
                    await asyncio.sleep(self.seg_duration / 1000.0)
        except Exception as e:
            print("异常：", e)

    def run(self):
        asyncio.run(self.execute())

# -------------------- 入口 --------------------

if __name__ == '__main__':
    # 替换下面的 token 与 ws_url 为你的实际参数 停止直接ctrl+c即可
    token = API_KEY
    ws_url = "wss://api.qnaigc.com/v1/voice/asr"
    seg_duration = 300 # 分段时长，单位毫秒,网络环境不好建议调大，否则会丢包
    client = AsrMicClient(token=token, ws_url=ws_url, seg_duration=seg_duration, format="pcm")
    client.run()

