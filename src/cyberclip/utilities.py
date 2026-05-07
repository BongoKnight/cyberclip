import re


def clean_tsv(new_text: str, text: str):
    """If new_text is a TSV value that starts with text as a first field, returns everythings except this field

    Code exemple ::
    clean_tsv("a\tbaba", "a")
    >>> "baba"
    clean_tsv("b\tbaba", "a")
    >>> "b\tbaba"
    """
    result = new_text
    if new_text.startswith(f"{text}\t"):
        result = re.sub("^" + re.escape(text) + "\t", "", new_text)
    return result


def find_delimiter(text: str, default: str = ",") -> str:
    if not text or not text.strip():
        return default

    sample = text[:5000]
    candidates = (",", ";", "\t", "|")
    quote_chars = {'"', "'", "“", "”", "‘", "’"}

    def unwrap_full_line_quotes(line: str) -> str:
        matching = {'"': '"', "'": "'", "“": "”", "‘": "’"}
        if len(line) >= 2 and line[0] in matching and line[-1] == matching[line[0]]:
            return line[1:-1].strip()
        return line

    lines = []
    for raw_line in sample.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lines.append(unwrap_full_line_quotes(line))
        if len(lines) == 20:
            break

    if len(lines) < 2:
        return default

    def count_delimiter_outside_quotes(line: str, delimiter: str) -> int:
        count = 0
        in_quote = False
        current_quote = None

        for char in line:
            if char in quote_chars:
                if in_quote and char == current_quote:
                    in_quote = False
                    current_quote = None
                elif not in_quote:
                    in_quote = True
                    current_quote = char
                continue

            if not in_quote and char == delimiter:
                count += 1

        return count

    best_delimiter = default
    best_score = -1
    best_max_count = -1

    for delimiter in candidates:
        counts = [count_delimiter_outside_quotes(line, delimiter) for line in lines]
        non_zero_counts = [c for c in counts if c > 0]

        if not non_zero_counts:
            continue

        non_zero_lines = len(non_zero_counts)
        most_common_count = max(set(non_zero_counts), key=non_zero_counts.count)
        consistent_lines = sum(1 for c in non_zero_counts if c == most_common_count)
        max_count = max(non_zero_counts)

        score = consistent_lines * 2 + non_zero_lines

        if score > best_score or (score == best_score and max_count > best_max_count):
            best_delimiter = delimiter
            best_score = score
            best_max_count = max_count

    return best_delimiter if best_score >= 0 else default


def get_rectangle_text(text: str, max_width: int, max_height: int):
    clean_text = ""
    lines = text.splitlines()
    nb_lines = len(lines)
    clean_text = "\n".join(
        [
            line[0 : min(len(line), max_width)]
            for line in lines[0 : min(nb_lines, max_height)]
        ]
    )
    return clean_text
