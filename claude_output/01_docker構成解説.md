# Docker構成の解説

## 概要

このプロジェクトは、Dify（AI開発プラットフォーム）とカスタムメールサービスを組み合わせた構成です。
Docker Composeを使用して、複数のコンテナを連携させています。

---

## docker-compose.yml 全体構成

### サービス構成図

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                      │
│              リバースプロキシ・ルーティング              │
└─────────────────────────────────────────────────────────┘
                    │                  │
         ┌──────────┴────────┐    ┌───┴──────┐
         │                   │    │          │
    ┌────▼─────┐      ┌──────▼────▼─┐  ┌────▼──────────┐
    │ Dify Web │      │  Dify API   │  │ Email Service │
    │(Port 3000)│      │ (Port 5001) │  │  (Port 8000)  │
    └──────────┘      └──────┬──────┘  └───────────────┘
                             │
                      ┌──────┴─────┐
                      │            │
              ┌───────▼──┐   ┌─────▼─────┐
              │Dify Worker│   │PostgreSQL │
              │           │   │(Port 5432)│
              └─────┬─────┘   └───────────┘
                    │
        ┌───────────┴──────────┬─────────────┐
        │                      │             │
   ┌────▼─────┐        ┌──────▼───┐   ┌─────▼────┐
   │  Redis   │        │ Weaviate │   │ Volumes  │
   │(Port 6379)│        │(Port 8080)│   │(永続化)  │
   └──────────┘        └──────────┘   └──────────┘
```

---

## 各サービスの詳細解説

### 1. PostgreSQL (db)
**ファイル位置**: docker-compose.yml:6-23

#### 役割
- Difyのメインデータベース
- ユーザー情報、ワークフロー設定、会話履歴を保存

#### 主要設定
```yaml
image: postgres:15-alpine  # 軽量版Alpine Linux
環境変数:
  - POSTGRES_USER: dify
  - POSTGRES_PASSWORD: dify_password  # 本番環境では変更必須
  - POSTGRES_DB: dify
  - PGDATA: データ保存パス指定
```

#### データ永続化
- `./volumes/db/data:/var/lib/postgresql/data`
- ホストの `volumes/db/data` にデータを保存

#### ヘルスチェック
- `pg_isready -U dify` で接続確認
- 10秒ごとにチェック、5回失敗で異常判定

---

### 2. Redis (redis)
**ファイル位置**: docker-compose.yml:25-40

#### 役割
- キャッシュとセッション管理
- API呼び出しのキャッシュ
- Celeryタスクキュー（バックグラウンドジョブ用）

#### 主要設定
```yaml
image: redis:7-alpine
command: redis-server --requirepass YOUR_REDIS_PASSWORD
```

#### 使用箇所
1. APIサービスの一時データ保存
2. Celeryのブローカー（タスク配信）
3. メールサービスのキャッシュ（depends_onで指定）

---

### 3. Weaviate (weaviate)
**ファイル位置**: docker-compose.yml:42-57

#### 役割
- ベクトルデータベース
- ナレッジベース機能
- RAG（検索拡張生成）に使用

#### 主要設定
```yaml
image: semitechnologies/weaviate:1.19.0
環境変数:
  - DEFAULT_VECTORIZER_MODULE: 'none'  # 外部ベクトル化を使用
  - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'  # 認証なしアクセス許可
```

#### ユースケース
- ドキュメントの意味検索
- LLMへのコンテキスト提供

---

### 4. Dify API (api)
**ファイル位置**: docker-compose.yml:59-107

#### 役割
- バックエンドのコアサービス
- ワークフロー実行
- LLM統合
- データ処理

#### 重要な環境変数
```yaml
MODE: api  # APIモードで起動
SECRET_KEY: YOUR_SECRET_KEY  # 本番環境では変更必須

# データベース接続
DB_HOST: db
DB_PORT: 5432

# Redis接続
CELERY_BROKER_URL: redis://:YOUR_REDIS_PASSWORD@redis:6379/1

# ベクトルDB接続
VECTOR_STORE: weaviate
WEAVIATE_ENDPOINT: http://weaviate:8080

