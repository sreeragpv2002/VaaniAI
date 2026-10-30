import re
import unicodedata
import numpy as np
import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

MODEL_ID = "ai4bharat/indic-parler-tts"
device = "cuda:0" if torch.cuda.is_available() else "cpu"

print("Using device:", device)

# Load model and tokenizers
print("Loading model and tokenizers...")
model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL_ID).to(device)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
description_tokenizer = AutoTokenizer.from_pretrained(
    model.config.text_encoder._name_or_path
)

# Standard description format for Harish (Male voice in Indic-Parler-TTS)
# Alternative female voice: replace "Harish speaks" with "Anjali speaks"
description = (
    "Harish speaks at a moderate pace with a clear, warm voice in a "
    "close-sounding environment. The recording is of very high quality, "
    "with minimal ambient noise."
)

description_inputs = description_tokenizer(
    description, return_tensors="pt"
).to(device)

# Load raw text from file
text_file_path = r"C:\Users\sreer\Downloads\MalayalamTTS\malayalam_corrected_v2.txt"
with open(text_file_path, "r", encoding="utf-8") as f:
    raw_text = f.read()


# Normalize Unicode characters
text = unicodedata.normalize("NFC", raw_text)

def split_into_chunks(text: str):
    """Split long text into sentence-sized chunks suitable for Parler-TTS."""
    # Split by quotes, punctuation marks (. ! ? : \n)
    segments = re.split(r'(?<=[.!?\n])\s+', text)
    cleaned = []
    for s in segments:
        s = s.strip()
        if not s:
            continue
        # If segment is still too long (> 150 characters), break further by commas or pauses
        if len(s) > 150:
            sub = re.split(r'(?<=[,;])\s+', s)
            for part in sub:
                part = part.strip()
                if part:
                    cleaned.append(part)
        else:
            cleaned.append(s)
    return cleaned

chunks = split_into_chunks(text)
print(f"Total chunks to synthesize: {len(chunks)}")

sample_rate = model.config.sampling_rate
# 300ms pause between sentences
sentence_pause = np.zeros(int(sample_rate * 0.30), dtype=np.float32)
audio_chunks = []

for i, chunk in enumerate(chunks, 1):
    print(f"[{i}/{len(chunks)}] Synthesizing: {chunk[:45]}...")
    
    text_inputs = tokenizer(chunk, return_tensors="pt").to(device)
    
    with torch.inference_mode():
        output = model.generate(
            input_ids=description_inputs.input_ids,
            attention_mask=description_inputs.attention_mask,
            prompt_input_ids=text_inputs.input_ids,
            prompt_attention_mask=text_inputs.attention_mask,
        )
    
    audio_segment = output.cpu().numpy().squeeze()
    audio_chunks.append(audio_segment)
    audio_chunks.append(sentence_pause)

# Concatenate all segments into single audio file
final_audio = np.concatenate(audio_chunks)

output_filename = "malayalam_male.wav"
sf.write(output_filename, final_audio, sample_rate)
print(f"\nCompleted! Generated clear audio saved to: {output_filename}")
