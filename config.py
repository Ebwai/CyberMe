import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # System
    LOG_LEVEL: str = "INFO"
    SAVE_PATH: str = r"F:\DataInput"
    CRON_TIME: str = "22:00"
    STATE_FILE_PATH: str = r"F:\DataInput\crawl_state.json"

    # Bilibili
    BILI_SESSDATA: str = ""
    BILI_JCT: str = ""
    BILI_BUVID3: str = ""
    BILI_MEDIA_ID: str = "" # Default Favorites Folder ID

    # Douyin
    DOUYIN_COOKIE: str = ""

    # Xiaohongshu
    XHS_COOKIE: str = ""
    
    # WeChat
    WECHAT_URLS_FILE: str = r"F:\DataInput\wechat_urls.txt"
    WECHAT_DB_PATH: str = ""

    # Whisper & Media
    WHISPER_MODEL_DIR: str = r"F:\Spider_proj\models"
    TEMP_AUDIO_DIR: str = r"F:\Spider_proj\temp"
    WHISPER_MODEL_SIZE: str = "base" # tiny, base, small, medium, large
    WHISPER_DEVICE: str = "cuda" # cuda or cpu

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# Ensure save path exists
if not os.path.exists(settings.SAVE_PATH):
    os.makedirs(settings.SAVE_PATH, exist_ok=True)
