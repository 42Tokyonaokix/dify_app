# AGENTS.md

## プロジェクト概要

### Dify + Gmail Email Service

Dify（AIワークフロープラットフォーム）とカスタムメールサービスを組み合わせた構成。
Docker Composeで複数コンテナを連携し、AIエージェントがメールを取得・表示する。

### アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                        User                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Nginx (Port 80)                           │
└─────────────────────────────────────────────────────────────┘
                    │                   │
         ┌──────────┘                   └──────────┐
         ▼                                         ▼
┌─────────────────┐                    ┌─────────────────────┐
│  Dify Web       │                    │     Dify API        │
│  (Port 3000)    │                    │    (Port 5001)      │
│  管理コンソール  │                    │  ワークフロー実行   │
└─────────────────┘                    └─────────────────────┘
                                                  │
         ┌────────────────┬───────────────────────┼────────────┐
         ▼                ▼                       ▼            ▼
┌──────────────┐  ┌──────────────┐    ┌─────────────┐    ┌───────────┐
│  PostgreSQL  │  │    Redis     │    │  Weaviate   │    │  Email    │
│  (5432)      │  │   (6379)     │    │   (8080)    │    │  Service  │
└──────────────┘  └──────────────┘    └─────────────┘    │  (8002)   │
                                                         └───────────┘
                                                               │
                                                               ▼
                                                         ┌───────────┐
                                                         │   Gmail   │
                                                         │   IMAP    │
                                                         └───────────┘
```

---

## サービス一覧

| サービス | ポート | 説明 |
|----------|--------|------|
| Nginx | 80 | リバースプロキシ |
| Dify Web | 3000 | 管理コンソール（Studio） |
| Dify API | 5001 | バックエンドAPI |
| PostgreSQL | 5432 | メインDB |
| Redis | 6379 | キャッシュ・キュー |
| Weaviate | 8080 | ベクトルDB |
| Email Service | 8002 | Gmail取得API |

---

## Email Service

### 仕様

- **場所**: `email-service/`
- **技術**: FastAPI + IMAPClient + Pydantic
- **ポート**: 外部 8002 → 内部 8000

### APIエンドポイント

| エンドポイント | 説明 |
|--------------|------|
| GET / | API情報 |
| GET /health | IMAP接続状態チェック |
| GET /emails?limit=10&folder=INBOX | メール取得（1-100件） |

### 環境変数

```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=16文字のアプリパスワード
```

### Difyからの呼び出し

```yaml
URL: http://email-service:8000/emails  # Docker内部ネットワーク
Method: GET
Query: limit=10, folder=INBOX
```

---

## Dify Apps

### エクスポート済みアプリ

| ファイル | タイプ | 説明 |
|---------|--------|------|
| `dify-apps/email_return.yml` | Agent | メール取得エージェント |

### インポート方法

1. `http://localhost:3000` にアクセス
2. 「アプリを作成」→「DSLファイルをインポート」
3. `dify-apps/email_return.yml` をアップロード
4. カスタムツール（email-service）を再設定

詳細は `dify-apps/README.md` を参照。

### Difyアプリタイプ比較

| タイプ | 用途 | ツール | 会話履歴 |
|--------|------|:------:|:--------:|
| Chatbot | 対話 | ❌ | ✅ |
| **Agent** | 自律タスク | ✅ | ✅ |
| Text Generator | 単発生成 | ❌ | ❌ |
| Workflow | 複雑フロー | ✅ | 選択可 |

**本プロジェクトではAgentを採用**（ツール使用 + 対話形式）

---

## 重要ファイル

| ファイル | 説明 |
|---------|------|
| docker-compose.yml | 全サービス定義 |
| .env | 認証情報（Git管理外） |
| email-service/main.py | メールAPI実装 |
| dify-apps/email_return.yml | Agentアプリ定義 |
| nginx/nginx.conf | リバースプロキシ設定 |

---

## 起動コマンド

```bash
# 全サービス起動
docker compose up -d

# email-serviceのみ
docker compose up -d email-service

# ログ確認
docker compose logs -f email-service

# 停止
docker compose down
```

---

## Gmail設定手順

1. Googleアカウントで2段階認証を有効化
2. アプリパスワードを生成（16文字）
3. Gmail設定でIMAPを有効化
4. `.env`ファイルに認証情報を設定

---

## 詳細ドキュメント

`claude_output/` 内:

| ファイル | 内容 |
|---------|------|
| 01_docker構成解説.md | Docker Compose詳細 |
| 04_main.py設計.md | API設計方針 |
| 05_main.py実装解説.md | 実装詳細 |
| 06_Gmail対応とOpenAI_API設定.md | 認証設定ガイド |
| 08_main.py一行解説.md | コード解説 |
| 09_Difyアプリタイプ比較.md | 4タイプの比較 |
| 11_プロジェクト進捗サマリー.md | 全体進捗 |

---

## LangChainとの対応

| LangChain | Dify |
|-----------|------|
| Agent + Tools | Agent |
| Chain / LCEL | Workflow |
| Memory | 両方に内蔵 |

Difyでの構築はLangChain学習の予行練習として有効。

---

## AGENT向け指示

- 解説や分析内容は `claude_output/` に出力する
- ファイル先頭に昇順の数値を付け、最新がわかるようにする
- 機密情報（APIキー、パスワード等）は絶対にコミットしない
- `.env.example` をテンプレートとして維持する
