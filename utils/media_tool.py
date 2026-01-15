import os
import asyncio
import logging
import subprocess
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

WHISPER_AVAILABLE = False
try:
    import yt_dlp
    import whisper
    WHISPER_AVAILABLE = True
except Exception as e:
    logger.warning(f"MediaTool dependencies check failed: {e}")
    # traceback is better but we don't want to spam if it's just missing
    # logger.exception(e) 


class MediaTool:
    _model = None

    @classmethod
    def is_available(cls) -> bool:
        if not WHISPER_AVAILABLE:
            return False
            
        # Check for ffmpeg
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n" + "!"*60)
            print(f"⚠️  【系统错误】 未检测到 ffmpeg")
            print("!"*60)
            print(f"原因详情: 系统中未安装 ffmpeg 或未将其添加至环境变量 PATH。")
            print(f"解决办法: 请安装 ffmpeg 并确保在命令行输入 'ffmpeg' 能正常运行。")
            print("!"*60 + "\n")
            logger.error("ffmpeg is missing. Processing will be partially disabled.")
            return False

    @classmethod
    def get_model(cls):
        """Lazy load the Whisper model."""
        if not WHISPER_AVAILABLE:
            return None
            
        if cls._model is None:
            logger.info(f"Loading Whisper model '{settings.WHISPER_MODEL_SIZE}' on device '{settings.WHISPER_DEVICE}' from {settings.WHISPER_MODEL_DIR}...")
            # Ensure model directory exists
            os.makedirs(settings.WHISPER_MODEL_DIR, exist_ok=True)
            try:
                cls._model = whisper.load_model(
                    settings.WHISPER_MODEL_SIZE, 
                    download_root=settings.WHISPER_MODEL_DIR,
                    device=settings.WHISPER_DEVICE
                )
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
        return cls._model

    @staticmethod
    async def download_audio(url: str, target_path: str) -> bool:
        """
        Download audio from a video URL using yt-dlp to a specific path.
        Returns True if successful.
        """
        if not WHISPER_AVAILABLE:
            return False

        return await asyncio.to_thread(MediaTool._sync_download_audio, url, target_path)

    @staticmethod
    async def download_video(url: str, target_path: str) -> bool:
        """
        Download video from a URL using yt-dlp to a specific path.
        Returns True if successful.
        """
        if not WHISPER_AVAILABLE:
            return False

        return await asyncio.to_thread(MediaTool._sync_download_video, url, target_path)

    @staticmethod
    def _sync_download_video(url: str, target_path: str) -> bool:
        dir_name = os.path.dirname(target_path)
        file_name = os.path.basename(target_path)
        base_name, _ = os.path.splitext(file_name)
        
        os.makedirs(dir_name, exist_ok=True)
        
        # We want to force the filename to match target_path if possible, 
        # but yt-dlp determines extension based on format.
        # We use 'merge_output_format': 'mp4' to encourage mp4.
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(dir_name, f"{base_name}.%(ext)s"),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            # Add headers if needed, but usually yt-dlp handles it
        }

        try:
            logger.info(f"Downloading video from {url} to directory {dir_name}...")
            import yt_dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # After download, we need to ensure the file exists at target_path
            # If target_path is "video.mp4", and yt-dlp produced "video.mp4", we are good.
            # If yt-dlp produced "video.mkv", we might want to rename or convert, 
            # but 'merge_output_format': 'mp4' usually ensures mp4.
            
            # Check for likely candidates
            candidates = [
                os.path.join(dir_name, f"{base_name}.mp4"),
                os.path.join(dir_name, f"{base_name}.mkv"),
                os.path.join(dir_name, f"{base_name}.webm")
            ]
            
            found_file = None
            for c in candidates:
                if os.path.exists(c):
                    found_file = c
                    break
            
            if found_file:
                if found_file != target_path:
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    os.rename(found_file, target_path)
                return True
            
            logger.error("Video download finished but expected file not found.")
            return False

        except Exception as e:
            logger.error(f"yt-dlp video download failed: {e}")
            return False

    @staticmethod
    def _sync_download_audio(url: str, target_path: str) -> bool:
        # target_path should be the full path including filename and extension (e.g. .../audio.wav)
        # yt-dlp expects a template without extension if we want it to decide, 
        # but here we want force wav.
        
        # We use a temp template and then rename/move or let ffmpeg handle it
        # Actually, if we set 'outtmpl' to target_path minus extension, it might add .wav
        
        dir_name = os.path.dirname(target_path)
        file_name = os.path.basename(target_path)
        base_name, _ = os.path.splitext(file_name)
        
        os.makedirs(dir_name, exist_ok=True)
        # output_template = os.path.join(dir_name, f"{base_name}.%(ext)s")
        # To force the exact filename:
        output_template = os.path.join(dir_name, f"{base_name}") # yt-dlp might add extension
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            logger.info(f"Downloading audio from {url} to {target_path}...")
            import yt_dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Check for the file. It should be .wav
            expected_wav = os.path.join(dir_name, f"{base_name}.wav")
            
            if os.path.exists(expected_wav):
                # If the user requested a specific path (target_path), rename if needed
                if expected_wav != target_path:
                     if os.path.exists(target_path):
                         os.remove(target_path)
                     os.rename(expected_wav, target_path)
                return True
            
            logger.error("Audio download finished but expected .wav file not found.")
            return False
        except Exception as e:
            err_msg = str(e)
            if "HTTP Error 403" in err_msg or "Sign in to confirm" in err_msg:
                print(f"\n❌ 【下载失败】 视频受限或失效: {url}")
                print(f"提示: 可能是 Cookie 失效、地区限制或需要登录观看。")
            elif "Connection" in err_msg or "Proxy" in err_msg:
                print(f"\n❌ 【网络错误】 无法连接到视频服务器: {url}")
                print(f"提示: 请检查网络连接或代理设置。")
            else:
                logger.error(f"yt-dlp download failed: {e}")
            return False

    @classmethod
    def transcribe_file(cls, audio_path: str) -> str:
        """
        Transcribe a local audio file using Whisper.
        This is a synchronous method (CPU blocking) intended to be run in a separate process or thread if needed,
        but since the new architecture separates processing, blocking here is acceptable or handled by caller.
        """
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper dependencies missing. Skipping transcription.")
            return ""

        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return ""

        try:
            model = cls.get_model()
            if not model:
                return ""

            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Transcribe
            # Note: run on GPU if configured in get_model
            result = model.transcribe(audio_path)
            text = result.get("text", "").strip()
            
            logger.info("Transcription completed.")
            return text
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""

    @staticmethod
    def extract_audio(video_path: str, audio_path: str) -> bool:
        """
        Extract audio from a video file using ffmpeg.
        Targeting 16kHz mono wav for optimal Whisper performance.
        Returns True if successful.
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return False

        try:
            logger.info(f"Extracting audio from {video_path} to {audio_path}...")
            
            # -y: overwrite output files
            # -i: input file
            # -vn: disable video
            # -acodec pcm_s16le: 16-bit PCM (WAV)
            # -ar 16000: 16kHz sampling rate
            # -ac 1: Mono
            command = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                audio_path
            ]
            
            # Run command
            # Use utf-8 encoding and ignore errors to prevent UnicodeDecodeError on Windows (GBK default)
            result = subprocess.run(command, capture_output=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                if os.path.exists(audio_path):
                    logger.info("Audio extraction completed successfully.")
                    return True
            
            logger.error(f"ffmpeg extraction failed with return code {result.returncode}")
            logger.error(f"ffmpeg stderr: {result.stderr}")
            return False
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            return False


class OCRTool:
    _reader = None

    @classmethod
    def get_reader(cls):
        """Lazy load the EasyOCR Reader."""
        if cls._reader is None:
            try:
                import torch
                import pickle
                
                # Monkeypatch torch.load for compatibility with Torch < 2.0 (weights_only)
                if not hasattr(torch, '_patched_for_easyocr'):
                    original_load = torch.load
                    def patched_load(f, map_location=None, pickle_module=pickle, **kwargs):
                        if 'weights_only' in kwargs:
                            del kwargs['weights_only']
                        return original_load(f, map_location=map_location, pickle_module=pickle_module, **kwargs)
                    torch.load = patched_load
                    torch._patched_for_easyocr = True
                    logger.info("Monkeypatched torch.load for EasyOCR compatibility.")

                import easyocr
                # Use GPU if available
                gpu_available = torch.cuda.is_available()
                logger.info(f"Initializing EasyOCR Reader (GPU={gpu_available})...")
                # Loading 'ch_sim' for simplified chinese and 'en' for english
                cls._reader = easyocr.Reader(
                    ['ch_sim', 'en'], 
                    gpu=gpu_available,
                    model_storage_directory=settings.WHISPER_MODEL_DIR # Centralized in F:\Spider_proj\models
                )
                logger.info("EasyOCR Reader initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                return None
        return cls._reader

    @classmethod
    def recognize_text(cls, image_path: str) -> str:
        """
        Recognize text from an image.
        Returns the combined text string.
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return ""

        try:
            import cv2
            import numpy as np
            
            reader = cls.get_reader()
            if not reader:
                return ""

            logger.info(f"Performing OCR on: {image_path}")
            
            # Use numpy and cv2.imdecode to support Chinese paths on Windows
            img_array = np.fromfile(image_path, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.error(f"Failed to decode image: {image_path}")
                return ""

            # detail=0 returns only the text content
            result = reader.readtext(img, detail=0)
            
            # Combine individual lines into one block
            text = "\n".join(result).strip()
            return text
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return ""
