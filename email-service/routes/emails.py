"""
メール取得エンドポイント
Gmailからメールを取得するAPI
"""
import logging

from fastapi import APIRouter, HTTPException, Query

from models import EmailResponse
from services.imap_service import fetch_emails

logger = logging.getLogger(__name__)

# ルーターを作成
router = APIRouter(tags=["Emails"])


@router.get("/emails", response_model=EmailResponse)
async def get_emails(
    limit: int = Query(default=10, ge=1, le=100, description="取得するメール件数"),
    folder: str = Query(default="INBOX", description="メールボックス名")
):
    """
    最新のメールを取得

    Parameters:
    - limit: 取得件数（1-100）
    - folder: メールボックス（デフォルト: INBOX）

    Returns:
    - EmailResponse: メール一覧
    """
    try:
        email_list = fetch_emails(limit=limit, folder=folder)
        return EmailResponse(count=len(email_list), emails=email_list)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")
