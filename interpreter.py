
import os
import time
import json
import threading
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

import azure.cognitiveservices.speech as speechsdk

load_dotenv()

# Keys & region
SPEECH_KEY = os.getenv("SPEECH_KEY", "")
SPEECH_REGION = os.getenv("SPEECH_REGION", "")

#CUSTOM_ENDPOINT_ID = os.getenv("CUSTOM_ENDPOINT_ID", "")
#CUSTOM_ENDPOINT_KEY = os.getenv("CUSTOM_ENDPOINT_KEY", "")

CUSTOM_ENDPOINT_KEY = ""
CATEGORY_ENDPOINT_ID = os.getenv("CATEGORY_ENDPOINT_ID", "")

# Source/Target
LOCALE = os.getenv("LOCALE", "en-US")
TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE", "it")

# TTS
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-JennyNeural")
USE_SPEAKER = True  # default speaker for synthesis output

# IO
INPUT_DIR = os.getenv("INPUT_DIR", "./incoming_audio")
USE_MIC = os.getenv("USE_MIC", "false").lower() == "true"

# Segmentation / silence timeouts (same knobs you used)
SEG_STRAT = os.getenv("SEGMENTATION_STRATEGY", "Semantic")
SEG_INIT_SILENCE_TIMEOUT = os.getenv("SEGMENTATION_INIT_SILENCE_TIMEOUT_MS", "800")
SEG_END_SILENCE_TIMEOUT = os.getenv("SEGMENTATION_END_SILENCE_TIMEOUT_MS", "800")

_synth_lock = threading.Lock()

# ============================================================
# Config builders
# ============================================================
def _resolve_subscription_key() -> str:
    return CUSTOM_ENDPOINT_KEY or SPEECH_KEY

def build_translation_config() -> speechsdk.translation.SpeechTranslationConfig:
    key = _resolve_subscription_key()
    if not key or not SPEECH_REGION:
        raise RuntimeError("Set SPEECH_KEY (or CUSTOM_ENDPOINT_KEY) and SPEECH_REGION in .env")

    tcfg = speechsdk.translation.SpeechTranslationConfig(
        subscription=key,
        region=SPEECH_REGION,
    )

    tcfg.speech_recognition_language = LOCALE

    tcfg.add_target_language(TARGET_LANGUAGE)

    tcfg.set_property(speechsdk.PropertyId.Speech_SegmentationStrategy, SEG_STRAT)
    tcfg.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, SEG_INIT_SILENCE_TIMEOUT)
    tcfg.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, SEG_END_SILENCE_TIMEOUT)

    tcfg.set_profanity(speechsdk.ProfanityOption.Masked)

    if CATEGORY_ENDPOINT_ID:
        tcfg.endpoint_id = CATEGORY_ENDPOINT_ID

    return tcfg

def build_synthesizer() -> speechsdk.SpeechSynthesizer:
    if not _resolve_subscription_key() or not SPEECH_REGION:
        raise RuntimeError("Set SPEECH_KEY (or CUSTOM_ENDPOINT_KEY) and SPEECH_REGION in .env")

    scfg = speechsdk.SpeechConfig(
        subscription=_resolve_subscription_key(),
        region=SPEECH_REGION,
    )

    scfg.speech_synthesis_voice_name = TTS_VOICE

    audio_cfg = speechsdk.audio.AudioOutputConfig(use_default_speaker=USE_SPEAKER)
    return speechsdk.SpeechSynthesizer(speech_config=scfg, audio_config=audio_cfg)

# ============================================================
# Utilities
# ============================================================
def speak_text(synth: speechsdk.SpeechSynthesizer, text: str):
    if not text:
        return
    with _synth_lock:
        # Fire-and-wait
        result = synth.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"[TTS] ✔ {len(text)} chars")
        elif result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details
            print(f"[TTS] Canceled: {details.reason} {details.error_details}")

