"""
データモデル
APIのリクエスト/レスポンスの形式を定義
"""
from pydantic import BaseModel, Field
from typing import List


class EmailMessage(BaseModel):
    """メール1通のデータ"""
    id: int
    subject: str
    sender: str = Field(alias="from")  # "from"はPythonの予約語なのでエイリアス
    date: str
    body: str
    snippet: str  # 本文の抜粋（最初の100文字）

    class Config:
        populate_by_name = True  # senderでもfromでも設定可能


class EmailResponse(BaseModel):
    """メール取得APIのレスポンス"""
    count: int
    emails: List[EmailMessage]


class HealthResponse(BaseModel):
    """ヘルスチェックAPIのレスポンス"""
    status: str
    imap_server: str
    connected: bool
