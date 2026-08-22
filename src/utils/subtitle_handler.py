import re


def seconds_to_srt_timestamp(seconds: float) -> str:
    """
    Converts seconds to the SRT timestamp format (HH:MM:SS,ms).

    Args:
        seconds (float): The time in seconds to be converted.

    Returns:
        str: The formatted timestamp as a string in SRT format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def tokenize_with_punctuation(text: str):
    """
    Tokenizes a text into words and punctuation marks, preserving their order.

    Args:
        text (str): The text to tokenize.

    Returns:
        list[str]: A list of tokens, where words and punctuation marks are separate.
    """
    return re.findall(r"\w+|[^\w\s]+", text)


def align_words_with_punctuation(words, full_text):
    """
    Aligns a list of word objects with the punctuated tokens from the full text.

    Args:
        words (list): A list of word objects, each containing `word`, `start`, and `end`.
        full_text (str): The full transcript text with punctuation.

    Returns:
        list[tuple]: A list of tuples where each tuple contains (start, end, word_with_punctuation).
    """
    punct_tokens = tokenize_with_punctuation(full_text)
    aligned_words = []
    pt_idx = 0

    for w_obj in words:
        base_word = None
        while pt_idx < len(punct_tokens):
            token = punct_tokens[pt_idx]
            pt_idx += 1
            if re.match(r"\w+", token, flags=re.UNICODE):
                base_word = token
                if pt_idx < len(punct_tokens):
                    next_token = punct_tokens[pt_idx]
                    if re.match(r"[^\w\s]+", next_token):
                        base_word += next_token
                        pt_idx += 1
                break

        if base_word is None:
            base_word = w_obj.word

        aligned_words.append((w_obj.start, w_obj.end, base_word))

    # Append any remaining tokens using spaces and then remove extra spaces before punctuation.
    if pt_idx < len(punct_tokens) and aligned_words:
        remaining = " ".join(punct_tokens[pt_idx:])
        remaining = re.sub(r'\s+([^\w\s])', r'\1', remaining)
        start, end, word_with_punc = aligned_words[-1]
        # Insert a space if needed
        if word_with_punc and remaining and word_with_punc[-1].isalnum() and remaining[0].isalnum():
            aligned_words[-1] = (start, end, word_with_punc + " " + remaining)
        else:
            aligned_words[-1] = (start, end, word_with_punc + remaining)

    return aligned_words


def format_srt_from_aligned_words(aligned_words, max_words_per_cue=10, max_chars_per_cue=40):
    """
    Formats a list of aligned words into SRT subtitle format and returns cues.

    Args:
        aligned_words (list[tuple]): A list of tuples containing (start, end, word_with_punctuation).
        max_words_per_cue (int): Maximum number of words allowed per subtitle cue.
        max_chars_per_cue (int): Maximum number of characters allowed per subtitle cue.

    Returns:
        tuple: A tuple containing:
            - str: The SRT-formatted subtitle text.
            - list: A list of cues, where each cue is a tuple (start, end, text).
    """
    cues = []
    current_words = []

    def flush_cue():
        """
        Flushes the current buffered words into a subtitle cue.
        """
        nonlocal current_words
        if not current_words:
            return
        start_time = current_words[0][0]
        end_time = current_words[-1][1]
        cue_text = " ".join(w[2] for w in current_words)
        cues.append((start_time, end_time, cue_text))
        current_words = []

    for w_data in aligned_words:
        start, end, w_text = w_data
        tentative_line = " ".join([cw[2] for cw in current_words] + [w_text])
        if (len(current_words) + 1 > max_words_per_cue) or (len(tentative_line) > max_chars_per_cue):
            flush_cue()
            current_words = [w_data]
        else:
            current_words.append(w_data)

    flush_cue()

    # Adjust the duration of the last one if it is too short
    if cues:
        last_start, last_end, last_text = cues[-1]
        min_duration = 2.0  # minimum duration in seconds for the last caption
        if (last_end - last_start) < min_duration:
            last_end = last_start + min_duration
            cues[-1] = (last_start, last_end, last_text)

    srt_content = ""
    for i, (start, end, text) in enumerate(cues, start=1):
        srt_content += (
            f"{i}\n"
            f"{seconds_to_srt_timestamp(start)} --> {seconds_to_srt_timestamp(end)}\n"
            f"{text}\n\n"
        )

    return srt_content, cues
