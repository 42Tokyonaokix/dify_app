"""
設定モジュール
環境変数から設定を読み込む
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """環境変数からの設定読み込み"""
    gmail_email: str = Field(default="your-email@gmail.com")
    gmail_app_password: str = Field(default="your-app-password")
    imap_server: str = Field(default="imap.gmail.com")
    imap_port: int = Field(default=993)

    class Config:
        env_file = ".env"
        case_sensitive = False


# シングルトンとして設定を作成
settings = Settings()