# ストレージ
STORAGE_TYPE: local
STORAGE_LOCAL_PATH: /app/storage
```

#### 依存関係
- `depends_on` で db と redis の起動を待機
- `service_healthy` 条件でヘルスチェック完了を確認

#### ボリュームマウント
- `./volumes/app/storage:/app/storage`
- アップロードファイルやモデルデータを永続化

---

### 5. Dify Worker (worker)
**ファイル位置**: docker-compose.yml:109-139

#### 役割
- 非同期タスク処理
- 長時間実行ジョブ
- バックグラウンド処理

#### 主要設定
```yaml
image: langgenius/dify-api:0.6.13  # APIと同じイメージ
MODE: worker  # Workerモードで起動
```

#### 処理内容
- メール送信
- データのインポート/エクスポート
- モデルの微調整
- 定期実行タスク

#### API との違い
- 同じイメージだが `MODE` 環境変数で動作が変わる
- ポート公開なし（外部からアクセスされない）

---

### 6. Dify Web (web)
**ファイル位置**: docker-compose.yml:141-151

#### 役割
- フロントエンドUI
- ブラウザからアクセスするダッシュボード

#### 主要設定
```yaml
image: langgenius/dify-web:0.6.13
環境変数:
  CONSOLE_API_URL: http://localhost:5001
  APP_API_URL: http://localhost:5001
```

#### 技術スタック
- Next.js（推測）
- React ベースの SPA

---

### 7. Nginx (nginx)
**ファイル位置**: docker-compose.yml:153-165

#### 役割
- リバースプロキシ
- フロントエンドとAPIを統合
- ポート80で一元提供

#### 設定マウント
- `./nginx/nginx.conf:/etc/nginx/nginx.conf:ro`
- `:ro` は読み取り専用マウント

#### 依存関係
- API と Web の起動を待機

---

### 8. Email Service (email-service)
**ファイル位置**: docker-compose.yml:167-186

#### 役割
- iCloudメール取得API
- IMAPでメールを取得
- DifyからHTTP経由で呼び出し可能

#### ビルド設定
```yaml
build:
  context: ./email-service
  dockerfile: Dockerfile
