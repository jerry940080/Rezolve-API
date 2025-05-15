# 🗣️ Kokoro TTS FastAPI Server

這是一個以open-webui 為核心構建的語音客服服務，使用 [Open-webui](https://github.com/open-webui/open-webui) [Taigi](https://huggingface.co/Bohanlu/Taigi-Llama-2-Translator-7B) , [FastAPI](https://fastapi.tiangolo.com/)  開發，並已容器化，方便快速部署與整合。

## 🚀 功能特色

- ✅ 提供 `/v1/transcription` 語音抄寫 API
- ✅ 提供 `/v1/audio/speech` 語音合成 API
- ✅ 提供 `/translate` 台語翻譯 API
- ✅ 提供 open-webui 語音串接
- ✅ 支援 Docker Compose 開發與部署
- ✅ 可即時掛載程式目錄，方便本地開發

## 更新項目
- 05/15 更新TTS斷句判斷與錯誤返還條件, 可生成長句語音, 若有部分句子無法生成成功則跳過該句.

## 🧱 專案結構

```
.
rezolve-fastapi/
│
├── docker-compose.yml
│
├── asr/
│   ├── app/
│   │   ├── main.py
│   │   ├── asr_model.py       # ASR API 接口
│   │   └── whisper_handler.py # asr模型載入 (faster-whisper 格式)
│   │
│   ├── models/                # 用來儲存 ASR 模型檔案
│   │   └── <model_files>      # 包含config.json / model.bin / vocabulary.json
│   │
│   └── Dockerfile
│
├── translate/                 # TAIGI模型vram占用高(14GB) 已移至遠端server上
│   ├── app/
│   │   ├── main_trans.py      # 翻譯 API 接口
│   │   └── taigi_translator.py # 模型載入
│   │
│   ├── models/                # 用來儲存翻譯模型檔案
│   │   └── <model_files>      # 實際的翻譯模型檔案
│   │
│   ├── Dockerfile
│   └── requirements_trans.txt # 翻譯所需的依賴
│
├── tts/
│   ├── app/
│   │   ├── utils/             # TTS 工具
│   │   ├── main_tts.py        # TTS API接口
│   │   ├── hparams.py         # TTS 參數設定
│   │   ├── kokoro_tts.py      # TTS inference code
│   │   ├── tacotron2.py       # 文字轉mel模型載入
│   │   └── wavrrnn.py         # mel轉語音模型載入
│   │
│   ├── models/                # TTS 模型檔案
│   │   ├── tacotron2_latest.pyt
│   │   └── wavernn.pyt
│   │
│   ├── Dockerfile
│   └── requirements_tts.txt  # TTS 所需的依賴
│
└── README.md
```

## ⚙️ 安裝與執行

### 🔧 1. 安裝 Docker 與 Docker Compose

請先安裝 Docker 與 docker-compose：

- [Docker 官方下載](https://www.docker.com/products/docker-desktop/)

### ▶️ 2. 啟動服務

```bash
docker compose up --build
各模型port :

- open-webuiL 3000
- asr-server: 7000
- tts-server: 8000
- translate-server: 9000 (在4090server上)

請都用localhost開啟
```




## 📡 API 使用方式

### ASR: POST `/audio/transcriptions`

#### 請求參數（`multipart/form-data`）

| 欄位名稱 | 類型        | 說明                       |
|----------|-------------|----------------------------|
| `file`   | `UploadFile`| 音訊檔案（必填）           |
| `model`  | `str`       | 模型名稱（預設為 `whisper-1`）  |

```json
{
  "text": "這是轉錄後的語音內容"
}
```

---

## 🧪 測試範例

```bash
curl -X POST http://localhost:7000/audio/transcriptions \
  -F "file=@test.wav" \
  -F "model=whisper-1"
```

---

### TTS: `POST /v1/audio/speech`

#### 請求格式（JSON）

```json
{
  "input": "Hello! This is Kokoro speaking.",
  "model": "kokoro",
  "voice": "af_heart"
}
```

> `model` 必須為 `"kokoro"`

#### 回應格式

- 回傳 `audio/wav` 音訊檔案

## 🧪 測試指令

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"我慾食飯.","model":"kokoro","voice":"af_heart"}' \
  --output kokoro.wav
```

### 翻譯: `POST /translate`

#### 請求格式（JSON）

```json
{
  "source_sentence": "我慾食飯..",
  "target_language": "POJ" 
}
```
target_language options: POJ, ZH, HAN, HL, EN 


#### 回應格式

- 回傳 `audio/wav` 音訊檔案

## 🧪 測試指令

```bash
curl -X POST http://xxx.xx.xx.xx:9000/translate \
-H "Content-Type: application/json" \
-d'{ "source_sentence": "我欲食飯", "target_language": "ZH"}'
```
## Open-webui設定
![image](https://github.com/user-attachments/assets/37c28ca8-f01a-4b97-a5b1-6d2b20a9c717)


## 🧾 License

- 本專案使用 MIT 授權
- Kokoro 模型依照 Apache 2.0 授權條款使用

## 🙋‍♀️ 聯絡與協助

若有建議或問題，歡迎提交 issue 或貢獻 pull request。
