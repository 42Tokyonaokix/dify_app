# main.py 実装解説

## 作成したファイル
`/home/naoki/dify_app/email-service/main.py`

## コード構成

### 1. 設定管理（Settings クラス）

```python
class Settings(BaseSettings):
    icloud_email: str = Field(default="your-email@icloud.com")
    icloud_password: str = Field(default="your-app-specific-password")
    imap_server: str = Field(default="imap.mail.me.com")
    imap_port: int = Field(default=993)
```

**役割**: 環境変数から iCloud 認証情報を読み込む

**環境変数**:
- `ICLOUD_EMAIL`: iCloud メールアドレス
- `ICLOUD_PASSWORD`: アプリ固有パスワード
- `IMAP_SERVER`: IMAPサーバー（デフォルト: imap.mail.me.com）
- `IMAP_PORT`: IMAPポート（デフォルト: 993）

### 2. データモデル

#### EmailMessage
```python
class EmailMessage(BaseModel):
    id: int              # メールID
    subject: str         # 件名
    sender: str          # 送信者
    date: str            # 送信日時
    body: str            # 本文（全文）
    snippet: str         # 本文の冒頭100文字
```

#### EmailResponse
```python
class EmailResponse(BaseModel):
    count: int           # 取得件数
    emails: List[EmailMessage]  # メール一覧
```

### 3. ユーティリティ関数

#### decode_mime_header()
- MIMEエンコードされたヘッダー（件名、送信者名）をデコード
- 日本語などの非ASCII文字を正しく表示

#### get_email_body()
- マルチパート/シンプルメールの両方に対応
- プレーンテキスト優先（HTMLはバックアップ）
- 添付ファイルをスキップ

#### connect_imap()
- IMAPサーバーに接続・認証
- SSL/TLS通信
- エラー時は HTTPException を発生

### 4. API エンドポイント

#### GET /
基本情報を返す。

**レスポンス例**:
```json
{
  "service": "iCloud Email Service",
  "version": "1.0.0",
  "endpoints": {
    "/emails": "Get latest emails",
    "/health": "Health check"
  }
}
```

#### GET /health
IMAP接続の状態をチェック。

**レスポンス例**:
```json
{
  "status": "healthy",
  "imap_server": "imap.mail.me.com",
  "connected": true
}
```

#### GET /emails
最新のメールを取得。

**クエリパラメータ**:
- `limit`: 取得件数（1-100、デフォルト10）
- `folder`: メールボックス名（デフォルト "INBOX"）

**リクエスト例**:
```bash
curl "http://localhost:8000/emails?limit=5"
```

**レスポンス例**:
```json
{
  "count": 5,
  "emails": [
    {
      "id": 12345,
      "subject": "会議の件",
      "sender": "Taro Yamada <taro@example.com>",
      "date": "Mon, 03 Feb 2026 10:30:00 +0900",
      "body": "明日の会議についてですが...",
      "snippet": "明日の会議についてですが..."
    }
  ]
}
```

## ローカルでテストする方法

### 1. 必要なパッケージをインストール

```bash
cd /home/naoki/dify_app/email-service
pip install -r requirements.txt
```

### 2. 環境変数を設定

```bash
export ICLOUD_EMAIL="your-email@icloud.com"
export ICLOUD_PASSWORD="your-app-specific-password"
```

または `.env` ファイルを作成:

```env
ICLOUD_EMAIL=your-email@icloud.com
ICLOUD_PASSWORD=your-app-specific-password
```

### 3. サーバーを起動

```bash
python main.py
```

または

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. ブラウザでアクセス

- API ドキュメント: http://localhost:8000/docs
- 基本情報: http://localhost:8000/
- ヘルスチェック: http://localhost:8000/health
- メール取得: http://localhost:8000/emails?limit=5

## Docker でテストする方法

### 1. .env ファイルを作成

プロジェクトルートに `.env` ファイルを作成:

```bash
cd /home/naoki/dify_app
nano .env
```

内容:
```env
ICLOUD_EMAIL=your-email@icloud.com
ICLOUD_PASSWORD=your-app-specific-password
```

### 2. Docker Compose で起動

```bash
docker compose up -d email-service
```

### 3. ログを確認

```bash
docker compose logs -f email-service
```

### 4. アクセス

http://localhost:8000/docs

## iCloud アプリ固有パスワードの取得方法

1. https://appleid.apple.com にサインイン
2. 「セキュリティ」セクションへ移動
3. 「アプリ用パスワード」を生成
4. 生成されたパスワードを `ICLOUD_PASSWORD` に設定

**注意**: 通常の Apple ID パスワードではなく、アプリ固有パスワードが必要です。

## Dify から呼び出す方法

Dify のワークフローで HTTP リクエストノードを使用:

```yaml
URL: http://email-service:8000/emails
Method: GET
Query Parameters:
  limit: 10
```

レスポンスの `emails` 配列から必要な情報を取得できます。

## セキュリティ上の注意

1. **パスワードをハードコードしない**
   - 必ず環境変数を使用
   - `.env` ファイルを `.gitignore` に追加

2. **本番環境では**
   - HTTPS を使用
   - API キー認証を追加（将来の拡張）
   - レート制限を実装

3. **ログ**
   - パスワードをログに出力しない
   - 現在の実装では安全に処理されています

## トラブルシューティング

### "IMAP connection failed"
- iCloud メールアドレスが正しいか確認
- アプリ固有パスワードを使用しているか確認
- 2ファクタ認証が有効になっているか確認

### "Authentication failed"
- アプリ固有パスワードを再生成
- メールアドレスにスペースなど余計な文字がないか確認

### "Failed to decode"
- 一部のメールは文字エンコーディングが特殊な場合があります
- その場合はスキップされ、他のメールは正常に取得されます

## 今後の拡張案

1. **メール送信機能**: SMTP を使った送信
2. **フィルタリング**: 送信者、日付、キーワードでフィルタ
3. **添付ファイル**: 添付ファイルのダウンロード
4. **複数アカウント**: 複数の iCloud アカウントに対応
5. **キャッシング**: Redis を使った結果のキャッシュ
6. **認証**: API キーによるアクセス制御

## ファイル構成（完成）

```
email-service/
├── Dockerfile           ✅ 作成済み
├── requirements.txt     ✅ 作成済み
├── main.py             ✅ 作成済み
└── .env.example        📝 次に作成すると良い
```
