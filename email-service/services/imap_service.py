"""
IMAPサービス
Gmailへの接続とメール取得を担当
"""
import email
from email.header import decode_header
import logging
from typing import List

from fastapi import HTTPException
from imapclient import IMAPClient

from config import settings
from models import EmailMessage

logger = logging.getLogger(__name__)


def connect_imap() -> IMAPClient:
    """
    IMAPサーバーに接続してクライアントを返す

    Returns:
        IMAPClient: 接続済みのIMAPクライアント

    Raises:
        HTTPException: 接続失敗時
    """
    try:
        client = IMAPClient(settings.imap_server, port=settings.imap_port, ssl=True)
        client.login(settings.gmail_email, settings.gmail_app_password)
        logger.info(f"Successfully connected to {settings.imap_server}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to IMAP server: {e}")
        raise HTTPException(status_code=500, detail=f"IMAP connection failed: {str(e)}")


def decode_mime_header(header_value: str) -> str:
    """
    MIMEエンコードされたヘッダーをデコード

    例: =?UTF-8?B?44GT44KT44Gr44Gh44Gv?= → こんにちは

    Args:
        header_value: エンコードされたヘッダー値

    Returns:
        デコードされた文字列
    """
    if not header_value:
        return ""

    decoded_parts = decode_header(header_value)
    decoded_string = ""

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded_string += part

    return decoded_string


def get_email_body(msg) -> str:
    """
    メールオブジェクトから本文を取得
    プレーンテキストを優先、なければHTMLを使用

    Args:
        msg: email.message.Messageオブジェクト

    Returns:
        メール本文
    """
    body = ""

    if msg.is_multipart():
        # マルチパートメール（テキスト+HTML等）の処理
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # 添付ファイルはスキップ
            if "attachment" in content_disposition:
                continue

            # プレーンテキストを優先
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                except Exception as e:
                    logger.warning(f"Failed to decode plain text: {e}")

            # HTMLがある場合はバックアップとして使用
            elif content_type == "text/html" and not body:
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except Exception as e:
                    logger.warning(f"Failed to decode HTML: {e}")
    else:
        # シンプルなメール（単一パート）
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Failed to decode simple message: {e}")
            body = str(msg.get_payload())

    return body.strip()


def fetch_emails(limit: int = 10, folder: str = "INBOX") -> List[EmailMessage]:
    """
    メールを取得

    Args:
        limit: 取得件数（1-100）
        folder: メールボックス名

    Returns:
        EmailMessageのリスト
    """
    with connect_imap() as client:
        # フォルダを選択（読み取り専用）
        client.select_folder(folder, readonly=True)

        # 全メールのIDを取得（削除済みを除く）
        messages = client.search(['NOT', 'DELETED'])

        if not messages:
            return []

        # 最新のメールから取得
        latest_messages = messages[-limit:] if len(messages) > limit else messages
        latest_messages.reverse()  # 新しい順にソート

        # メールデータを取得
        email_list = []
        fetch_data = client.fetch(latest_messages, ['RFC822'])

        for msg_id, data in fetch_data.items():
            try:
                # 生データをメールオブジェクトにパース
                raw_email = data[b'RFC822']
                msg = email.message_from_bytes(raw_email)

                # ヘッダー情報を取得
                subject = decode_mime_header(msg.get('Subject', 'No Subject'))
                sender = decode_mime_header(msg.get('From', 'Unknown'))
                date = msg.get('Date', 'Unknown')

                # 本文を取得
                body = get_email_body(msg)
                snippet = body[:100] + "..." if len(body) > 100 else body

                email_list.append(EmailMessage(
                    id=msg_id,
                    subject=subject,
                    sender=sender,
                    date=date,
                    body=body,
                    snippet=snippet
                ))

            except Exception as e:
                logger.error(f"Failed to parse email {msg_id}: {e}")
                continue

        return email_list
