# main.py 一行ずつ解説

## 全体構成

main.pyは以下の5つのパートで構成されています：
1. **インポート** (1-12行目)
2. **設定クラス** (14-31行目)
3. **データモデル** (33-56行目)
4. **ユーティリティ関数** (64-128行目)
5. **APIエンドポイント** (130-254行目)

---

## 1. インポート部分 (1-12行目)

```python
"""
Gmail Email Service API
IMAPでGmailを取得し、REST APIとして提供
"""
```
→ **ドキュメンテーション文字列（docstring）**: このファイルが何をするか説明

```python
from fastapi import FastAPI, HTTPException, Query
```
→ **FastAPI**: PythonのWebフレームワーク（APIを簡単に作れる）
- `FastAPI`: アプリケーション本体
- `HTTPException`: エラーを返すときに使う（例: 500 Internal Server Error）
- `Query`: URLパラメータの定義（例: `/emails?limit=10`）

```python
from pydantic import BaseModel, Field
```
→ **Pydantic**: データの型チェックと変換を行うライブラリ
- `BaseModel`: データの形を定義するベースクラス
- `Field`: フィールドの詳細設定（デフォルト値、説明など）

```python
from pydantic_settings import BaseSettings
```
→ **BaseSettings**: 環境変数から設定を読み込むクラス

```python
from typing import List, Optional
```
→ **型ヒント**: 変数の型を明示するためのもの
- `List`: リスト型（例: `List[str]` = 文字列のリスト）
- `Optional`: Noneを許容する（例: `Optional[str]` = 文字列 or None）

```python
import email
from email.header import decode_header
```
→ **email**: Pythonの標準ライブラリでメールを解析
- `decode_header`: 日本語などの件名をデコード

```python
from imapclient import IMAPClient
```
→ **IMAPClient**: IMAPサーバーに接続してメールを取得するライブラリ

```python
import logging
```
→ **logging**: ログ出力（デバッグや監視用）

---

## 2. ロギング設定 (14-16行目)

```python
logging.basicConfig(level=logging.INFO)
```
→ ログレベルをINFOに設定（DEBUG < INFO < WARNING < ERROR）

```python
logger = logging.getLogger(__name__)
```
→ このファイル用のロガーを取得
- `__name__`: このファイルの名前（"main"）

---

## 3. 設定クラス (18-31行目)

```python
class Settings(BaseSettings):
```
→ `BaseSettings`を継承して設定クラスを定義
→ 環境変数から自動的に値を読み込む

```python
    """環境変数からの設定読み込み"""
    gmail_email: str = Field(default="your-email@gmail.com")
```
→ `gmail_email`という文字列型の設定項目
→ 環境変数 `GMAIL_EMAIL` から読み込む（なければデフォルト値）

```python
    gmail_app_password: str = Field(default="your-app-password")
    imap_server: str = Field(default="imap.gmail.com")
    imap_port: int = Field(default=993)
```
→ 同様に他の設定項目を定義

```python
    class Config:
        env_file = ".env"
        case_sensitive = False
```
→ 設定の設定（メタ設定）
- `env_file = ".env"`: .envファイルからも読み込む
- `case_sensitive = False`: 大文字小文字を区別しない

```python
settings = Settings()
```
→ 設定クラスのインスタンスを作成（ここで環境変数が読み込まれる）

---

## 4. データモデル (33-56行目)

### EmailMessage（1通のメール）

```python
class EmailMessage(BaseModel):
    """メールメッセージのデータモデル"""
    id: int
    subject: str
    sender: str = Field(alias="from")
```
→ メール1通のデータ構造を定義
→ `alias="from"`: JSONでは"from"というキー名を使う（Pythonの予約語なので）

```python
    date: str
    body: str
    snippet: str
```
→ 日付、本文、本文の抜粋

```python
    class Config:
        populate_by_name = True
```
→ エイリアス名でも元の名前でも値を設定可能

### EmailResponse（レスポンス全体）

```python
class EmailResponse(BaseModel):
    count: int
    emails: List[EmailMessage]
```
→ APIのレスポンス形式
→ メール件数と、メールのリスト

### HealthResponse（ヘルスチェック）

```python
class HealthResponse(BaseModel):
    status: str
    imap_server: str
    connected: bool
```
→ サービスの状態を返す形式

---

## 5. FastAPIアプリケーション作成 (57-62行目)

```python
app = FastAPI(
    title="Gmail Email Service",
    description="IMAPでGmailを取得するREST API",
    version="1.0.0"
)
```
→ FastAPIアプリケーションを作成
→ `/docs` で自動生成されるドキュメントに表示される情報

