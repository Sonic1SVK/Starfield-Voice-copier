import re

raw_text = """
Character lines. Rossie is a woman—let’s turn her into a man. The model is starting to load into VRAM; this might take a few minutes on the first run. Keep an eye on GPU usage. In the meantime, let’s process the character lines. The first 16 lines are already underway—that’s the first batch. I had to reduce the batch size because the VRAM was overflowing. If you set the batch size too high, the GPU can’t keep up and starts using the PC’s system RAM, which you’ll definitely notice—the system will start swapping. That’s better now. The batch size was too big. We’re at 45—halfway there. Finding the right balance for your specific hardware takes a bit of time; it’s not just a "press a button and forget about it" kind of thing. We’re at 81 out of 112, with about 51 seconds left. Done! 128 lines in about 8 minutes—including my own testing. It doesn’t sound drunk; let’s change that—we’ll switch to mode C. If you change the voice, you have to overwrite the previously generated .wav files. The video is already 26 minutes of pure boredom, but hey, you asked for a tutorial, so here it is! :D We’re halfway through. At least you get to see how to troubleshoot issues—63 out of 128 done. It’s all about getting the settings right. On a CPU, 128 lines would probably take an hour or so. We’re almost finished; I’ll play them back in a moment. Let me listen to a few. It should sound fine now. I mean, if that didn’t sound like a drunk person, I honestly don’t know what does! :D Let me play it again. If you want it to sound even more like a drunk person, you’ll need to write it that way in the dialogue itself. If you write it the way the AI wrote it in the prompt, that’s exactly how it’s going to sound. "Ah, hold on... hold on a second, lads, listen to this—you're never gonna believe it! I was just... just sitting there in the Astral Lounge, right? Minding me own business, having a quiet little sip of Bog's Grog... when this, this absolute gobshite from New Atlantis knocks me Chunks right off the table! Straight onto the floor! Well, I... I completely lost the head, didn't I? Threw a wild right hook, smashed three chairs, and next thing I know—hic—half of Neon security is chasing me down the docks! Still got me drink though... ha! Best night in the Settled Systems, I swear to God!" Get it? Alright, jokes aside. Hopefully, that helped you out. It was a bit of a bore, but I can show you how to create .wem files and generate facial expressions using FaceGen via the Creation Kit (CK). It’s lip-syncing—meaning the character will react and articulate according to the text. So, if you write it correctly—for instance, specifying that the character is very angry—they’ll have both the voice and the facial expression to match. That’s a wrap!
""".strip()

TOTAL_DURATION_SEC = 38 * 60 + 8
MIN_SUB_DURATION = 4.0
MAX_SUB_DURATION = 10.0


def format_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def split_into_blocks(text: str, max_chars: int = 130) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r'(?<=[.!?…"])\s+', cleaned)

    blocks = []
    current = ""

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        if len(sent) > max_chars:
            parts = re.split(r"(?<=[,;—:])\s+", sent)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if current and len(current) + 1 + len(part) <= max_chars:
                    current += " " + part
                else:
                    if current:
                        blocks.append(current)
                    current = part
            continue

        if current and len(current) + 1 + len(sent) <= max_chars:
            current += " " + sent
        else:
            if current:
                blocks.append(current)
            current = sent

    if current:
        blocks.append(current)

    return blocks


def build_srt(text: str, output_file: str = "subtitles.srt", total_duration: float = TOTAL_DURATION_SEC):
    blocks = split_into_blocks(text)
    if not blocks:
        print("Ziadny text na spracovanie.")
        return

    step = total_duration / len(blocks)

    with open(output_file, "w", encoding="utf-8") as f:
        for i, block in enumerate(blocks, start=1):
            start_sec = (i - 1) * step
            duration = max(MIN_SUB_DURATION, min(step - 0.3, MAX_SUB_DURATION))
            end_sec = min(start_sec + duration, total_duration - 0.1)
            if end_sec <= start_sec:
                end_sec = start_sec + 2.0

            f.write(f"{i}\n")
            f.write(f"{format_srt_time(start_sec)} --> {format_srt_time(end_sec)}\n")
            f.write(f"{block}\n\n")

    print(f"Vygenerovanych {len(blocks)} titulkov do suboru '{output_file}'.")


if __name__ == "__main__":
    build_srt(raw_text, "subtitles.srt", TOTAL_DURATION_SEC)
