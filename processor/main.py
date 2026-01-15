import os
import glob
from datetime import datetime
from loguru import logger
from config import settings
from utils.media_tool import MediaTool, OCRTool
from tqdm import tqdm

def process_daily_content(date_str: str = None):
    """
    Main processing pipeline for a specific date.
    1. Extract audio from videos.
    2. Transcribe audio files.
    3. Perform OCR on images.
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    daily_dir = os.path.join(settings.SAVE_PATH, date_str)
    if not os.path.exists(daily_dir):
        logger.warning(f"No data directory found for {date_str}: {daily_dir}")
        return

    # Define platform scopes
    OCR_PLATFORMS = ["Xiaohongshu"]
    TRANSCRIPTION_PLATFORMS = ["Bilibili", "Xiaohongshu"]

    def get_platform(path):
        try:
            return os.path.relpath(path, daily_dir).split(os.sep)[0]
        except:
            return ""

    # Phase 1: Audio Extraction from Videos
    logger.info(f"Phase 1: Checking for video files in {daily_dir}...")
    video_files = glob.glob(os.path.join(daily_dir, "**", "video.mp4"), recursive=True)
    for video_path in video_files:
        platform = get_platform(video_path)
        if platform not in TRANSCRIPTION_PLATFORMS:
            continue

        audio_path = os.path.join(os.path.dirname(video_path), "audio.wav")
        if not os.path.exists(audio_path):
            MediaTool.extract_audio(video_path, audio_path)

    # Phase 2: Transcription
    logger.info(f"Phase 2: Transcribing audio files in {daily_dir}...")
    audio_files = glob.glob(os.path.join(daily_dir, "**", "*.wav"), recursive=True)
    # Filter audio files by platform
    audio_files = [f for f in audio_files if get_platform(f) in TRANSCRIPTION_PLATFORMS]

    if audio_files and MediaTool.is_available():
        MediaTool.get_model() # Ensure model is loaded
        for audio_path in tqdm(audio_files, desc="Transcribing"):
            try:
                handle_transcription(audio_path)
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_path}: {e}")
    else:
        logger.info("No audio files or Whisper unavailable (or skipped by platform filter).")

    # Phase 3: OCR
    logger.info(f"Phase 3: Performing OCR on images in {daily_dir}...")
    # Find all post directories that have an assets folder
    assets_dirs = glob.glob(os.path.join(daily_dir, "**", "assets"), recursive=True)
    # Filter assets dirs by platform
    assets_dirs = [d for d in assets_dirs if get_platform(d) in OCR_PLATFORMS]

    if assets_dirs:
        for assets_path in tqdm(assets_dirs, desc="OCR Processing"):
            try:
                handle_ocr(assets_path)
            except Exception as e:
                logger.error(f"Failed to process OCR for {assets_path}: {e}")
    else:
        logger.info("No assets folders found for OCR (or skipped by platform filter).")

def handle_transcription(audio_path: str):
    dir_path = os.path.dirname(audio_path)
    md_files = glob.glob(os.path.join(dir_path, "*.md"))
    if not md_files: return
    
    md_path = md_files[0]
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "[PENDING_TRANSCRIPTION]" not in content and "[AI-Generated Transcript]" in content:
        return # Skip if already done

    text = MediaTool.transcribe_file(audio_path)
    if text:
        new_content = content.replace("[PENDING_TRANSCRIPTION]", "")
        if "## 字幕/文稿" not in new_content:
            new_content += "\n\n## 字幕/文稿\n"
        
        transcript_marker = "[AI-Generated Transcript]"
        if transcript_marker not in new_content:
            new_content += f"\n{transcript_marker}\n{text}\n"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

def handle_ocr(assets_path: str):
    post_dir = os.path.dirname(assets_path)
    md_files = glob.glob(os.path.join(post_dir, "*.md"))
    if not md_files: return
    
    md_path = md_files[0]
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if OCR already performed for this post
    if "## 图片 OCR 结果" in content:
        return

    image_exts = ['*.jpg', '*.jpeg', '*.png', '*.webp']
    images = []
    for ext in image_exts:
        images.extend(glob.glob(os.path.join(assets_path, ext)))
    
    if not images: return

    ocr_results = []
    for img_path in sorted(images):
        text = OCRTool.recognize_text(img_path)
        if text:
            filename = os.path.basename(img_path)
            ocr_results.append(f"### {filename}\n{text}\n")
    
    if ocr_results:
        ocr_section = "\n\n## 图片 OCR 结果\n" + "\n".join(ocr_results)
        with open(md_path, 'a', encoding='utf-8') as f:
            f.write(ocr_section)
        logger.info(f"Added OCR results to {os.path.basename(md_path)}")

if __name__ == "__main__":
    process_daily_content()
