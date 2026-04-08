def add_silence(pcm_bytes, seconds=0.3):
    num_samples = int(seconds * 22050)
    silence = b"\x00\x00" * num_samples  # 16-bit PCM silence
    return silence + silence + pcm_bytes + silence