---

## 6. ユーティリティ関数 (64-128行目)

### decode_mime_header（ヘッダーのデコード）

```python
def decode_mime_header(header_value: str) -> str:
```
→ 関数の定義。引数は文字列、戻り値も文字列

```python
    if not header_value:
        return ""
```
→ 空の場合は空文字を返す（ガード句）

```python
    decoded_parts = decode_header(header_value)
```
→ MIMEエンコードされたヘッダーをデコード
→ 例: `=?UTF-8?B?44GT44KT44Gr44Gh44Gv?=` → `こんにちは`

```python
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded_string += part
```
→ デコード結果を結合
→ バイト列なら文字列にデコード

### get_email_body（本文取得）

```python
def get_email_body(msg) -> str:
```
→ メールオブジェクトから本文を取得

```python
    if msg.is_multipart():
```
→ マルチパートメール（HTML + テキストなど複数形式を含む）かチェック

```python
        for part in msg.walk():
```
→ メールの各パートを順番に処理

```python
            if "attachment" in content_disposition:
                continue
```
→ 添付ファイルはスキップ

```python
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
```
→ プレーンテキストを優先して取得

### connect_imap（IMAP接続）

```python
def connect_imap() -> IMAPClient:
```
→ IMAPサーバーに接続する関数

```python
    client = IMAPClient(settings.imap_server, port=settings.imap_port, ssl=True)
```
→ SSL接続でIMAPクライアントを作成

```python
    client.login(settings.gmail_email, settings.gmail_app_password)
```
→ ログイン

```python
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IMAP connection failed: {str(e)}")
```
→ 失敗したら500エラーを返す

---

## 7. APIエンドポイント (130-228行目)

### ルートエンドポイント（/）

```python
@app.get("/", tags=["Info"])
```
→ デコレータ: GETリクエストで"/"にアクセスしたときにこの関数を実行
→ `tags`: ドキュメントでのグループ分け

```python
async def root():
```
→ 非同期関数（asyncio）として定義

### ヘルスチェック（/health）

```python
@app.get("/health", response_model=HealthResponse, tags=["Health"])
```
→ `response_model`: レスポンスの形式を指定（自動バリデーション）

```python
    with connect_imap() as client:
```
→ `with`文: 接続を自動的に閉じる（コンテキストマネージャー）

### メール取得（/emails）

```python
@app.get("/emails", response_model=EmailResponse, tags=["Emails"])
async def get_emails(
    limit: int = Query(default=10, ge=1, le=100, description="取得するメール件数"),
    folder: str = Query(default="INBOX", description="メールボックス名")
):
```
→ クエリパラメータを定義
- `ge=1, le=100`: 1以上100以下のバリデーション
- URLは `/emails?limit=10&folder=INBOX` のようになる

```python
    client.select_folder(folder, readonly=True)
```
→ メールボックスを選択（読み取り専用）

```python
    messages = client.search(['NOT', 'DELETED'])
```
→ 削除済み以外のメールIDを検索

```python
    latest_messages = messages[-limit:]
```
→ リストの最後からlimit件を取得（最新のメール）

```python
    fetch_data = client.fetch(latest_messages, ['RFC822'])
```
→ メールの全データを取得

```python
    msg = email.message_from_bytes(raw_email)
```
→ 生データをメールオブジェクトにパース

---

## 8. ライフサイクルイベント (230-250行目)

```python
@app.on_event("startup")
async def startup_event():
```
→ アプリ起動時に実行される処理

```python
@app.on_event("shutdown")
async def shutdown_event():
```
→ アプリ終了時に実行される処理

---

## 9. メイン実行 (252-254行目)

```python
if __name__ == "__main__":
```
→ このファイルを直接実行した場合のみ実行

```python
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```
→ uvicornサーバーを起動
- `"main:app"`: mainモジュールのappを使う
- `host="0.0.0.0"`: 全IPから接続可能
- `port=8000`: ポート8000で起動
- `reload=True`: コード変更時に自動再起動

---

## APIの呼び出しフロー

```
ブラウザ/Dify
    │
    ▼ GET /emails?limit=5
┌──────────────────────────────┐
│ FastAPI (main.py)            │
│   1. get_emails() が呼ばれる  │
│   2. connect_imap() で接続    │
│   3. メールを取得・パース      │
│   4. EmailResponse を返す     │
└──────────────────────────────┘
    │
    ▼ JSON レスポンス
{
  "count": 5,
  "emails": [...]
}
```
