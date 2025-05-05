# 🗣️ Kokoro TTS FastAPI Server

這是一個以 [Kokoro](https://github.com/rinnakk/kokoro) 為核心構建的文字轉語音（Text-to-Speech）API 服務，使用 [FastAPI](https://fastapi.tiangolo.com/) 開發，支援多種語音風格，並已容器化，方便快速部署與整合。

## 🚀 功能特色

- ✅ 提供 `/v1/audio/speech` 語音合成 API
- ✅ 使用 Kokoro 輕量 TTS 模型（支援英文、拼音、IPA）
- ✅ 可指定語音風格（voice）
- ✅ 支援 Docker Compose 開發與部署
- ✅ 可即時掛載程式目錄，方便本地開發

## 🧱 專案結構

```
.
├── app/                    # FastAPI 主程式
│   ├── main.py             # API 路由定義
│   └── kokoro_tts.py       # Kokoro TTS 處理模組
├── Dockerfile              # 建立容器映像
├── docker-compose.yml      # 容器啟動設定
├── requirements.txt        # Python 套件清單
└── README.md
```

## ⚙️ 安裝與執行

### 🔧 1. 安裝 Docker 與 Docker Compose

請先安裝 Docker 與 docker-compose：

- [Docker 官方下載](https://www.docker.com/products/docker-desktop/)

### ▶️ 2. 啟動服務

```bash
docker compose up --build
```

> 預設會安裝 Kokoro 相關套件並啟動 API 伺服器於 `http://localhost:8000`

## 📡 API 使用方式

### `POST /v1/audio/speech`

#### 請求格式（JSON）

```json
{
  "input": "Hello! This is Kokoro speaking.",
  "model": "kokoro",
  "voice": "af_heart"
}
```

> `model` 必須為 `"kokoro"`，`voice` 可選擇 Kokoro 所支援的語音風格。

#### 回應格式

- 回傳 `audio/wav` 音訊檔案

## 🧪 測試指令

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Kokoro is fast and light.","model":"kokoro","voice":"af_heart"}' \
  --output kokoro.wav
```

## 📦 開發者模式

若你希望即時修改程式碼無需重建容器，可透過 volume 掛載：

```yaml
# docker-compose.yml 範例片段
services:
  tts-server:
    volumes:
      - ./app:/app
```

也可在開發時使用：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧾 License

- 本專案使用 MIT 授權
- Kokoro 模型依照 Apache 2.0 授權條款使用

## 🙋‍♀️ 聯絡與協助

若有建議或問題，歡迎提交 issue 或貢獻 pull request。