# ============================================================
# Real-time from microphone
# ============================================================
def interpret_microphone():
    print(f"[Interpreter] Mic mode. Source={LOCALE} → Target={TARGET_LANGUAGE}")
    print(f"[Segmentation] Strategy={SEG_STRAT}, SilenceTimeout=[Init:{SEG_INIT_SILENCE_TIMEOUT}ms, End:{SEG_END_SILENCE_TIMEOUT}ms]")
    tcfg = build_translation_config()
    audio_in = speechsdk.AudioConfig(use_default_microphone=True)
    trec = speechsdk.translation.TranslationRecognizer(translation_config=tcfg, audio_config=audio_in)

    synth = build_synthesizer()

    def recognizing_cb(evt: speechsdk.translation.TranslationRecognitionEventArgs):
        if evt.result.reason == speechsdk.ResultReason.TranslatingSpeech:
            partial = evt.result.translations.get(TARGET_LANGUAGE, "")
            if partial:
                print(f" [Interim] {partial}")

    def recognized_cb(evt: speechsdk.translation.TranslationRecognitionEventArgs):
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            src_disp = evt.result.text or ""
            tgt_disp = evt.result.translations.get(TARGET_LANGUAGE, "")
            print(f"[Segment][Src] {src_disp}")
            print(f"[Segment][Tgt] {tgt_disp}")
            try:
                payload = json.loads(evt.result.json)
            except Exception as ex:
                pass
            speak_text(synth, tgt_disp)
        elif evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"[Segment][Src-only] {evt.result.text}")
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("[Segment] NoMatch")

    def canceled_cb(evt: speechsdk.SpeechRecognitionCanceledEventArgs):
        print(f"[Canceled] {evt.reason} {evt.error_details}")

    def session_started_cb(evt: speechsdk.SessionEventArgs):
        print("[Session] Started")

    def session_stopped_cb(evt: speechsdk.SessionEventArgs):
        print("[Session] Stopped")

    trec.recognizing.connect(recognizing_cb)
    trec.recognized.connect(recognized_cb)
    trec.canceled.connect(canceled_cb)
    trec.session_started.connect(session_started_cb)
    trec.session_stopped.connect(session_stopped_cb)

    trec.start_continuous_recognition()
    print("[Interpreter] Speak; translated segments will play out. Ctrl+C to stop.\n")
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[Interpreter] Stopping…")
    finally:
        trec.stop_continuous_recognition()

# ============================================================
# From audio files (folder watch)
# ============================================================
def interpret_file(audio_path: Path):
    print(f"[Interpreter] File: {audio_path.name}  Source={LOCALE} → Target={TARGET_LANGUAGE}")
    tcfg = build_translation_config()
    audio_in = speechsdk.AudioConfig(filename=str(audio_path))
    trec = speechsdk.translation.TranslationRecognizer(translation_config=tcfg, audio_config=audio_in)

    synth = build_synthesizer()

    def recognizing_cb(evt: speechsdk.translation.TranslationRecognitionEventArgs):
        if evt.result.reason == speechsdk.ResultReason.TranslatingSpeech:
            partial = evt.result.translations.get(TARGET_LANGUAGE, "")
            if partial:
                print(f" [Interim] {partial}")

    def recognized_cb(evt: speechsdk.translation.TranslationRecognitionEventArgs):
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            src_disp = evt.result.text or ""
            tgt_disp = evt.result.translations.get(TARGET_LANGUAGE, "")
            print(f"[Segment][Src] {src_disp}")
            print(f"[Segment][Tgt] {tgt_disp}")
            # Speak the translated text for each finalized segment
            speak_text(synth, tgt_disp)

    def canceled_cb(evt: speechsdk.SpeechRecognitionCanceledEventArgs):
        print(f"[Canceled] {evt.reason} {evt.error_details}")

    trec.recognizing.connect(recognizing_cb)
    trec.recognized.connect(recognized_cb)
    trec.canceled.connect(canceled_cb)

    trec.start_continuous_recognition()
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[Interpreter] Pausing… (next file)")
    finally:
        trec.stop_continuous_recognition()

def watch_folder():
    input_dir = Path(INPUT_DIR)
    input_dir.mkdir(parents=True, exist_ok=True)
    print(f"[Daemon] Watching: {input_dir.resolve()} (drop .wav/.mp3/.mp4/.m4a/.flac)")
    print(f"[Segmentation] Strategy={SEG_STRAT}, SilenceTimeout=[Init:{SEG_INIT_SILENCE_TIMEOUT}ms, End:{SEG_END_SILENCE_TIMEOUT}ms]")
    seen = set()
    try:
        while True:
            for p in input_dir.iterdir():
                if p.is_file() and p.suffix.lower() in {".wav", ".mp3", ".mp4", ".m4a", ".flac"} and p not in seen:
                    seen.add(p)
                    interpret_file(p)
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[Daemon] Stopped.")

# ============================================================
# Entrypoint
# ============================================================
if __name__ == "__main__":
    mic = str(input("Use microphone? (Y/N): ")).strip().lower()
    if mic == "y":
        interpret_microphone()
    else:
        watch_folder()
