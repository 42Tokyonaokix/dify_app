"""
ヘルスチェックエンドポイント
サービスの状態を確認
"""
from fastapi import APIRouter

from config import settings
from models import HealthResponse
from services.imap_service import connect_imap

# ルーターを作成（app.get()の代わりにrouter.get()を使う）
router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    ヘルスチェック - IMAP接続を確認

    Returns:
        HealthResponse: 接続状態
    """
    try:
        with connect_imap() as client:
            connected = True
    except:
        connected = False

    return HealthResponse(
        status="healthy" if connected else "unhealthy",
        imap_server=settings.imap_server,
        connected=connected
    )
