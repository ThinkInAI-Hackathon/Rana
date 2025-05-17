import base64
import json
import types
from flask import Blueprint, jsonify
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models
import pyaudio
import wave
import numpy as np
import threading
from config import Tecent_API_SEC,Tecent_API_KEY
# stt tecent
def tencent_speech2text(input_filepath):
  try:
      cred = credential.Credential(Tecent_API_SEC, Tecent_API_KEY)
      httpProfile = HttpProfile()
      httpProfile.endpoint = "asr.tencentcloudapi.com"

      clientProfile = ClientProfile()
      clientProfile.httpProfile = httpProfile
      client = asr_client.AsrClient(cred, "", clientProfile)

      rawData = open(input_filepath, "rb").read()
      base64_data = base64.b64encode(rawData).decode("utf-8")
      base64_data = base64_data.replace("\n", "").replace("\r", "")

      req = models.SentenceRecognitionRequest()
      params = {
        "EngSerViceType": "16k_zh",
        "SourceType": 1,
        "VoiceFormat": "wav",
        "Data": base64_data
      }
      req.from_json_string(json.dumps(params))

      resp = client.SentenceRecognition(req)
      print(resp.to_json_string())
      return resp.Result

  except TencentCloudSDKException as err:
      print(err)

# 示例使用
if __name__ == "__main__":
    filepath = R'E:\Project\Rana\voice\1.wav'
    print(tencent_speech2text(filepath))