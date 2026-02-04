# Dify Apps

Difyで作成したアプリケーションのDSLファイル（エクスポート）を格納。

## 含まれるアプリ

| ファイル | タイプ | 説明 |
|---------|--------|------|
| `email_return.yml` | Agent | メール取得エージェント。email-serviceと連携してGmailを取得・表示 |

## インポート手順

### 1. Dify Studioにアクセス

```
http://localhost:3000
```

### 2. アプリをインポート

1. 左サイドバーの「スタジオ」をクリック
2. 「アプリを作成」→「DSLファイルをインポート」
3. YAMLファイルをアップロード
4. インポート完了

### 3. カスタムツールの設定

インポート後、カスタムツール（email-service）を再設定する必要があります。

#### OpenAPIスキーマ

「ツール」→「カスタムツール」→「作成」で以下を登録：

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Email Service",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "http://email-service:8000"
    }
  ],
  "paths": {
    "/emails": {
      "get": {
        "operationId": "getEmails",
        "summary": "メールを取得する",
        "parameters": [
          {
            "name": "limit",
            "in": "query",
            "schema": {
              "type": "integer",
              "default": 10,
              "minimum": 1,
              "maximum": 100
            },
            "description": "取得するメール件数"
          },
          {
            "name": "folder",
            "in": "query",
            "schema": {
              "type": "string",
              "default": "INBOX"
            },
            "description": "メールボックス名（INBOX, Sent, SPAM等）"
          }
        ],
        "responses": {
          "200": {
            "description": "メール一覧"
          }
        }
      }
    }
  }
}
```

### 4. エージェントにツールを追加

1. インポートしたアプリを開く
2. 「ツール」セクション →「+ 追加」
3. 登録したEmail Serviceの`getEmails`を選択
4. 保存

## 動作確認

プレビューで以下を入力：

```
最新のメールを見せて
```

メール内容が表示されれば成功。
