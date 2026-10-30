"""
src/audio/voice_cloner.py - Tone-color conversion / voice cloning using OpenVoice.

Converts base TTS narration to match a target voice timbre (e.g., actress)
using a reference audio clip. Runs on CPU or GPU.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class VoiceCloner:
    """Clones voice tone color from a reference audio file onto synthesized speech."""

    @staticmethod
    def _ensure_ffmpeg_path() -> Optional[str]:
        """Ensures an ffmpeg executable is accessible in PATH via imageio-ffmpeg if available."""
        if shutil.which("ffmpeg"):
            return None
        try:
            import imageio_ffmpeg
            exe_path = Path(imageio_ffmpeg.get_ffmpeg_exe())
            ffmpeg_dir = exe_path.parent
            # Whisper / pydub look explicitly for 'ffmpeg.exe'
            target_exe = ffmpeg_dir / "ffmpeg.exe"
            if not target_exe.exists():
                shutil.copyfile(exe_path, target_exe)
            return str(ffmpeg_dir)
        except Exception:
            return None

    @staticmethod
    def is_available() -> bool:
        """Checks if openvoice-cli is installed and callable."""
        try:
            import openvoice_cli  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def clone(
        input_audio_path: str,
        ref_audio_path: str,
        output_audio_path: Optional[str] = None,
        device: str = "cpu",
    ) -> str:
        """
        Converts the vocal timbre of input_audio_path to match ref_audio_path.

        Args:
            input_audio_path: Path to the generated speech WAV file.
            ref_audio_path: Path to the reference audio (e.g., actress.wav).
            output_audio_path: Destination WAV path. If None, appends '_cloned.wav'.
            device: 'cpu' or 'cuda:0'.

        Returns:
            Resolved path to the cloned audio file.
        """
        in_path = Path(input_audio_path).resolve()
        ref_path = Path(ref_audio_path).resolve()

        if not in_path.exists():
            raise FileNotFoundError(f"Input audio file not found: {in_path}")
        if not ref_path.exists():
            raise FileNotFoundError(f"Reference audio file not found: {ref_path}")

        if output_audio_path:
            out_path = Path(output_audio_path).resolve()
        else:
            out_path = in_path.with_name(f"{in_path.stem}_cloned.wav")

        out_path.parent.mkdir(parents=True, exist_ok=True)

        print("\n" + "=" * 80)
        print("VOICE CLONING (TONE COLOR CONVERSION)")
        print(f"Base Audio:      {in_path.name}")
        print(f"Reference Voice: {ref_path.name}")
        print(f"Output File:     {out_path.name}")
        print(f"Device:          {device.upper()}")
        print("=" * 80 + "\n")

        # Setup environment with ffmpeg in PATH
        env = os.environ.copy()
        ffmpeg_dir = VoiceCloner._ensure_ffmpeg_path()
        if ffmpeg_dir:
            env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")
            env["Path"] = ffmpeg_dir + os.pathsep + env.get("Path", "")
            os.environ["PATH"] = env["PATH"]
            os.environ["Path"] = env["Path"]

        # Run openvoice_cli via Python subprocess
        cmd = [
            sys.executable,
            "-m",
            "openvoice_cli",
            "single",
            "-i",
            str(in_path),
            "-r",
            str(ref_path),
            "-o",
            str(out_path),
            "-d",
            device,
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
            if result.stdout:
                print(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            err = (e.stderr or e.stdout or "").strip()
            if "No module named openvoice_cli" in err:
                raise RuntimeError(
                    "openvoice-cli is not installed. Run: pip install openvoice-cli"
                ) from e
            if "WinError 2" in err or "ffmpeg" in err.lower():
                raise RuntimeError(
                    "FFmpeg is missing. Install it via: pip install imageio-ffmpeg"
                ) from e
            raise RuntimeError(f"Voice cloning failed: {err}") from e
        except FileNotFoundError as e:
            raise RuntimeError(
                "Python executable or openvoice-cli not found in path."
            ) from e


        if not out_path.exists():
            raise RuntimeError(f"Voice cloning finished but output file was not created: {out_path}")

        print(f"[Done] Voice cloned audio successfully saved to: {out_path}\n")
        return str(out_path)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Clone voice timbre using OpenVoice.")
    parser.add_argument("--input", "-i", required=True, help="Path to base TTS audio WAV")
    parser.add_argument("--ref", "-r", required=True, help="Path to reference voice clip WAV")
    parser.add_argument("--output", "-o", default=None, help="Path to save cloned audio WAV")
    parser.add_argument("--device", "-d", default="cpu", choices=["cpu", "cuda:0"], help="Device to use")
    args = parser.parse_args()

    VoiceCloner.clone(
        input_audio_path=args.input,
        ref_audio_path=args.ref,
        output_audio_path=args.output,
        device=args.device,
    )


if __name__ == "__main__":
    main()
