# Dify + Gmail Email Service

Dify（AIワークフロープラットフォーム）とカスタムメールサービスを組み合わせたプロジェクト。
AIエージェントがGmailからメールを取得・表示できます。

## 概要

```
User → Dify Agent → Email Service → Gmail (IMAP)
         ↓
    「最新のメール見せて」
         ↓
    メール内容を表示
```

## 必要なもの

- Docker / Docker Compose
- Gmailアカウント（2段階認証 + アプリパスワード）
- OpenAI APIキー（または他のLLMプロバイダー）

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/42Tokyonaokix/dify_app.git
cd dify_app
```

### 2. 環境変数を設定

```bash
cp .env.example .env
```

`.env` を編集：

```env
# Gmail設定
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# データベース
POSTGRES_PASSWORD=your-secure-password

# Redis
REDIS_PASSWORD=your-redis-password

# Dify
SECRET_KEY=your-secret-key
WEAVIATE_API_KEY=your-weaviate-key
```

### 3. Gmailアプリパスワードを取得

1. [Googleアカウント](https://myaccount.google.com/) にアクセス
2. セキュリティ → 2段階認証を有効化
3. アプリパスワード → 「メール」用に生成
4. 16文字のパスワードを `.env` にコピー

### 4. 起動

```bash
docker compose up -d
```

### 5. 動作確認

| URL | 説明 |
|-----|------|
| http://localhost:3000 | Dify Studio（管理画面） |
| http://localhost:8002/docs | Email Service API |
| http://localhost:8002/health | ヘルスチェック |

## Dify Agentのセットアップ

### カスタムツールを登録

1. http://localhost:3000 にアクセス
2. 「ツール」→「カスタムツール」→「作成」
3. `dify-apps/README.md` のOpenAPIスキーマを貼り付け
4. 保存

### Agentアプリをインポート

1. 「スタジオ」→「アプリを作成」→「DSLファイルをインポート」
2. `dify-apps/email_return.yml` をアップロード
3. インポート後、ツール設定で `getEmails` を追加
4. OpenAI等のモデルを設定

### 使ってみる

プレビューで入力：
```
最新のメールを5件見せて
```

## アーキテクチャ

```
┌─────────────────────────────────────────────────┐
│                  Nginx (80)                     │
└─────────────────────────────────────────────────┘
                │               │
        ┌───────┘               └───────┐
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│  Dify Web     │               │   Dify API    │
│   (3000)      │               │    (5001)     │
└───────────────┘               └───────────────┘
                                        │
        ┌───────────┬───────────┬───────┴───────┐
        ▼           ▼           ▼               ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ PostgreSQL│ │   Redis   │ │ Weaviate  │ │  Email    │
│  (5432)   │ │  (6379)   │ │  (8080)   │ │  Service  │
└───────────┘ └───────────┘ └───────────┘ │  (8002)   │
                                          └───────────┘
                                                │
                                                ▼
                                          ┌───────────┐
                                          │   Gmail   │
                                          │   IMAP    │
                                          └───────────┘
```

## サービス一覧

| サービス | ポート | 説明 |
|----------|--------|------|
| Nginx | 80 | リバースプロキシ |
| Dify Web | 3000 | 管理コンソール |
| Dify API | 5001 | バックエンドAPI |
| PostgreSQL | 5432 | データベース |
| Redis | 6379 | キャッシュ |
| Weaviate | 8080 | ベクトルDB |
| Email Service | 8002 | メール取得API |

## Email Service API

| エンドポイント | 説明 |
|---------------|------|
| `GET /` | API情報 |
| `GET /health` | ヘルスチェック |
| `GET /emails?limit=10&folder=INBOX` | メール取得 |

### パラメータ

| パラメータ | デフォルト | 範囲 | 説明 |
|-----------|-----------|------|------|
| `limit` | 10 | 1-100 | 取得件数 |
| `folder` | INBOX | - | フォルダ名 |

## コマンド

```bash
# 起動
docker compose up -d

# 停止
docker compose down

# ログ確認
docker compose logs -f email-service

# 再ビルド
docker compose up -d --build email-service
```

## ファイル構成

```
dify_app/
├── README.md
├── AGENTS.md               # 詳細ドキュメント
├── docker-compose.yml
├── .env.example
│
├── email-service/          # メール取得API
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── routes/
│   └── services/
│
├── dify-apps/              # Difyアプリ
│   ├── email_return.yml    # Agentエクスポート
│   └── README.md           # インポート手順
│
└── nginx/
    └── nginx.conf
```

## 技術スタック

- **Dify**: AIワークフロープラットフォーム
- **FastAPI**: Email Service API
- **IMAPClient**: Gmail接続
- **PostgreSQL**: メインDB
- **Redis**: キャッシュ・キュー
- **Weaviate**: ベクトルDB
- **Docker Compose**: コンテナオーケストレーション

## ライセンス

MIT
