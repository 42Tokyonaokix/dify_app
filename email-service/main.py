"""
Gmail Email Service API
エントリーポイント - FastAPIアプリケーションの初期化と起動
"""
import logging

from fastapi import FastAPI

from config import settings
from services.imap_service import connect_imap
from routes import emails, health

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション作成
app = FastAPI(
    title="Gmail Email Service",
    description="IMAPでGmailを取得するREST API",
    version="1.0.0"
)

# ルーターを登録（各エンドポイントを追加）
app.include_router(health.router)
app.include_router(emails.router)


# === ルートエンドポイント ===
@app.get("/", tags=["Info"])
async def root():
    """API情報を返す"""
    return {
        "service": "Gmail Email Service",
        "version": "1.0.0",
        "endpoints": {
            "/emails": "Get latest emails",
            "/health": "Health check",
            "/docs": "API documentation"
        }
    }


# === ライフサイクルイベント ===
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("Starting Gmail Email Service...")
    logger.info(f"IMAP Server: {settings.imap_server}:{settings.imap_port}")
    logger.info(f"Email: {settings.gmail_email}")

    # 接続テスト
    try:
        with connect_imap() as client:
            folders = client.list_folders()
            logger.info(f"Available folders: {[f[2] for f in folders]}")
    except Exception as e:
        logger.warning(f"Initial connection test failed: {e}")
        logger.warning("Service will start, but IMAP connection may not work")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    logger.info("Shutting down Gmail Email Service...")


# === 直接実行時 ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
