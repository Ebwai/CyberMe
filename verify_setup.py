import sys
import os
from loguru import logger

# Add project root to sys.path
sys.path.append(os.getcwd())

def test_imports():
    logger.info("Testing imports...")
    try:
        from config import settings
        logger.success(f"Config loaded. SAVE_PATH: {settings.SAVE_PATH}")
        
        # Check if sensitive keys are set (mask them)
        if settings.BILI_SESSDATA: logger.success("Bili config: OK")
        else: logger.error("Bili config: MISSING")
            
        if settings.DOUYIN_COOKIE: logger.success("Douyin config: OK")
        else: logger.error("Douyin config: MISSING")

        if settings.XHS_COOKIE: logger.success("XHS config: OK")
        else: logger.error("XHS config: MISSING")
            
        import crawlers.bilibili
        import crawlers.douyin
        import crawlers.wechat
        import crawlers.xhs
        import utils.storage
        logger.success("All modules imported successfully.")
        return True
    except Exception as e:
        logger.exception(f"Import failed: {e}")
        return False

if __name__ == "__main__":
    if test_imports():
        logger.success("Environment Verification PASSED")
    else:
        logger.error("Environment Verification FAILED")
        sys.exit(1)
