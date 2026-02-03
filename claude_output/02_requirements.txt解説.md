# requirements.txt の想定内容解説

## 概要
`email-service/requirements.txt` は、iCloudメール取得APIサービスで使用するPythonパッケージの依存関係を定義するファイルです。

## 場所
- **正しい配置場所**: `/home/naoki/dify_app/email-service/requirements.txt`
- Dockerfileの13行目で `COPY requirements.txt .` としてコピーされます

## 想定される依存パッケージ

### 必須パッケージ

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
```

#### 各パッケージの役割

1. **fastapi**
   - REST APIフレームワーク
   - Difyから呼び出し可能なエンドポイントを提供
   - 自動的なAPIドキュメント生成（Swagger UI）

2. **uvicorn[standard]**
   - ASGIサーバー
   - FastAPIアプリケーションを実行
   - `[standard]` で追加の依存関係（websockets, httptools等）を含む
   - Dockerfile の CMD で使用: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

3. **pydantic**
   - データバリデーションライブラリ
   - FastAPIのリクエスト/レスポンスモデル定義に使用
   - 型安全性を提供

4. **pydantic-settings**
   - 環境変数の読み込みと管理
   - docker-compose.ymlで定義された環境変数（ICLOUD_EMAIL, ICLOUD_PASSWORD等）を扱う

### IMAPクライアント用パッケージ（いずれか）

#### オプション1: imapclient（推奨）
```txt
imapclient==3.0.1
```
- 高レベルなIMAPクライアントライブラリ
- 使いやすいAPI
- SSL/TLS接続のサポート

#### オプション2: 標準ライブラリ
- `imaplib` は Python 標準ライブラリなので requirements.txt 不要
- より低レベルだが追加インストール不要

## サービスの役割（docker-compose.yml より）

```yaml
email-service:
  # IMAPでメールを取得し、Difyから呼び出し可能なREST APIを提供
  environment:
    ICLOUD_EMAIL: ${ICLOUD_EMAIL:-your-email@icloud.com}
    ICLOUD_PASSWORD: ${ICLOUD_PASSWORD:-your-app-specific-password}
    IMAP_SERVER: imap.mail.me.com
    IMAP_PORT: 993
```

## 推奨される requirements.txt の内容

```txt
# Web API フレームワーク
fastapi==0.109.0
uvicorn[standard]==0.27.0

# データバリデーションと設定管理
pydantic==2.5.3
pydantic-settings==2.1.0

# IMAPクライアント
imapclient==3.0.1

# オプション: ロギング、日時処理など
python-dateutil==2.8.2
```

## 次のステップ

requirements.txt を作成した後、以下のファイルも必要です:

1. **main.py**: FastAPIアプリケーション本体
   - `/emails` などのエンドポイント定義
   - IMAP接続とメール取得ロジック
   - 環境変数からの設定読み込み

2. **.env** (オプション): ローカル開発用の環境変数
   - ICLOUD_EMAIL
   - ICLOUD_PASSWORD（アプリ固有パスワード）

## iCloud メール接続について

- **IMAPサーバー**: imap.mail.me.com
- **ポート**: 993 (SSL/TLS)
- **認証**: アプリ固有パスワードが必要
  - Apple ID の2ファクタ認証を有効にする
  - appleid.apple.com でアプリ固有パスワードを生成