```
イメージをプルするのではなく、ローカルでビルド

#### 環境変数
```yaml
ICLOUD_EMAIL: ${ICLOUD_EMAIL:-your-email@icloud.com}
ICLOUD_PASSWORD: ${ICLOUD_PASSWORD:-your-app-specific-password}
IMAP_SERVER: imap.mail.me.com
IMAP_PORT: 993
```
- `${変数名:-デフォルト値}` 構文を使用
- `.env` ファイルから読み込み

#### ボリュームマウント
- `./email-service:/app`
- ホットリロード対応（コード変更を即座に反映）

#### 依存関係
- Redis のみに依存

---

## email-service/Dockerfile 解説

**ファイル位置**: email-service/Dockerfile

### ビルドプロセス

```dockerfile
# ベースイメージ
FROM python:3.11-slim
```
- Python 3.11 の軽量版
- Debian ベース

```dockerfile
# 作業ディレクトリ
WORKDIR /app
```
- コンテナ内の `/app` ディレクトリで作業

```dockerfile
# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
```
- `gcc`: Python パッケージのコンパイルに必要
- `/var/lib/apt/lists/*` 削除でイメージサイズ削減

```dockerfile
# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
- `--no-cache-dir`: pip キャッシュを保存しない（イメージサイズ削減）
- レイヤーキャッシュ活用のため、コード本体より先にインストール

```dockerfile
# アプリケーションコードのコピー
COPY . .
```
- カレントディレクトリの全ファイルをコピー

```dockerfile
# ポート公開
EXPOSE 8000
```
- ドキュメント目的（実際の公開は docker-compose.yml で指定）

```dockerfile
# サーバー起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
- Uvicorn: ASGI サーバー（FastAPI 用）
- `--host 0.0.0.0`: すべてのインターフェースでリッスン
- `--reload`: ファイル変更を検知して自動再起動（開発用）

### 想定される技術スタック
- **FastAPI**: Python の Web フレームワーク
- **Uvicorn**: ASGI サーバー
- **imaplib**: IMAP プロトコル（メール取得）

---

## nginx/nginx.conf 解説

**ファイル位置**: nginx/nginx.conf

### 全体構成

```nginx
user  nginx;
worker_processes  auto;
```
- `auto`: CPU コア数に応じて自動設定

```nginx
events {
    worker_connections  1024;
}
```
- 各ワーカーが同時に処理できる接続数

### HTTP 設定

```nginx
client_max_body_size 15M;
```
- アップロード可能なファイルサイズ上限
- デフォルト 1M から引き上げ

### ルーティング設定

#### 1. フロントエンドへのプロキシ (nginx.conf:31-37)
```nginx
location / {
    proxy_pass http://web:3000;
    ...
}
```
- すべてのパスをフロントエンドへ
- Docker の内部ネットワークで `web:3000` に接続

#### 2. API 呼び出しのプロキシ (nginx.conf:40-48)
```nginx
location /api {
    proxy_pass http://api:5001;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
    ...
}
```
- `/api` パスを Dify API へ
- タイムアウト 300 秒（LLM 処理に時間がかかる可能性）

#### 3. Console API (nginx.conf:51-59)
```nginx
location /console/api {
    proxy_pass http://api:5001;
    ...
}
```
- 管理画面用の API エンドポイント

#### 4. Files エンドポイント (nginx.conf:62-68)
```nginx
location /files {
    proxy_pass http://api:5001;
    ...
}
```
- ファイルアップロード/ダウンロード用

### プロキシヘッダー
すべてのロケーションで以下を設定：
```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```
- クライアント情報をバックエンドに伝達
- ロードバランサー経由でも正しいIPを取得

---

## データフローの例

### メール取得のフロー
1. Dify Web (ブラウザ) → Nginx (Port 80)
2. Nginx → Dify API (Port 5001)
3. Dify API → Email Service (Port 8000, HTTP API)
4. Email Service → iCloud (Port 993, IMAP)
5. 取得したメールを Dify API に返却
6. Dify API → PostgreSQL (保存)
7. Dify API → Weaviate (ベクトル化・保存)

### ワークフロー実行のフロー
1. ユーザーが Dify Web でワークフローを実行
2. Nginx → Dify API
3. Dify API → Worker (Celery 経由でタスク投入)
4. Worker → LLM プロバイダー (OpenAI/Anthropic など)
5. Worker → Weaviate (コンテキスト検索)
6. Worker → Redis (進捗保存)
7. Worker → PostgreSQL (結果保存)

---

## セキュリティ上の注意点

### 本番環境での必須対応

1. **シークレットキーの変更**
   ```yaml
   SECRET_KEY: YOUR_SECRET_KEY
   ```
   ランダムな文字列に変更

2. **パスワードの変更**
   - `POSTGRES_PASSWORD`
   - `REDIS_PASSWORD`
   - `WEAVIATE_API_KEY`

3. **環境変数の外部化**
   - `.env` ファイルを使用
   - Git にコミットしない

4. **Nginx の HTTPS 化**
   - Let's Encrypt で証明書取得
   - HTTP から HTTPS へリダイレクト

5. **Weaviate の認証有効化**
   ```yaml
   AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
   ```

6. **Redis の接続制限**
   - ファイアウォールで外部アクセスを制限
   - Docker ネットワーク内のみに限定

---

## 開発環境での起動手順

```bash
# 1. 環境変数の設定
cp .env.example .env
nano .env  # iCloud の認証情報を設定

# 2. コンテナのビルドと起動
docker-compose up -d --build

# 3. ログの確認
docker-compose logs -f

# 4. 初回セットアップ
# ブラウザで http://localhost にアクセス
# Dify のセットアップウィザードに従う

# 5. Email Service の動作確認
curl http://localhost:8000/health
```

---

## トラブルシューティング

### コンテナが起動しない場合

```bash
# 個別のサービスログを確認
docker-compose logs db
docker-compose logs api
docker-compose logs email-service

# ヘルスチェックの状態を確認
docker-compose ps
```

### Email Service が接続できない場合

1. iCloud のアプリ専用パスワードを確認
2. 2 段階認証が有効になっているか確認
3. IMAP が有効になっているか確認

### Dify にログインできない場合

1. 初回セットアップが完了しているか確認
2. PostgreSQL の接続を確認
   ```bash
   docker-compose exec db psql -U dify -c "SELECT 1"
   ```

---

## まとめ

この構成の特徴：

1. **マイクロサービスアーキテクチャ**
   - 各サービスが独立したコンテナ
   - スケーラブルな設計

2. **データ永続化**
   - ボリュームマウントでデータ保持
   - コンテナ再起動でもデータ消失なし

3. **ヘルスチェック**
   - 依存関係の順序制御
   - 安定した起動

4. **カスタムサービス統合**
   - Email Service で独自機能を追加
   - Dify のエコシステムに組み込み

5. **開発者フレンドリー**
   - ホットリロード対応
   - ログの集約管理
   - 環境変数での設定管理
