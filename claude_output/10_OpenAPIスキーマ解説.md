# OpenAPIスキーマ解説

## 概要

OpenAPIスキーマは**APIの仕様書**。DifyのカスタムツールにAPIの呼び出し方を教えるために使用する。

## 今回作成したスキーマ

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
              "default": 5
            }
          },
          {
            "name": "folder",
            "in": "query",
            "schema": {
              "type": "string",
              "default": "INBOX"
            }
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

## 各セクションの解説

### 1. メタ情報

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Email Service",
    "version": "1.0.0"
  },
```

| キー | 説明 |
|------|------|
| `openapi` | OpenAPI仕様のバージョン（3.0.0が現行） |
| `info.title` | APIの名前（Difyでツール名として表示） |
| `info.version` | APIのバージョン番号 |

### 2. サーバー設定

```json
  "servers": [
    {
      "url": "http://email-service:8000"
    }
  ],
```

| キー | 説明 |
|------|------|
| `servers` | APIのベースURLを指定 |
| `url` | Docker内部のemail-serviceコンテナのアドレス |

**ポイント**: Docker Compose内では、サービス名（`email-service`）でコンテナ間通信ができる。

### 3. パス（エンドポイント）定義

```json
  "paths": {
    "/emails": {
      "get": {
```

| キー | 説明 |
|------|------|
| `paths` | 利用可能なエンドポイント一覧 |
| `/emails` | エンドポイントのパス |
| `get` | HTTPメソッド（GET, POST, PUT, DELETE等） |

**実際のURL**: `http://email-service:8000/emails`

### 4. オペレーション情報

```json
        "operationId": "getEmails",
        "summary": "メールを取得する",
```

| キー | 説明 |
|------|------|
| `operationId` | ツールの一意識別子（Difyが内部で使用） |
| `summary` | ツールの説明（UIに表示される） |

### 5. パラメータ定義

```json
        "parameters": [
          {
            "name": "limit",
            "in": "query",
            "schema": {
              "type": "integer",
              "default": 5
            }
          },
```

| キー | 説明 |
|------|------|
| `name` | パラメータ名 |
| `in` | パラメータの送り方 |
| `schema.type` | データ型（integer, string, boolean等） |
| `schema.default` | デフォルト値 |

#### `in` の種類

| 値 | 説明 | 例 |
|----|------|-----|
| `query` | URLクエリパラメータ | `/emails?limit=5` |
| `path` | URLパスの一部 | `/emails/{id}` |
| `header` | HTTPヘッダー | `Authorization: Bearer xxx` |
| `body` | リクエストボディ | POSTのJSON本文 |

### 6. レスポンス定義

```json
        "responses": {
          "200": {
            "description": "メール一覧"
          }
        }
```

| キー | 説明 |
|------|------|
| `200` | HTTPステータスコード（成功） |
| `description` | レスポンスの説明 |

## Difyでの動作

このスキーマをDifyに登録すると：

1. **ツールとして認識**: 「getEmails」というツールが使用可能になる
2. **AI が自動呼び出し**: ユーザーが「メール見せて」と言うとAIがこのツールを使う
3. **パラメータ自動設定**: AIが文脈から`limit`や`folder`を適切に設定

### 実際のAPI呼び出し例

```
GET http://email-service:8000/emails?limit=5&folder=INBOX
```

## YAML vs JSON

Difyは**JSON形式**を推奨。YAML形式だと `invalid schema type` エラーになる場合がある。

| 形式 | Dify対応 |
|------|----------|
| JSON | OK |
| YAML | エラーになることがある |

## 参考リンク

- [OpenAPI Specification](https://swagger.io/specification/)
- [Dify カスタムツールドキュメント](https://docs.dify.ai/)
