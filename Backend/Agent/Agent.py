




def terminal(input_text, timeout_s=None):
    import subprocess

    if not input_text:
        return "<error>Missing command.</error>"

    command = (input_text or "").strip()
    if not command:
        return "<error>Missing command.</error>"

    if timeout_s is None:
        timeout_s = 100
    try:
        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return "<error>Command timed out.</error>"
    except OSError as exc:
        return f"<error>Unable to run command: {exc}</error>"

    def _truncate_tokens(text, max_tokens=10000, start_tokens=4000, middle_tokens=1000, end_tokens=5000):
        if not text:
            return text
        token_estimate = max(0, int((len(text) + 3) / 4))
        if token_estimate <= max_tokens:
            return text
        start_chars = max(0, start_tokens * 4)
        middle_chars = max(0, middle_tokens * 4)
        end_chars = max(0, end_tokens * 4)
        start_part = text[:start_chars]
        end_part = text[-end_chars:] if end_chars else ""
        mid_start = max(0, (len(text) - middle_chars) // 2)
        mid_part = text[mid_start : mid_start + middle_chars] if middle_chars else ""
        return start_part + "\n...\n" + mid_part + "\n...\n" + end_part

    stdout = _truncate_tokens(completed.stdout or "")
    stderr = _truncate_tokens(completed.stderr or "")
    code = completed.returncode

    return (
        "<terminal>\n"
        f"  <exit_code>{code}</exit_code>\n"
        "  <stdout>\n"
        f"{stdout}"
        "  </stdout>\n"
        "  <stderr>\n"
        f"{stderr}"
        "  </stderr>\n"
        "</terminal>"
    )


def _is_ignored_path(path):
    import os

    return os.path.basename(path) == ".DS_Store"




def extract_signatures(input_text, from_line=None, to_line=None):
    import os
    import ast
    import re

    file_path = (input_text or "").strip()
    if not file_path:
        return "<error>Missing file path.</error>"
    if _is_ignored_path(file_path):
        return "<error>Ignored file.</error>"
    if _is_ignored_path(file_path):
        return "<error>Ignored file.</error>"
    if _is_ignored_path(file_path):
        return "<error>Ignored file.</error>"
    if _is_ignored_path(file_path):
        return "<error>Ignored file.</error>"
    if _is_ignored_path(file_path):
        return "<error>Ignored file.</error>"

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except FileNotFoundError:
        return f"<error>File not found: {file_path}</error>"
    except OSError as exc:
        return f"<error>Unable to read file: {file_path} ({exc})</error>"

    ext = os.path.splitext(file_path)[1].lower()
    lines = content.splitlines()
    results = []

    if ext == ".py":
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    line_no = getattr(node, "lineno", None)
                    if line_no is not None and 1 <= line_no <= len(lines):
                        results.append((line_no, lines[line_no - 1]))
                if isinstance(node, ast.ClassDef):
                    line_no = getattr(node, "lineno", None)
                    if line_no is not None and 1 <= line_no <= len(lines):
                        results.append((line_no, lines[line_no - 1]))
                if isinstance(node, ast.Return):
                    line_no = getattr(node, "lineno", None)
                    if line_no is not None and 1 <= line_no <= len(lines):
                        results.append((line_no, lines[line_no - 1]))
        except SyntaxError:
            def_pattern = re.compile(
                r"^\s*(async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("
            )
            for idx, line in enumerate(lines, start=1):
                match = def_pattern.search(line)
                if match:
                    results.append((idx, line))
                elif re.match(r"^\s*return\b", line):
                    results.append((idx, line))

    elif ext in (".js", ".jsx", ".ts", ".tsx"):
        func_patterns = [
            re.compile(r"^\s*function\s+[A-Za-z0-9_$]+\s*\("),
            re.compile(
                r"^\s*(?:const|let|var)\s+[A-Za-z0-9_$]+(?:\s*:\s*[^=]+)?\s*=\s*function\s*\("
            ),
            re.compile(
                r"^\s*(?:const|let|var)\s+[A-Za-z0-9_$]+(?:\s*:\s*[^=]+)?\s*=\s*(?:async\s*)?\(.*\)\s*=>"
            ),
            re.compile(r"^\s*export\s+(?:default\s+)?function\s+[A-Za-z0-9_$]+\s*\("),
            re.compile(r"^\s*export\s+default\s+.+"),
            re.compile(r"^\s*export\s+\{.*\}\s*;?\s*$"),
        ]
        for idx, line in enumerate(lines, start=1):
            for pattern in func_patterns:
                if pattern.search(line):
                    results.append((idx, line))
                    break

    elif ext in (".html", ".htm"):
        tag_pattern = re.compile(r"<\s*(/?)\s*([A-Za-z][A-Za-z0-9:-]*)")
        for idx, line in enumerate(lines, start=1):
            for match in tag_pattern.finditer(line):
                slash = "/" if match.group(1) == "/" else ""
                indent = line[: match.start()]
                results.append((idx, f"{indent}<{slash}{match.group(2)}>"))

    elif ext == ".css":
        class_pattern = re.compile(r"\.([A-Za-z0-9_-]+)")
        for idx, line in enumerate(lines, start=1):
            for match in class_pattern.finditer(line):
                results.append((idx, f".{match.group(1)}"))

    else:
        return "<error>Unsupported file type for signature extraction.</error>"

    if from_line is not None or to_line is not None:
        try:
            start = int(from_line) if from_line is not None else 1
            end = int(to_line) if to_line is not None else len(lines)
        except ValueError:
            return "<error>Invalid range.</error>"
        if start > end:
            start, end = end, start
        start = max(1, start)
        end = min(len(lines), end)
        results = [item for item in results if start <= item[0] <= end]

    if not results:
        return f"<signature path=\"{file_path}\"><content></content></signature>"

    results.sort(key=lambda item: item[0])
    width = max(3, len(str(max(n for n, _ in results))))
    content_lines = []
    prev_line = None
    for n, text in results[:600]:
        if prev_line is not None and n - prev_line > 1:
            content_lines.append("  ...")
        content_lines.append(f"  {n:>{width}} | {text}")
        prev_line = n

    remaining = max(0, len(results) - 600)
    if remaining > 0:
        content_lines.append(f"[+ {remaining}]")
    content_block = "\n".join(content_lines)

    return (
        f"<signature path=\"{file_path}\">\n"
        "<content>\n"
        f"{content_block}\n"
        "</content>\n"
        "</signature>"
    )




def file_read(input_text, from_line=None, to_line=None):
    import os
    import math
    import re
    import subprocess
    import json

    file_path = (input_text or "").strip()
    if not file_path:
        return "<error>Missing file path.</error>"
    if _is_ignored_path(file_path):
        return "<error>Ignored file.</error>"

    def _extract_pdf_text(pdf_path):
        import base64
        import zlib

        try:
            with open(pdf_path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            return None, f"<error>File not found: {pdf_path}</error>"
        except OSError as exc:
            return None, f"<error>Unable to read file: {pdf_path} ({exc})</error>"

        stream_pattern = re.compile(
            br"<<(.*?)>>\s*stream\r?\n(.*?)\r?\nendstream", re.DOTALL
        )
        streams = stream_pattern.findall(data)
        if not streams:
            return "", None

        def _decode_pdf_string(s):
            out = []
            i = 0
            while i < len(s):
                ch = s[i]
                if ch == 92:  # backslash
                    if i + 1 < len(s):
                        nxt = s[i + 1]
                        if nxt in b"nrtbf":
                            out.append(
                                {
                                    ord("n"): "\n",
                                    ord("r"): "\r",
                                    ord("t"): "\t",
                                    ord("b"): "\b",
                                    ord("f"): "\f",
                                }[nxt]
                            )
                            i += 2
                            continue
                        if 48 <= nxt <= 55:
                            j = i + 1
                            octal = []
                            while j < len(s) and len(octal) < 3 and 48 <= s[j] <= 55:
                                octal.append(s[j])
                                j += 1
                            try:
                                out.append(chr(int(bytes(octal), 8)))
                            except ValueError:
                                pass
                            i = j
                            continue
                        out.append(chr(nxt))
                        i += 2
                        continue
                out.append(chr(ch))
                i += 1
            return "".join(out)

        def _decode_ascii_hex(raw):
            raw = re.sub(br"\s+", b"", raw)
            if b">" in raw:
                raw = raw.split(b">", 1)[0]
            if len(raw) % 2 == 1:
                raw += b"0"
            try:
                return bytes.fromhex(raw.decode("ascii"))
            except ValueError:
                return b""

        def _decode_ascii85(raw):
            if b"<~" in raw and b"~>" in raw:
                raw = raw.split(b"<~", 1)[1].split(b"~>", 1)[0]
            try:
                return base64.a85decode(raw, adobe=False, ignorechars=b" \t\r\n")
            except Exception:
                return b""

        def _apply_filters(stream_data, filters):
            data_out = stream_data
            for flt in filters:
                if flt in ("FlateDecode", "Fl"):
                    try:
                        data_out = zlib.decompress(data_out)
                    except Exception:
                        return b""
                elif flt in ("ASCII85Decode", "A85"):
                    data_out = _decode_ascii85(data_out)
                elif flt in ("ASCIIHexDecode", "AHx"):
                    data_out = _decode_ascii_hex(data_out)
                else:
                    return b""
            return data_out

        def _parse_filters(dict_bytes):
            filters = []
            m = re.search(br"/Filter\s*\[(.*?)\]", dict_bytes, flags=re.DOTALL)
            if m:
                names = re.findall(br"/([A-Za-z0-9]+)", m.group(1))
                filters = [n.decode("ascii", errors="ignore") for n in names]
            else:
                m = re.search(br"/Filter\s*/([A-Za-z0-9]+)", dict_bytes)
                if m:
                    filters = [m.group(1).decode("ascii", errors="ignore")]
            return filters

        text_parts = []
        for dict_bytes, stream in streams:
            filters = _parse_filters(dict_bytes)
            if filters:
                decoded = _apply_filters(stream, filters)
                if not decoded:
                    continue
                stream = decoded

            i = 0
            in_string = False
            buf = []
            nesting = 0
            while i < len(stream):
                ch = stream[i]
                if not in_string:
                    if ch == 40:  # '('
                        in_string = True
                        nesting = 1
                        buf = []
                    i += 1
                    continue
                if ch == 92:  # backslash
                    if i + 1 < len(stream):
                        buf.append(ch)
                        buf.append(stream[i + 1])
                        i += 2
                        continue
                if ch == 40:  # '('
                    nesting += 1
                    buf.append(ch)
                elif ch == 41:  # ')'
                    nesting -= 1
                    if nesting == 0:
                        text_parts.append(_decode_pdf_string(bytes(buf)))
                        in_string = False
                    else:
                        buf.append(ch)
                else:
                    buf.append(ch)
                i += 1

        extracted = "\n".join([t for t in text_parts if t.strip()])
        return extracted, None

    is_pdf = file_path.lower().endswith(".pdf")
    is_json = file_path.lower().endswith(".json")
    if is_pdf:
        content = None
        try:
            completed = subprocess.run(
                ["pdftotext", file_path, "-"],
                text=True,
                capture_output=True,
                timeout=30,
            )
            if completed.returncode == 0 and completed.stdout:
                content = completed.stdout
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            content = None

        if content is None:
            content, err = _extract_pdf_text(file_path)
            if err:
                return err
            if content is None:
                return "<error>Unable to extract PDF text.</error>"
    elif is_json:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                raw_json = f.read()
            data = json.loads(raw_json)
        except FileNotFoundError:
            return f"<error>File not found: {file_path}</error>"
        except (OSError, json.JSONDecodeError) as exc:
            return f"<error>Unable to read JSON: {file_path} ({exc})</error>"

        def _preview_value(val, max_chars=100):
            text = json.dumps(val, ensure_ascii=False)
            if len(text) <= max_chars:
                return text
            remaining = max(0, len(text) - max_chars)
            return f"{text[:max_chars]}... [+ {remaining} chars]"

        if isinstance(data, dict):
            pairs = []
            for k, v in data.items():
                pairs.append(f'    "{k}" : "{_preview_value(v)}"')
            content = "{\n" + "\n".join(pairs) + "\n}"
        else:
            content = _preview_value(data)
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except FileNotFoundError:
            return f"<error>File not found: {file_path}</error>"
        except OSError as exc:
            return f"<error>Unable to read file: {file_path} ({exc})</error>"

    lines = content.splitlines()
    total_lines = len(lines)
    max_lines = 600

    start_line = 1
    end_line = total_lines
    if from_line is not None:
        start_line = max(1, int(from_line))
    if to_line is not None:
        end_line = min(total_lines, int(to_line))
    if start_line > end_line:
        start_line, end_line = end_line, start_line

    requested_count = max(0, end_line - start_line + 1)
    lines_returned = min(requested_count, max_lines)
    actual_end = start_line + lines_returned - 1 if lines_returned else start_line - 1
    percent_of_file = (lines_returned / total_lines * 100.0) if total_lines > 0 else 0.0

    try:
        file_size_bytes = os.path.getsize(file_path)
        file_size_kb = f"{file_size_bytes / 1024:.1f}KB"
    except OSError:
        file_size_kb = "unknown"

    content_lines = []
    if lines_returned:
        if is_pdf:
            content_lines.extend(lines[start_line - 1 : actual_end])
        else:
            width = max(3, len(str(total_lines)))
            for idx, line in enumerate(
                lines[start_line - 1 : actual_end], start=start_line
            ):
                content_lines.append(f"  {idx:>{width}} | {line}")

    remaining = max(0, total_lines - actual_end)
    if remaining > 0:
        content_lines.append(
            f"\n[+ {remaining} Lines] ({actual_end + 1} - {total_lines}) still available"
        )

    content_block = "\n".join(content_lines)
    returned_char_count = len(content_block)
    token_estimate = math.ceil(returned_char_count / 4) if returned_char_count else 0
    if total_lines == 0:
        range_label = "empty"
    else:
        range_label = (
            "full"
            if lines_returned == total_lines and start_line == 1
            else f"{start_line}-{actual_end}"
        )

    return (
        f'<file path="{file_path}">\n\n'
        '"""\n'
        "<metadata>\n"
        f"  <total_lines>{total_lines}</total_lines>\n"
        f"  <lines_returned>{lines_returned}</lines_returned>\n"
        f"  <percent_of_file>{percent_of_file}%</percent_of_file>\n"
        f"  <range>{range_label}</range>\n"
        f"  <char_count>{returned_char_count:,}</char_count>\n"
        f"  <token_estimate>{token_estimate:,}</token_estimate>\n"
        f"  <file_size>{file_size_kb}</file_size>\n"
        "</metadata>\n\n"
        "<content>\n"
        f"{content_block}\n"
        "</content>\n\n"
        "</file>\n"
        '"""'
    )

def fuzzy_search():
    pass

def grep_search(file_path, find_text, context=2, from_line=None, to_line=None, max_matches=100):
    import re

    if not file_path:
        return "<error>Missing file path.</error>"
    if not find_text:
        return "<error>Missing find text.</error>"

    if isinstance(find_text, (list, tuple)):
        find_texts = [t for t in find_text if t]
    else:
        find_texts = [find_text]
    if not find_texts:
        return "<error>Missing find text.</error>"
    if len(find_texts) > 10:
        return "<error>Too many find terms (max 10).</error>"

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except FileNotFoundError:
        return f"<error>File not found: {file_path}</error>"
    except OSError as exc:
        return f"<error>Unable to read file: {file_path} ({exc})</error>"

    lines = content.splitlines()
    total_lines = len(lines)
    start = 1
    end = total_lines
    if from_line is not None:
        try:
            start = max(1, int(from_line))
        except ValueError:
            return "<error>Invalid from value.</error>"
    if to_line is not None:
        try:
            end = min(total_lines, int(to_line))
        except ValueError:
            return "<error>Invalid to value.</error>"
    if start > end:
        start, end = end, start

    matches = []
    for i, line in enumerate(lines):
        if i < start - 1 or i > end - 1:
            continue
        if any(t in line for t in find_texts):
            matches.append(i)
            if len(matches) >= max_matches:
                break
    if not matches:
        return (
            f"<search path=\"{file_path}\">\n"
            "<content>\n"
            "No results found\n"
            "</content>\n"
            "</search>"
        )

    ranges = []
    for idx in matches:
        r_start = max(0, idx - context, start - 1)
        r_end = min(len(lines) - 1, idx + context, end - 1)
        if not ranges or r_start > ranges[-1][1] + 1:
            ranges.append([r_start, r_end])
        else:
            ranges[-1][1] = max(ranges[-1][1], r_end)

    colors = [
        "\033[42m",  # green
        "\033[41m",  # red
        "\033[44m",  # blue
        "\033[103m",  # yellow
        "\033[100m",  # grey
        "\033[45m",  # magenta
        "\033[46m",  # cyan
        "\033[102m",  # light green
        "\033[101m",  # light red
        "\033[104m",  # light blue
    ]
    color_map = {}
    for idx, term in enumerate(find_texts):
        color_map[term] = colors[idx % len(colors)]
    pattern_terms = sorted(set(find_texts), key=len, reverse=True)
    highlight_re = re.compile("|".join(re.escape(t) for t in pattern_terms))
    width = max(3, len(str(len(lines))))
    content_lines = []
    content_lines_color = []
    line_count = 0
    for range_start, range_end in ranges:
        for i in range(range_start, range_end + 1):
            if line_count >= 600:
                break
            if content_lines and not content_lines[-1].startswith("  ..."):
                last_line = content_lines[-1]
                try:
                    last_num = int(last_line.split("|", 1)[0].strip())
                except ValueError:
                    last_num = None
                if last_num is not None and i + 1 - last_num > 1:
                    content_lines.append("  ...")
                    content_lines_color.append("  ...")
                    line_count += 1
                    if line_count >= 600:
                        break
            line = lines[i]
            if any(t in line for t in find_texts):
                line_plain = highlight_re.sub(
                    lambda m: f"👉{m.group(0)}👈",
                    line,
                )
                line_color = highlight_re.sub(
                    lambda m: (
                        "👉"
                        + f"{color_map.get(m.group(0), '\033[103m')}"
                        + m.group(0)
                        + "\033[0m"
                        + "👈"
                    ),
                    line,
                )
            else:
                line_plain = line
                line_color = line
            content_lines.append(f"  {i + 1:>{width}} | {line_plain}")
            content_lines_color.append(f"  {i + 1:>{width}} | {line_color}")
            line_count += 1
        if line_count >= 600:
            break

    remaining = max(0, sum(r_end - r_start + 1 for r_start, r_end in ranges) - line_count)
    if remaining > 0:
        content_lines.append(f"[+ {remaining}]")
        content_lines_color.append(f"[+ {remaining}]")
    content_lines.append(f"Found: {len(matches)}")
    content_lines_color.append(f"Found: {len(matches)}")
    for term in find_texts:
        term_count = sum(1 for line in lines[start - 1 : end] if term in line)
        content_lines.append(f"Found {term}: {term_count}")
        content_lines_color.append(f"Found {term}: {term_count}")

    content_block = "\n".join("  " + line for line in content_lines)
    content_block_color = "\n".join("  " + line for line in content_lines_color)
    return (
        f"<search path=\"{file_path}\">\n"
        "<content>\n"
        f"{content_block}\n"
        "</content>\n"
        "</search>"
    )

def regex_search(file_path, patterns, context=2, from_line=None, to_line=None, max_matches=100):
    import re

    if not file_path:
        return "<error>Missing file path.</error>"
    if not patterns:
        return "<error>Missing find text.</error>"

    if isinstance(patterns, (list, tuple)):
        regex_list = [p for p in patterns if p]
    else:
        regex_list = [patterns]
    if not regex_list:
        return "<error>Missing find text.</error>"
    if len(regex_list) > 10:
        return "<error>Too many find terms (max 10).</error>"

    try:
        compiled = [re.compile(p) for p in regex_list]
    except re.error as exc:
        return f"<error>Invalid regex: {exc}</error>"

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except FileNotFoundError:
        return f"<error>File not found: {file_path}</error>"
    except OSError as exc:
        return f"<error>Unable to read file: {file_path} ({exc})</error>"

    lines = content.splitlines()
    total_lines = len(lines)
    start = 1
    end = total_lines
    if from_line is not None:
        try:
            start = max(1, int(from_line))
        except ValueError:
            return "<error>Invalid from value.</error>"
    if to_line is not None:
        try:
            end = min(total_lines, int(to_line))
        except ValueError:
            return "<error>Invalid to value.</error>"
    if start > end:
        start, end = end, start

    matches = []
    for i, line in enumerate(lines):
        if i < start - 1 or i > end - 1:
            continue
        if any(c.search(line) for c in compiled):
            matches.append(i)
            if len(matches) >= max_matches:
                break
    if not matches:
        return (
            f"<search path=\"{file_path}\">\n"
            "<content>\n"
            "No results found\n"
            "</content>\n"
            "</search>"
        )

    ranges = []
    for idx in matches:
        r_start = max(0, idx - context, start - 1)
        r_end = min(len(lines) - 1, idx + context, end - 1)
        if not ranges or r_start > ranges[-1][1] + 1:
            ranges.append([r_start, r_end])
        else:
            ranges[-1][1] = max(ranges[-1][1], r_end)

    colors = [
        "\033[42m",  # green
        "\033[41m",  # red
        "\033[44m",  # blue
        "\033[103m",  # yellow
        "\033[100m",  # grey
        "\033[45m",  # magenta
        "\033[46m",  # cyan
        "\033[102m",  # light green
        "\033[101m",  # light red
        "\033[104m",  # light blue
    ]
    color_map = {}
    for idx, pat in enumerate(regex_list):
        color_map[pat] = colors[idx % len(colors)]

    width = max(3, len(str(len(lines))))
    content_lines = []
    content_lines_color = []
    line_count = 0

    for range_start, range_end in ranges:
        for i in range(range_start, range_end + 1):
            if line_count >= 600:
                break
            if content_lines and not content_lines[-1].startswith("  ..."):
                last_line = content_lines[-1]
                try:
                    last_num = int(last_line.split("|", 1)[0].strip())
                except ValueError:
                    last_num = None
                if last_num is not None and i + 1 - last_num > 1:
                    content_lines.append("  ...")
                    content_lines_color.append("  ...")
                    line_count += 1
                    if line_count >= 600:
                        break

            line = lines[i]
            if any(c.search(line) for c in compiled):
                line_plain = line
                line_color = line
                for pat, comp in zip(regex_list, compiled):
                    line_plain = comp.sub(lambda m: f"👉{m.group(0)}👈", line_plain)
                    line_color = comp.sub(
                        lambda m, p=pat: (
                            "👉"
                            + f"{color_map.get(p, '\033[103m')}"
                            + m.group(0)
                            + "\033[0m"
                            + "👈"
                        ),
                        line_color,
                    )
            else:
                line_plain = line
                line_color = line

            content_lines.append(f"  {i + 1:>{width}} | {line_plain}")
            content_lines_color.append(f"  {i + 1:>{width}} | {line_color}")
            line_count += 1
        if line_count >= 600:
            break

    remaining = max(0, sum(r_end - r_start + 1 for r_start, r_end in ranges) - line_count)
    if remaining > 0:
        content_lines.append(f"[+ {remaining}]")
        content_lines_color.append(f"[+ {remaining}]")
    content_lines.append(f"Found: {len(matches)}")
    content_lines_color.append(f"Found: {len(matches)}")
    for pat, comp in zip(regex_list, compiled):
        term_count = sum(
            1
            for line in lines[start - 1 : end]
            if comp.search(line)
        )
        content_lines.append(f"Found {pat}: {term_count}")
        content_lines_color.append(f"Found {pat}: {term_count}")

    content_block = "\n".join("  " + line for line in content_lines)
    content_block_color = "\n".join("  " + line for line in content_lines_color)
    return (
        f"<search path=\"{file_path}\">\n"
        "<content>\n"
        f"{content_block}\n"
        "</content>\n"
        "</search>"
    )

def file_search(input_text):
    if not input_text or "::" not in input_text:
        return "<error>Provide search as: path::text</error>"
    file_path, find_text = input_text.split("::", 1)
    return grep_search(file_path.strip(), find_text.strip())


def file_create(file_path, content_text):
    import os

    if not file_path:
        return "<error>Missing file path.</error>"

    def _next_available_path(path):
        if not os.path.exists(path):
            return path, False
        directory, filename = os.path.split(path)
        base, ext = os.path.splitext(filename)
        idx = 1
        while True:
            candidate = os.path.join(directory, f"{base}({idx}){ext}")
            if not os.path.exists(candidate):
                return candidate, True
            idx += 1

    directory = os.path.dirname(file_path)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as exc:
            return f"<error>Unable to create directory: {directory} ({exc})</error>"

    final_path, renamed = _next_available_path(file_path)
    try:
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(content_text or "")
    except OSError as exc:
        return f"<error>Unable to create file: {final_path} ({exc})</error>"

    if renamed:
        return f"<ok>File already existed, created: {final_path}</ok>"
    return f"<ok>Created file: {final_path}</ok>"


def file_edits(file_path, from_line, to_line, new_text, old_text=None):
    import os

    if not file_path:
        return "<error>Missing file path.</error>"
    has_range = from_line is not None and to_line is not None
    has_old = old_text is not None

    if not has_range and not has_old:
        return "<error>Missing edit selector (lines or old text).</error>"
    if has_range and has_old:
        return "<error>Provide either line range or old text, not both.</error>"
    if has_old and old_text == "":
        return "<error>Old text is empty.</error>"

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except FileNotFoundError:
        return f"<error>File not found: {file_path}</error>"
    except OSError as exc:
        return f"<error>Unable to read file: {file_path} ({exc})</error>"

    had_trailing_newline = content.endswith("\n")

    if has_old:
        if old_text not in content:
            return (
                "<error>Old text not found. "
                "No changes applied.</error>"
            )
        updated_content = content.replace(old_text, new_text)
    else:
        try:
            start_line = int(from_line)
            end_line = int(to_line)
        except ValueError:
            return "<error>Invalid line range.</error>"

        if start_line > end_line:
            start_line, end_line = end_line, start_line
        if start_line < 1:
            start_line = 1

        lines = content.splitlines()
        total_lines = len(lines)

        if total_lines == 0:
            start_line = 1
            end_line = 0
        elif start_line > total_lines:
            start_line = total_lines + 1
            end_line = total_lines
        else:
            end_line = min(end_line, total_lines)

        if new_text == "":
            new_lines = []
        else:
            new_lines = new_text.split("\n")
        before = lines[: start_line - 1]
        after = lines[end_line:]
        updated = before + new_lines + after

        updated_content = "\n".join(updated)
    if had_trailing_newline:
            updated_content += "\n"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
    except OSError as exc:
        return f"<error>Unable to write file: {file_path} ({exc})</error>"

    if has_old:
        return f"<ok>Edited file: {file_path} (text replaced)</ok>"
    return f"<ok>Edited file: {file_path} (lines {start_line}-{end_line})</ok>"



def Actor(messages, system_prompt, model, on_first_token=None, line_prefix=""):
    try:
        from .LLMs import LLM_messages
    except Exception:
        from LLMs import LLM_messages

    history = list(messages)
    if system_prompt:
        history = [{"role": "system", "content": system_prompt}] + history
    return LLM_messages(history, model=model, on_first_token=on_first_token, line_prefix=line_prefix)


def Director(messages, system_prompt, model, on_first_token=None, line_prefix=""):
    try:
        from .LLMs import LLM_messages
    except Exception:
        from LLMs import LLM_messages

    history = list(messages)
    if system_prompt:
        history = [{"role": "system", "content": system_prompt}] + history
    return LLM_messages(history, model=model, on_first_token=on_first_token, line_prefix=line_prefix)





def Tools_handler(input_text):
    import re
    import xml.etree.ElementTree as ET

    if not input_text or "<" not in input_text:
        return ""

    def _normalize_tools_block(text):
        text = re.sub(r"<\s*/\s*tools\s*>", "</tools>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*tools\b", "<tools", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*tool\s*>", "</tools>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*tool\b", "<tools", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*file\s*>", "</file>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*file\s*>", "<file>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*read\s*>", "</read>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*read\b", "<read", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*terminal\s*>", "</terminal>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*terminal\s*>", "<terminal>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*command\s*>", "</command>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*command\s*>", "<command>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*timeout\s*>", "</timeout>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*timeout\s*>", "<timeout>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*edit\s*>", "</edit>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*edit\b", "<edit", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*lines\s*>", "</lines>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*lines\b", "<lines", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*new\s*>", "</new>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*new\s*>", "<new>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*old\s*>", "</old>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*old\s*>", "<old>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*create\s*>", "</create>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*create\b", "<create", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*signature\s*>", "</signature>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*signature\s*>", "<signature>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*search\s*>", "</search>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*search\s*>", "<search>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*/\s*find\s*>", "</find>", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*find\s*>", "<find>", text, flags=re.IGNORECASE)
        return text

    def _escape_command_text(text):
        def _escape(m):
            inner = m.group(1)
            inner = inner.replace("&", "&amp;")
            return f"<command>{inner}</command>"

        return re.sub(
            r"<\s*command\s*>(.*?)<\s*/\s*command\s*>",
            _escape,
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

    def _fallback_handle_tools_block(block_text):
        # Fallback parser for malformed XML (e.g., raw HTML inside <create>).
        outputs = []
        create_pattern = re.compile(
            r"<\s*create\b([^>]*)>(.*?)<\s*/\s*create\s*>",
            re.IGNORECASE | re.DOTALL,
        )
        for attrs, body in create_pattern.findall(block_text):
            file_match = re.search(r'\bfile\s*=\s*"([^"]+)"', attrs, re.IGNORECASE)
            path_match = re.search(r'\bpath\s*=\s*"([^"]+)"', attrs, re.IGNORECASE)
            file_path = (file_match.group(1) if file_match else "").strip()
            if not file_path and path_match:
                file_path = path_match.group(1).strip()
            raw_text = body
            if raw_text.startswith("\n"):
                raw_text = raw_text[1:]
            outputs.append(file_create(file_path, raw_text))
        return "\n\n".join(o for o in outputs if o)

    def _handle_tools_block(normalized_block):
        normalized_block = _escape_command_text(normalized_block)
        try:
            root = ET.fromstring(normalized_block.strip())
        except ET.ParseError as exc:
            fallback = _fallback_handle_tools_block(normalized_block)
            if fallback:
                return fallback
            return f"<error>Malformed tools payload: {exc}</error>"

        read_node = root.find(".//file/read")
        if read_node is not None:
            file_path = read_node.attrib.get("file", "").strip()
            path_attr = read_node.attrib.get("path", "").strip()
            if not file_path and path_attr:
                file_path = path_attr
            from_line = read_node.attrib.get("from")
            to_line = read_node.attrib.get("to")
            return file_read(file_path, from_line=from_line, to_line=to_line)

        edit_node = root.find(".//file/edit")
        if edit_node is not None:
            import textwrap

            file_path = edit_node.attrib.get("file", "").strip()
            path_attr = edit_node.attrib.get("path", "").strip()
            if not file_path and path_attr:
                file_path = path_attr
            lines_node = edit_node.find("lines")
            from_line = lines_node.attrib.get("from") if lines_node is not None else None
            to_line = lines_node.attrib.get("to") if lines_node is not None else None

            def _extract_block_text(node):
                if node is None or node.text is None:
                    return None
                raw = node.text
                if raw.startswith("\n"):
                    raw = raw[1:]
                raw = textwrap.dedent(raw)
                lines = raw.splitlines()
                while lines and lines[-1].strip() == "":
                    lines.pop()
                return "\n".join(lines)

            old_text = _extract_block_text(edit_node.find("old"))

            new_text = _extract_block_text(edit_node.find("new"))
            if new_text is None:
                new_text = ""

            return file_edits(
                file_path, from_line, to_line, new_text, old_text=old_text
            )

        create_node = root.find(".//file/create")
        if create_node is not None:
            import textwrap

            file_path = create_node.attrib.get("file", "").strip()
            path_attr = create_node.attrib.get("path", "").strip()
            if not file_path and path_attr:
                file_path = path_attr

            def _extract_raw_create_text(block_text):
                match = re.search(
                    r"<\s*create\b[^>]*>(.*?)<\s*/\s*create\s*>",
                    block_text,
                    flags=re.IGNORECASE | re.DOTALL,
                )
                return match.group(1) if match else None

            raw_text = _extract_raw_create_text(normalized_block)
            if raw_text is None:
                raw_text = create_node.text or ""
            if raw_text.startswith("\n"):
                raw_text = raw_text[1:]
            content_text = textwrap.dedent(raw_text)
            return file_create(file_path, content_text)

        signature_node = root.find(".//signature/read")
        if signature_node is not None:
            file_path = signature_node.attrib.get("file", "").strip()
            from_line = signature_node.attrib.get("from")
            to_line = signature_node.attrib.get("to")
            return extract_signatures(file_path, from_line=from_line, to_line=to_line)

        search_node = root.find(".//search")
        search_read = root.find(".//search/read")
        if search_read is not None:
            import os

            search_type = ""
            if search_node is not None:
                search_type = search_node.attrib.get("type", "").strip().lower()
            if search_type and search_type not in ("grep", "regex"):
                return "<error>Unsupported search type.</error>"

            file_path = search_read.attrib.get("file", "").strip()
            path_attr = search_read.attrib.get("path", "").strip()
            target = path_attr or file_path
            from_line = search_read.attrib.get("from")
            to_line = search_read.attrib.get("to")
            find_nodes = search_read.findall("find")
            find_texts = []
            for node in find_nodes:
                raw = node.text if node is not None else ""
                if raw is None:
                    raw = ""
                text = raw.strip()
                if text:
                    find_texts.append(text)
            if not find_texts:
                return "<error>Missing find text.</error>"

            if not target:
                return "<error>Missing file or path.</error>"

            if os.path.isdir(target):
                max_lines = 1000
                content_lines = []
                total_files = 0
                included_files = 0
                for root_dir, _, filenames in os.walk(target):
                    filenames = [n for n in filenames if n != ".DS_Store"]
                    filenames.sort()
                    for name in filenames:
                        total_files += 1
                        if len(content_lines) >= max_lines:
                            continue
                        file_full = os.path.join(root_dir, name)
                        try:
                            with open(file_full, "r", encoding="utf-8", errors="replace") as f:
                                file_lines = f.read().splitlines()
                        except OSError:
                            continue

                        included_files += 1
                        content_lines.append(f"== file: {file_full} ==")
                        width = max(3, len(str(len(file_lines))))
                        for idx, line in enumerate(file_lines, start=1):
                            if len(content_lines) >= max_lines:
                                break
                            content_lines.append(f"  {idx:>{width}} | {line}")

                remaining_files = max(0, total_files - included_files)
                content_lines.append(f"Files total: {total_files}")
                content_lines.append(f"Files remaining: {remaining_files}")
                content_block = "\n".join(content_lines)
                return (
                    f"<search path=\"{target}\">\n"
                    "<content>\n"
                    f"{content_block}\n"
                    "</content>\n"
                    "</search>"
                )

            if search_type == "regex":
                return regex_search(
                    target, find_texts, from_line=from_line, to_line=to_line
                )
            return grep_search(
                target, find_texts, from_line=from_line, to_line=to_line
            )

        terminal_nodes = root.findall(".//terminal")
        if terminal_nodes:
            outputs = []
            for terminal_node in terminal_nodes:
                cmd_node = terminal_node.find("command")
                timeout_node = terminal_node.find("timeout")
                if cmd_node is not None:
                    command = cmd_node.text or ""
                else:
                    # Support <terminal>ls</terminal> without <command> wrapper
                    command = terminal_node.text or ""
                command = command.strip()

                timeout_s = None
                if timeout_node is not None and timeout_node.text:
                    try:
                        timeout_s = int(timeout_node.text.strip())
                    except ValueError:
                        outputs.append("<error>Invalid timeout.</error>")
                        continue

                outputs.append(terminal(command, timeout_s=timeout_s))

            return "\n\n".join(o for o in outputs if o)

        return ""

    normalized_all = _normalize_tools_block(input_text)
    normalized_all = re.sub(r"\bFILE\s*=", "file=", normalized_all, flags=re.IGNORECASE)
    normalized_all = re.sub(r"\bPATH\s*=", "path=", normalized_all, flags=re.IGNORECASE)
    normalized_all = re.sub(r"\bFROM\s*=", "from=", normalized_all, flags=re.IGNORECASE)
    normalized_all = re.sub(r"\bTO\s*=", "to=", normalized_all, flags=re.IGNORECASE)
    normalized_all = normalized_all.replace("\x08", "\\b")
    blocks = re.findall(r"<tools\b[^>]*>.*?</tools>", normalized_all, flags=re.DOTALL | re.IGNORECASE)
    if not blocks:
        return ""

    outputs = []
    for block in blocks:
        outputs.append(_handle_tools_block(block))

    combined = "\n\n".join(o for o in outputs if o)
    if not combined:
        return ""
    return f"<output>\n{combined}\n</output>"


def context_manager(input_text):
    pass











def Agent():
    import json
    import os
    import time
    import curses
    import sys
    import threading
    import re

    try:
        from .LLMs import DEFAULT_MODEL, MODEL_OPTIONS
    except Exception:
        from LLMs import DEFAULT_MODEL, MODEL_OPTIONS

    chats_dir = os.path.join(os.path.dirname(__file__), "..", "Chats")
    chats_dir = os.path.abspath(chats_dir)
    os.makedirs(chats_dir, exist_ok=True)

    def _now():
        return time.strftime("%Y-%m-%dT%H:%M:%S")

    def _load_system_prompt(filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read().strip()
        except OSError:
            return ""

    director_system_prompt = _load_system_prompt("system_prompt_1.txt")
    actor_system_prompt = _load_system_prompt("system_prompt_2.txt")

    def _token_estimate(text):
        return max(0, int((len(text) + 3) / 4))

    def _token_bucket(tokens):
        if tokens < 1000:
            return str(tokens)
        k = tokens / 1000.0
        if k.is_integer():
            return f"{int(k)}k"
        return f"{k:.3f}".rstrip("0").rstrip(".") + "k"

    def _count_tools_from_text(text):
        lowered = text.lower()
        return {
            "file_read": len(re.findall(r"<\s*read\b", lowered)),
            "file_edit": len(re.findall(r"<\s*edit\b", lowered)),
            "file_create": len(re.findall(r"<\s*create\b", lowered)),
            "terminal": len(re.findall(r"<\s*terminal\b", lowered)),
            "search": len(re.findall(r"<\s*search\b", lowered)),
            "signature": len(re.findall(r"<\s*signature\b", lowered)),
        }

    def _extract_actor_instructions(text):
        pattern = re.compile(
            r"<\s*actor\s*>(.*?)<\s*/\s*actor\s*>",
            re.IGNORECASE | re.DOTALL,
        )
        return [m.strip() for m in pattern.findall(text or "") if m.strip()]

    def _has_tools_tag(text):
        return bool(re.search(r"<\s*tool\b|<\s*tools\b", text or "", re.IGNORECASE))

    def _format_stats(data):
        context_tokens = data.get("prompt_tokens_last", 0)
        max_context = 90000
        percent = (context_tokens / max_context * 100) if max_context else 0.0
        return (
            f"Context Tokens: {_token_bucket(context_tokens)}/{_token_bucket(max_context)} "
            f"({percent:.1f}%) | Output Tokens: {data.get('tokens_generated_total', 0)}"
        )

    def _build_history(chain, tools_as_user=False):
        history = []
        for m in chain:
            if not isinstance(m, dict):
                continue
            role = m.get("role")
            content = m.get("content")
            if role == "tools":
                role = "user" if tools_as_user else "user"
            elif role == "actor":
                role = "user"
            elif role not in {"user", "assistant", "system"}:
                role = None
            if role and content is not None:
                history.append({"role": role, "content": content})
        return history

    def _ensure_totals(data):
        data.setdefault("tokens_prompted_total", 0)
        data.setdefault("tokens_generated_total", 0)
        data.setdefault("tools_used_total", 0)
        data.setdefault(
            "tools_used",
            {
                "file_read": 0,
                "file_edit": 0,
                "file_create": 0,
                "terminal": 0,
                "search": 0,
                "signature": 0,
            },
        )
        if "director_chain" not in data and "messages" in data:
            data["director_chain"] = data.pop("messages", [])
        data.setdefault("director_chain", [])
        data.setdefault("actor_chain", [])

    def _load_chat(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return {
                    "created_at": _now(),
                    "updated_at": _now(),
                    "model": DEFAULT_MODEL,
                    "director_chain": data,
                    "actor_chain": [],
                }
            if isinstance(data, dict):
                if "director_chain" in data and isinstance(data["director_chain"], list):
                    return data
                if "messages" in data and isinstance(data["messages"], list):
                    data["director_chain"] = data.pop("messages", [])
                    data.setdefault("actor_chain", [])
                    return data
        except Exception:
            return {
                "created_at": _now(),
                "updated_at": _now(),
                "model": DEFAULT_MODEL,
                "director_chain": [],
                "actor_chain": [],
            }
        return {
            "created_at": _now(),
            "updated_at": _now(),
            "model": DEFAULT_MODEL,
            "director_chain": [],
            "actor_chain": [],
        }

    def _get_recent_chats(limit=10):
        entries = []
        try:
            for name in os.listdir(chats_dir):
                if not name.endswith(".json"):
                    continue
                full = os.path.join(chats_dir, name)
                try:
                    mtime = os.path.getmtime(full)
                except OSError:
                    mtime = 0
                entries.append((mtime, full))
        except OSError:
            return []
        entries.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in entries[:limit]]

    def _select_chat_ui(chat_paths):
        options = ["New chat"] + chat_paths

        def _run(stdscr):
            curses.curs_set(0)
            idx = 0
            while True:
                stdscr.erase()
                height, width = stdscr.getmaxyx()
                stdscr.addstr(0, 0, "Select chat (Enter to load)")

                for i, opt in enumerate(options):
                    prefix = "➤ " if i == idx else "  "
                    label = opt if i == 0 else os.path.basename(opt)
                    stdscr.addstr(2 + i, 0, (prefix + label)[: width - 1])

                history_start = 2 + len(options) + 1
                stdscr.addstr(history_start, 0, "History:")
                if idx == 0:
                    history_lines = ["<new chat>"]
                else:
                    data = _load_chat(options[idx])
                    if isinstance(data, dict):
                        msgs = data.get("director_chain", [])
                    else:
                        msgs = data
                    history_lines = [
                        f"{m.get('role')}: {m.get('content')}"
                        for m in msgs
                        if isinstance(m, dict)
                    ]

                max_history = height - history_start - 1
                for j, line in enumerate(history_lines[:max_history]):
                    stdscr.addstr(history_start + 1 + j, 0, line[: width - 1])

                key = stdscr.getch()
                if key in (curses.KEY_UP, ord("k")):
                    idx = (idx - 1) % len(options)
                elif key in (curses.KEY_DOWN, ord("j")):
                    idx = (idx + 1) % len(options)
                elif key in (curses.KEY_ENTER, 10, 13):
                    return options[idx]

        return curses.wrapper(_run)

    recent = _get_recent_chats(10)
    selected = _select_chat_ui(recent)

    if selected == "New chat":
        chat_id = time.strftime("%Y%m%d_%H%M%S")
        chat_path = os.path.join(chats_dir, f"chat_{chat_id}.json")
        chat_data = {
            "created_at": _now(),
            "updated_at": _now(),
            "model": DEFAULT_MODEL,
            "director_chain": [],
            "actor_chain": [],
        }
    else:
        chat_path = selected
        chat_data = _load_chat(chat_path)

    _ensure_totals(chat_data)
    current_model = chat_data.get("model", DEFAULT_MODEL)

    # Colors
    prompt_color = "\033[36m"
    response_color = "\033[92m"
    actor_color = "\033[95m"
    tools_color = "\033[93m"
    dim_color = "\033[90m"
    reset_color = "\033[0m"

    # Indentation for Actor output
    actor_indent = "\t"

    def _print_tool_usage(tool_output, indent="\t"):
        """Print a summary of tools used from the output."""
        reads = re.findall(r'<file path="([^"]+)"', tool_output)
        edits = re.findall(r"<ok>Edited file: ([^<]+)</ok>", tool_output)
        creates = re.findall(r"<ok>Created file: ([^<]+)</ok>", tool_output)
        terminals = re.findall(r"<exit_code>(\d+)</exit_code>", tool_output)

        if reads:
            for f in reads:
                print(f"{indent}{tools_color}[read]{reset_color} {f}")
        if edits:
            for f in edits:
                print(f"{indent}{tools_color}[edit]{reset_color} {f}")
        if creates:
            for f in creates:
                print(f"{indent}{tools_color}[create]{reset_color} {f}")
        if terminals:
            for code in terminals:
                status = "ok" if code == "0" else f"exit {code}"
                print(f"{indent}{tools_color}[terminal]{reset_color} {status}")

    if chat_data["director_chain"]:
        print(f"{dim_color}--- Chat history ---{reset_color}")
        for m in chat_data["director_chain"]:
            role = m.get("role", "unknown")
            content = m.get("content", "")
            if role == "user":
                print(f"{dim_color}You: {content[:100]}...{reset_color}" if len(content) > 100 else f"{dim_color}You: {content}{reset_color}")
            elif role == "assistant":
                print(f"{dim_color}Director: {content[:100]}...{reset_color}" if len(content) > 100 else f"{dim_color}Director: {content}{reset_color}")
            elif role == "actor":
                print(f"{dim_color}  Actor: {content[:100]}...{reset_color}" if len(content) > 100 else f"{dim_color}  Actor: {content}{reset_color}")
        print(f"{dim_color}--- End history ---{reset_color}\n")

    def _switch_chat():
        nonlocal chat_path, chat_data, current_model
        recent = _get_recent_chats(10)
        selected = _select_chat_ui(recent)
        if selected == "New chat":
            chat_id = time.strftime("%Y%m%d_%H%M%S")
            chat_path = os.path.join(chats_dir, f"chat_{chat_id}.json")
            chat_data = {
                "created_at": _now(),
                "updated_at": _now(),
                "model": DEFAULT_MODEL,
                "director_chain": [],
                "actor_chain": [],
            }
        else:
            chat_path = selected
            chat_data = _load_chat(chat_path)

        _ensure_totals(chat_data)
        current_model = chat_data.get("model", DEFAULT_MODEL)
        print("\033c", end="")
        print("Chat history:")
        for m in chat_data["director_chain"]:
            role = m.get("role", "unknown")
            content = m.get("content", "")
            print(f"{role}: {content}")

    def _select_model_ui():
        options = list(MODEL_OPTIONS)

        def _run(stdscr):
            curses.curs_set(0)
            idx = options.index(current_model) if current_model in options else 0
            while True:
                stdscr.erase()
                _, width = stdscr.getmaxyx()
                stdscr.addstr(0, 0, "Select model (Enter to confirm)")
                for i, opt in enumerate(options):
                    prefix = "➤ " if i == idx else "  "
                    stdscr.addstr(2 + i, 0, (prefix + opt)[: width - 1])
                key = stdscr.getch()
                if key in (curses.KEY_UP, ord("k")):
                    idx = (idx - 1) % len(options)
                elif key in (curses.KEY_DOWN, ord("j")):
                    idx = (idx + 1) % len(options)
                elif key in (curses.KEY_ENTER, 10, 13):
                    return options[idx]

        return curses.wrapper(_run)

    def _input_box():
        print(f"{dim_color}─────────────────────────────────────{reset_color}")
        text = input(f"{prompt_color}You: {reset_color}")
        return text

    def _start_spinner(label, chars):
        stop_event = threading.Event()

        def _spin():
            idx = 0
            while not stop_event.is_set():
                ch = chars[idx % len(chars)]
                sys.stdout.write(f"\r{dim_color}{label} {ch}{reset_color}  ")
                sys.stdout.flush()
                idx += 1
                time.sleep(0.08)
            sys.stdout.write("\r" + (" " * 40) + "\r")
            sys.stdout.flush()

        t = threading.Thread(target=_spin, daemon=True)
        t.start()
        return stop_event, t

    while True:
        user_text = _input_box().strip()
        if not user_text:
            break
        if user_text == "/":
            print("/back  /exit  /chats  /models")
            continue
        if user_text == "/exit":
            break
        if user_text in {"/chats", "/back"}:
            _switch_chat()
            continue
        if user_text == "/models":
            current_model = _select_model_ui()
            chat_data["model"] = current_model
            chat_data["updated_at"] = _now()
            try:
                with open(chat_path, "w", encoding="utf-8") as f:
                    json.dump(chat_data, f, ensure_ascii=False, indent=2)
            except OSError:
                pass
            print(f"Model: {current_model}")
            continue
        if user_text.lower() in {"exit", "quit"}:
            break

        user_tokens = _token_estimate(user_text)
        stats_text = _format_stats(chat_data)
        user_content = f"{user_text}\n\n\n---\nStats \n{stats_text}"
        chat_data["director_chain"].append(
            {
                "role": "user",
                "content": user_content,
                "created_at": _now(),
                "token_estimate": user_tokens,
                "token_bucket": _token_bucket(user_tokens),
                "tools_used_total": chat_data["tools_used_total"],
                "tools_used": dict(chat_data["tools_used"]),
            }
        )
        history = _build_history(chat_data["director_chain"])

        chat_data["prompt_tokens_last"] = sum(
            _token_estimate(m.get("content", ""))
            for m in chat_data["director_chain"]
            if isinstance(m, dict)
        ) + (_token_estimate(director_system_prompt) if director_system_prompt else 0)
        chat_data["tokens_prompted_total"] += chat_data["prompt_tokens_last"]
        print(f"{dim_color}{stats_text}{reset_color}")

        max_tool_iterations = 15
        phase = "thinking"
        for _ in range(max_tool_iterations):
            spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            label = "Director thinking..." if phase == "thinking" else "Director tools..."
            stop_event, _ = _start_spinner(label, spinner_chars)
            print(f"{response_color}Director: ", end="", flush=True)
            try:
                assistant_text = Director(
                    history,
                    director_system_prompt,
                    current_model,
                    on_first_token=stop_event.set,
                )
            except Exception as exc:
                stop_event.set()
                print(reset_color, end="", flush=True)
                print(f"\n{dim_color}[error] Director failed: {exc}{reset_color}")
                break
            print(reset_color, end="", flush=True)
            stop_event.set()
            if not assistant_text.strip():
                print(f"\n{dim_color}[error] Director returned empty.{reset_color}")
                break
            assistant_tokens = _token_estimate(assistant_text)
            chat_data["director_chain"].append(
                {
                    "role": "assistant",
                    "content": assistant_text,
                    "created_at": _now(),
                    "model": current_model,
                    "token_estimate": assistant_tokens,
                    "token_bucket": _token_bucket(assistant_tokens),
                    "tools_used_total": chat_data["tools_used_total"],
                    "tools_used": dict(chat_data["tools_used"]),
                }
            )
            chat_data["tokens_generated_total"] += assistant_tokens

            actor_instructions = _extract_actor_instructions(assistant_text)
            for instruction in actor_instructions:
                print(f"\n{actor_indent}{dim_color}[Actor task received]{reset_color}")
                chat_data["actor_chain"].append(
                    {"role": "user", "content": instruction, "created_at": _now()}
                )
                actor_history = _build_history(chat_data["actor_chain"])
                actor_did_work = False

                for _ in range(max_tool_iterations):
                    try:
                        print(f"{actor_indent}{actor_color}Actor: ", end="", flush=True)
                        actor_text = Actor(
                            actor_history,
                            actor_system_prompt,
                            current_model,
                            line_prefix=actor_indent,
                        )
                    except Exception as exc:
                        print(reset_color, end="", flush=True)
                        print(f"\n{actor_indent}{dim_color}[error] Actor failed: {exc}{reset_color}")
                        break
                    print(reset_color, end="", flush=True)
                    if not actor_text.strip():
                        print(f"\n{actor_indent}{dim_color}[error] Actor returned empty.{reset_color}")
                        break
                    chat_data["actor_chain"].append(
                        {
                            "role": "assistant",
                            "content": actor_text,
                            "created_at": _now(),
                            "model": current_model,
                        }
                    )

                    if not _has_tools_tag(actor_text):
                        break
                    actor_tools_output = Tools_handler(actor_text)
                    if not actor_tools_output:
                        break

                    actor_did_work = True
                    # Print tool usage summary
                    _print_tool_usage(actor_tools_output, indent=actor_indent)

                    chat_data["actor_chain"].append(
                        {"role": "tools", "content": actor_tools_output, "created_at": _now()}
                    )
                    delta_actor = _count_tools_from_text(actor_tools_output)
                    for k, v in delta_actor.items():
                        chat_data["tools_used"][k] = chat_data["tools_used"].get(k, 0) + v
                    chat_data["tools_used_total"] = sum(chat_data["tools_used"].values())
                    actor_history = _build_history(chat_data["actor_chain"], tools_as_user=True)

                # After Actor loop ends, ask for summary and give to Director
                if actor_did_work:
                    summary_prompt = "Summarize what you accomplished for the above task in a brief summary."
                    chat_data["actor_chain"].append(
                        {"role": "user", "content": summary_prompt, "created_at": _now()}
                    )
                    actor_history = _build_history(chat_data["actor_chain"], tools_as_user=True)
                    try:
                        print(f"{actor_indent}{actor_color}Actor Summary: ", end="", flush=True)
                        actor_summary = Actor(
                            actor_history,
                            actor_system_prompt,
                            current_model,
                            line_prefix=actor_indent,
                        )
                        print(reset_color, end="", flush=True)
                        if actor_summary.strip():
                            chat_data["actor_chain"].append(
                                {
                                    "role": "assistant",
                                    "content": actor_summary,
                                    "created_at": _now(),
                                    "model": current_model,
                                }
                            )
                            chat_data["director_chain"].append(
                                {"role": "actor", "content": actor_summary, "created_at": _now()}
                            )
                    except Exception as exc:
                        print(reset_color, end="", flush=True)
                        print(f"\n{actor_indent}{dim_color}[error] Actor summary failed: {exc}{reset_color}")

            assistant_tools_text = re.sub(
                r"<\s*actor\s*>.*?<\s*/\s*actor\s*>",
                "",
                assistant_text or "",
                flags=re.IGNORECASE | re.DOTALL,
            )
            if not _has_tools_tag(assistant_tools_text):
                break
            tools_output = Tools_handler(assistant_tools_text)
            if not tools_output:
                break

            # Print Director tool usage summary
            _print_tool_usage(tools_output, indent="")
            delta = _count_tools_from_text(assistant_text)
            for k, v in delta.items():
                chat_data["tools_used"][k] = chat_data["tools_used"].get(k, 0) + v
            chat_data["tools_used_total"] = sum(chat_data["tools_used"].values())
            tools_tokens = _token_estimate(tools_output)
            chat_data["director_chain"].append(
                {
                    "role": "tools",
                    "content": tools_output,
                    "created_at": _now(),
                    "token_estimate": tools_tokens,
                    "token_bucket": _token_bucket(tools_tokens),
                    "tools_used_total": chat_data["tools_used_total"],
                    "tools_used": dict(chat_data["tools_used"]),
                }
            )
            # Tools output is not counted in Output Tokens.

            history = _build_history(chat_data["director_chain"], tools_as_user=True)
            phase = "tools"

        chat_data["updated_at"] = _now()
        chat_data["model"] = current_model

        try:
            with open(chat_path, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass



def pre_check():
    import importlib
    import shutil

    required_modules = [
        "ast",
        "base64",
        "math",
        "os",
        "re",
        "subprocess",
        "textwrap",
        "xml.etree.ElementTree",
        "zlib",
    ]

    optional_commands = ["pdftotext"]

    lines = ["<precheck>"]
    lines.append("  <modules>")
    for name in required_modules:
        try:
            importlib.import_module(name)
            lines.append(f"    <module name=\"{name}\" status=\"ok\" />")
        except Exception as exc:
            lines.append(
                f"    <module name=\"{name}\" status=\"missing\" error=\"{exc}\" />"
            )
    lines.append("  </modules>")

    lines.append("  <commands>")
    for cmd in optional_commands:
        available = shutil.which(cmd) is not None
        status = "ok" if available else "missing"
        lines.append(f"    <command name=\"{cmd}\" status=\"{status}\" />")
    lines.append("  </commands>")
    lines.append("</precheck>")

    return "\n".join(lines)


def test_agent():
    input_text = r"""
<tools>
<file>
  <edit file="/Users/agnos/Downloads/AGNOS/AGEditor_2/V2/Backend/text.py">
        <old>
Line 5 in 5th line
Line 6 in 6th line
Line 7 in 7th line
Line 8 in 8th line
Line 9 in 9th line
Line 10 in 10th line
        </old>
    <new>
Line 5 in 5th line
Line 6 in 6th line
Line 7 in 7th line
Line 8 in 8th line
Line 9 in 9th line
Line 10 in 10th line
    </new>
  </edit>
</file>
</tools>

    """

    input_text = """





<tools>
<terminal>
  <command>cd /Users/agnos/Downloads/AGNOS/Tester/testai/Test1 && source venv/bin/activate && python app.py</command>
  <timeout>120</timeout>
</terminal>
</tools>







    """








    response = Tools_handler(input_text)
    print(response)
    try:
        import os

        debug_dir = "/Users/agnos/Downloads/AGNOS/AGEDITOR_3/V1/Backend/Debug"
        os.makedirs(debug_dir, exist_ok=True)
        debug_path = os.path.join(debug_dir, "response.md")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(response)
    except OSError:
        pass


if __name__ == "__main__":
    test_agent()
    # Agent()
    # print(pre_check())