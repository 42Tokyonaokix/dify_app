# email-service/main.py 設計書

## 目的
iCloudメールをIMAPで取得し、Difyから呼び出し可能なREST APIを提供する。

## 必要な機能

### 1. 設定管理
- 環境変数から iCloud 認証情報を読み込む
- IMAP サーバー設定の管理

### 2. IMAP接続
- iCloud IMAP サーバーへの接続
- SSL/TLS 通信
- 認証処理

### 3. メール取得機能
- 受信箱からメールを取得
- メール件数の制限（例：最新10件）
- メールの基本情報を抽出（件名、送信者、本文など）

### 4. REST API エンドポイント

#### GET /emails
- 最新のメールを取得
- クエリパラメータ：
  - `limit`: 取得件数（デフォルト10）
  - `folder`: メールボックス（デフォルトINBOX）

#### GET /health
- ヘルスチェック用エンドポイント
- IMAP接続の状態確認

#### GET /
- API情報の表示

## データモデル

### EmailMessage
```python
{
  "id": int,              # メールID
  "subject": str,         # 件名
  "from": str,            # 送信者
  "date": str,            # 送信日時
  "body": str,            # 本文（プレーンテキスト）
  "snippet": str          # 本文の冒頭（100文字程度）
}
```

### EmailResponse
```python
{
  "count": int,           # 取得件数
  "emails": List[EmailMessage]
}
```

## エラーハンドリング
- IMAP接続エラー
- 認証エラー
- メール取得エラー

## セキュリティ
- パスワードをログに出力しない
- 環境変数での認証情報管理
- HTTPS/TLS通信の強制

## 実装のポイント

### 1. pydantic-settings で環境変数管理
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    icloud_email: str
    icloud_password: str
    imap_server: str = "imap.mail.me.com"
    imap_port: int = 993
```

### 2. imapclient でIMAP接続
```python
from imapclient import IMAPClient

with IMAPClient(server, ssl=True) as client:
    client.login(email, password)
    client.select_folder('INBOX')
    messages = client.search(['NOT', 'DELETED'])
```

### 3. メール本文の取得
- multipart メールの処理
- HTML/プレーンテキストの選択
- 文字エンコーディングの処理

## ディレクトリ構成（最終）

```
email-service/
├── Dockerfile
├── requirements.txt
├── main.py           ← これから作成
└── .env.example      ← サンプル環境変数ファイル（後で作成）
```
