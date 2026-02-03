# Gmail 対応 & OpenAI API キー設定ガイド

## ✅ Gmail 対応完了

以下のファイルを Gmail 用に書き換えました：

### 変更内容

1. **email-service/main.py**
   - `ICLOUD_EMAIL` → `GMAIL_EMAIL`
   - `ICLOUD_PASSWORD` → `GMAIL_APP_PASSWORD`
   - IMAP サーバー: `imap.mail.me.com` → `imap.gmail.com`

2. **email-service/.env.example**
   - Gmail 用の環境変数サンプルに更新

3. **docker-compose.yml**
   - email-service の環境変数を Gmail 用に変更
   - ポート: 8002:8000（ポート競合を回避）

## Gmail アプリパスワードの取得方法

### 1. 2段階認証プロセスを有効化

1. https://myaccount.google.com にアクセス
2. 左メニューから「セキュリティ」を選択
3. 「Googleへのログイン」セクションで「2段階認証プロセス」をクリック
4. 画面の指示に従って2段階認証を有効化

### 2. アプリパスワードを生成

1. 2段階認証が有効な状態で、再び「セキュリティ」ページへ
2. 「Googleへのログイン」セクション内の「アプリパスワード」をクリック
3. 「アプリを選択」→「その他（カスタム名）」を選択
4. 名前を入力（例：「Dify Email Service」）
5. 「生成」をクリック
6. 表示された16文字のパスワードをコピー（スペースなし）

### 3. .env ファイルに設定

プロジェクトルートに `.env` ファイルを作成:

```bash
cd /home/naoki/dify_app
nano .env
```

内容:
```env
# Gmail 設定
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop

# OpenAI API キー（後述）
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

## 🤖 OpenAI API キーの設定方法

OpenAI API キーは、Dify が AI モデルを使用するために必要です。

### 方法1: docker-compose.yml で設定（推奨）

#### ステップ1: .env ファイルに追加

```env
# OpenAI API キー
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

#### ステップ2: docker-compose.yml を編集

`api` サービスと `worker` サービスの `environment` セクションに追加します。

現在の docker-compose.yml を確認してから、以下を追加する場所を教えます：

```yaml
api:
  environment:
    # ... 既存の環境変数 ...

    # OpenAI API設定（追加）
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    OPENAI_API_BASE: https://api.openai.com/v1

worker:
  environment:
    # ... 既存の環境変数 ...

    # OpenAI API設定（追加）
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    OPENAI_API_BASE: https://api.openai.com/v1
```

### 方法2: Dify Web UI で設定（簡単）

Docker Compose でDifyを起動した後、Web UIから設定できます：

1. Dify にアクセス: http://localhost （または http://localhost:80）
2. アカウント作成・ログイン
3. 「設定」→「モデルプロバイダー」を選択
4. 「OpenAI」を選択
5. API キーを入力して保存

**メリット**:
- GUI で簡単に設定できる
- 複数のモデルプロバイダーを管理しやすい
- API キーをファイルに保存しなくて良い

**推奨**: まず方法2で試して、動作確認してから方法1に移行するのが良いでしょう。

## 📧 Gmail Email Service の起動方法

### 1. .env ファイルを作成

```bash
cd /home/naoki/dify_app

# .env.example をコピー（存在する場合）
cp email-service/.env.example .env

# または新規作成
nano .env
```

内容:
```env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### 2. Docker Compose で起動

```bash
# email-service だけを起動
docker compose up -d email-service

# または全サービスを起動
docker compose up -d
```

### 3. 動作確認

```bash
# ログを確認
docker compose logs -f email-service

# API ドキュメントにアクセス
# http://localhost:8002/docs
```

### 4. メール取得テスト

```bash
# ブラウザまたは curl で確認
curl "http://localhost:8002/emails?limit=5"
```

## Dify から Email Service を呼び出す

Dify のワークフローで HTTP リクエストノードを使用:

```yaml
URL: http://email-service:8000/emails
Method: GET
Query Parameters:
  limit: 10
  folder: INBOX
```

**注意**: Docker ネットワーク内では `email-service:8000` を使用します（`localhost:8002` ではない）。

## トラブルシューティング

### Gmail 接続エラー

**エラー**: "IMAP connection failed"

**原因と対処**:
1. 2段階認証が有効でない → 有効化してください
2. アプリパスワードが間違っている → 再生成してください
3. IMAP が無効 → Gmail 設定で IMAP を有効化

### Gmail で IMAP を有効化

1. Gmail にログイン
2. 右上の歯車アイコン →「すべての設定を表示」
3. 「メール転送と POP/IMAP」タブ
4. 「IMAP を有効にする」を選択
5. 「変更を保存」

### OpenAI API エラー

**エラー**: "Invalid API key"

**対処**:
1. API キーが正しいか確認（`sk-proj-` で始まる）
2. API キーにスペースや改行が入っていないか確認
3. OpenAI アカウントに請求情報が登録されているか確認

## セキュリティ上の注意

### .env ファイルの管理

**.gitignore に追加**:
```bash
echo ".env" >> .gitignore
```

これで `.env` ファイルが Git にコミットされるのを防ぎます。

### パスワードの保護

- `.env` ファイルのパーミッションを制限:
  ```bash
  chmod 600 .env
  ```

- Docker イメージにパスワードを含めない（環境変数で渡す）

## 次のステップ

1. ✅ Gmail アプリパスワードを取得
2. ✅ .env ファイルを作成
3. ✅ Docker Compose で起動
4. 📝 OpenAI API キーを Dify Web UI で設定
5. 🚀 Dify でワークフローを作成
6. 📧 Email Service を Dify から呼び出す

## まとめ

### Email Service（Gmail）

- **アクセス**: http://localhost:8002/docs
- **環境変数**: `GMAIL_EMAIL`, `GMAIL_APP_PASSWORD`
- **Docker内**: `http://email-service:8000`

### OpenAI API

- **設定方法1**: docker-compose.yml の環境変数
- **設定方法2**: Dify Web UI（推奨）
- **環境変数**: `OPENAI_API_KEY`

### Dify

- **アクセス**: http://localhost （または http://localhost:80）
- **初回**: アカウント作成が必要
- **OpenAI設定**: Web UI の「モデルプロバイダー」から
