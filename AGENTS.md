# CLAUDE.md

## プロジェクト概要

### Dify + Gmail Email Service

Dify（AIワークフロープラットフォーム）とカスタムメールサービスを組み合わせた構成。
Docker Composeで複数コンテナを連携。

### アーキテクチャ

```
Nginx (Port 80) ─── Dify Web (Port 3000)
       │
       └── Dify API (Port 5001) ─── PostgreSQL / Redis / Weaviate
       │
       └── Email Service (Port 8002) ─── Gmail (IMAP)
```

### Email Service 仕様

- **場所**: `email-service/`
- **技術**: FastAPI + IMAPClient + Pydantic
- **ポート**: 外部 8002 → 内部 8000

#### APIエンドポイント

| エンドポイント | 説明 |
|--------------|------|
| GET / | API情報 |
| GET /health | IMAP接続状態チェック |
| GET /emails?limit=10&folder=INBOX | メール取得 |

#### 環境変数

```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=16文字のアプリパスワード
```

#### Difyからの呼び出し

```yaml
URL: http://email-service:8000/emails  # Docker内部
Method: GET
Query: limit=10, folder=INBOX
```

### 重要ファイル

| ファイル | 説明 |
|---------|------|
| docker-compose.yml | 全サービス定義 |
| email-service/main.py | メールAPI実装 |
| email-service/Dockerfile | コンテナビルド設定 |
| email-service/requirements.txt | Python依存関係 |
| nginx/nginx.conf | リバースプロキシ設定 |
| .env | 認証情報（Git管理外） |

### Gmail設定手順

1. Googleアカウントで2段階認証を有効化
2. アプリパスワードを生成（16文字）
3. Gmail設定でIMAPを有効化
4. `.env`ファイルに認証情報を設定

### 起動コマンド

```bash
# email-serviceのみ
docker compose up -d email-service

# 全サービス
docker compose up -d

# ログ確認
docker compose logs -f email-service
```

### 詳細ドキュメント

`claude_output/` 内に詳細な解説あり:
- 01: Docker構成解説
- 04: main.py設計
- 05: main.py実装解説
- 06: Gmail対応とOpenAI API設定ガイド
- 08: main.py一行解説

---

## AGENT向け指示
- 解説や分析内容は、 "claude_output/" に出力する。
- claude_output/ 内に出力する際は、ファイル先頭に昇順の数値を付け、どれが最新かわかるようにする。
