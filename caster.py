import os
import shutil
import subprocess
import sys
import tempfile

TIME_LIMIT = 10   # seconds before the spell is stopped

# Python error name -> message in Filipino
ERRORS = {
    "SyntaxError": "Maling pagkakasulat ng spell. Suriin ang baybay at ang mga bantas, tulad ng : at mga panaklong.",
    "IndentationError": "Mali ang pagkakapasok ng linya. Gumamit ng 4 na space.",
    "TabError": "Mali ang pagkakapasok ng linya. Huwag paghaluin ang tab at space.",
    "NameError": "Hindi kilala ang pangalang ito. Tiyaking nabuo mo na ito bago gamitin.",
    "ZeroDivisionError": "Hindi maaaring hatiin sa zero.",
    "TypeError": "Hindi magkatugma ang uri ng datos na ginamit.",
    "ValueError": "Maling halaga ang ibinigay sa spell.",
    "IndexError": "Wala sa hanay ang posisyong hinahanap.",
    "KeyError": "Walang ganitong susi sa aklat.",
}
FALLBACK = "May hindi inaasahang sumpa na pumigil sa spell."


class CastReport:
    """What happened when the spell was run."""

    def __init__(self, stdout, stderr, problem, timed_out, exit_code):
        self.stdout = stdout
        self.stderr = stderr
        self.problem = problem
        self.timed_out = timed_out
        self.exit_code = exit_code


def read_digits(text, pos):
    """Read the digits that start at position pos."""
    digits = ""
    while pos < len(text) and text[pos].isdigit():
        digits = digits + text[pos]
        pos += 1
    return digits


def fix_line_numbers(stderr, line_map, script_path):
    """Change Python line numbers in the error into the user's Mystika line numbers."""
    marker = 'File "' + script_path + '", line '
    fixed = []
    for line in stderr.splitlines():
        if marker in line:
            start = line.index(marker)
            pos = start + len(marker)
            digits = read_digits(line, pos)
            if digits != "":
                number = int(digits)
                mystika_line = line_map.get(number, number)
                line = (line[:start] + 'File "<mystika>", line ' + str(mystika_line)
                        + line[pos + len(digits):])
        fixed.append(line)
    return "\n".join(fixed)


def magical_message(stderr):
    """Turn a Python error into a short message in Filipino."""
    lines = []
    for line in stderr.strip().splitlines():
        if line.strip() != "":
            lines.append(line)
    last = ""
    if len(lines) > 0:
        last = lines[-1]
    kind = last.split(":", 1)[0].strip()

    marker = 'File "<mystika>", line '
    line_number = ""
    for line in lines:
        if marker in line:
            digits = read_digits(line, line.index(marker) + len(marker))
            if digits != "":
                line_number = digits

    place = ""
    if line_number != "":
        place = "Linya " + line_number + ": "
    return place + ERRORS.get(kind, FALLBACK) + "\nDetalye: " + last


def cast(python_code, line_map, time_limit=TIME_LIMIT):
    """Run the Python code in a separate process. Never crashes; reports everything."""
    if python_code.strip() == "":
        return CastReport("", "", None, False, 0)

    workdir = tempfile.mkdtemp(prefix="mystika_")
    try:
        script = os.path.join(workdir, "spell.py")
        file = open(script, "w", encoding="utf-8")
        file.write(python_code)
        file.close()

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        flags = 0
        if os.name == "nt":
            flags = subprocess.CREATE_NO_WINDOW   # no black console window on Windows

        try:
            done = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=time_limit,
                stdin=subprocess.DEVNULL,
                env=env,
                cwd=workdir,
                creationflags=flags,
            )
        except subprocess.TimeoutExpired:
            message = ("Lumampas sa " + str(time_limit) + " segundo ang spell kaya ito itinigil. "
                       "Baka may ikot na walang katapusan (halimbawa: lireo ivo:) "
                       "o napakatagal na gawain.")
            return CastReport("", "", message, True, -1)

        stderr = fix_line_numbers(done.stderr or "", line_map, script)
        stderr = stderr.replace(script, "<mystika>")

        problem = None
        if done.returncode != 0 and stderr.strip() != "":
            problem = magical_message(stderr)
        return CastReport((done.stdout or "").rstrip("\n"), stderr, problem, False, done.returncode)

    except Exception as error:
        return CastReport("", "", "[Caster] Unexpected failure: " + str(error), False, -1)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)