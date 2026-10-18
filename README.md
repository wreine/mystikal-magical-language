# Mistika ✦ Encantados Studio

A spell-casting programming language and a single-window desktop IDE for it. Mistika source is scanned into runes, woven into Python, and cast (executed) in a separate process. Runtime errors are reported against your Mistika line numbers, not the generated Python's, and are explained in Filipino.

The magic words are Encantadia-inspired: write `abisala` instead of `if`, `adnes` instead of `match`, `hayag` instead of `print`.

## Requirements

- Python 3.10+ (the switch spells use `match`/`case`, which need 3.10)
- tkinter (bundled with most Python installs; on Debian/Ubuntu: `sudo apt install python3-tk`)
- No third-party packages

## Run

```bash
python main.py
```

## Usage

| Action | How |
|---|---|
| Run the spell | **✦ Run Spell** button or **Ctrl+Enter** |
| Indent / dedent | **Tab** inserts 4 spaces, **Shift+Tab** removes up to 4 |
| Auto-indent | Pressing Enter keeps the indent, and adds 4 after a line ending in `:` |
| Load the demo program | **📜 Load Sample** button |
| Reset editor and output | **🗑 Clear** button |
| Insert a keyword | Double-click it in the Spellbook sidebar (selecting a row shows its meaning) |

The right panel has two tabs: **Result** (program output, or an error message) and **Python Form** (the generated Python). The status bar shows ready / casting / nagtagumpay / pumalya.

## Keywords (31 spells)

### Daloy ng Mahika
| Mistika | Python | Meaning |
|---|---|---|
| abisala | if | Abisala! Kung totoo ang kondisyon |
| eshma | elif | Isa pang kondisyon |
| ashti | else | Kung walang tumama |
| lireo | while | Umikot habang may bisa ang sumpa |
| sapiro | for | Isa-isang daanan ang koleksyon |
| hathoria | in | Nasa loob ng |
| lagot | break | Sirain ang ikot |
| tuloy | continue | Lumaktaw sa susunod na ikot |
| tahimik | pass | Walang gagawin |

### Pagpili (switch)
| Mistika | Python | Meaning |
|---|---|---|
| adnes | match | Alamin kung ano ang halaga (switch) |
| ecsha | case | Marahil ito ang halaga (case) |
| alsha | case _ | Lahat ng iba pang halaga (default) |

### Katotohanan
| Mistika | Python | Meaning |
|---|---|---|
| ivo | True | Pag-ibig, tama, totoo |
| hagorn | False | Kasamaan, mali, hindi totoo |
| adamya | None | Ang kawalan |
| emre | and | Dapat parehong tama |
| alena | or | Isa lang ay sapat na |
| pirena | not | Baligtarin ang bisa |

### Pagsubok
| Mistika | Python | Meaning |
|---|---|---|
| hamon | try | Subukan ang mapanganib na gawain |
| bigo | except | Kapag nabigo ang hamon |
| wakas | finally | Laging mangyayari sa dulo |
| sumpain | raise | Magpakawala ng sumpa (error) |

### Pagtawag
| Mistika | Python | Meaning |
|---|---|---|
| hayag | print | Ihayag ang mensahe |

### Anyo ng Datos
| Mistika | Python | Meaning |
|---|---|---|
| buo | int | Buong bilang |
| hati | float | May decimal |
| titik | str | Teksto |
| tadhana | bool | Totoo o hindi |
| hanay | list | Maayos na koleksyon |
| tali | tuple | Koleksyon na hindi mababago |
| natatangi | set | Koleksyon na walang pareho |
| aklat | dict | Susi at halaga |

Everything else that is allowed is plain Python syntax (`range`, `len`, operators, and so on).

## Rules of the language

- **No methods.** Users cannot define functions or classes, and method calls with a dot (such as `"abc".upper()`) are rejected.
- **No advanced keywords.** `def`, `class`, `lambda`, `return`, `yield`, `import`, `from`, `global`, `nonlocal`, `async`, `await`, `with`, `del` and `assert` are rejected with a `[Bawal na Spell]` message.
- **Scope:** data types, if-else, switch, loops, and error handling.

The "no methods" rule applies to the Mistika language only. The Python code that implements Mistika uses classes and methods normally.

## Example

```
puntos = 75
abisala puntos >= 90:
    hayag("Mataas")
eshma puntos >= 70:
    hayag("Katamtaman")
ashti:
    hayag("Mababa")

edad = 2
adnes edad:
    ecsha 1:
        hayag("isa")
    ecsha 2:
        hayag("dalawa")
    alsha:
        hayag("ibang bilang")
```

## Error handling

- Users can catch errors with `hamon` / `bigo` / `wakas` and raise them with `sumpain`.
- Runtime errors are explained in Filipino, with the original Python message under `Detalye`.
- An empty editor (or one with only spaces and comments) shows `Walang Spell`.
- Forbidden words show `[Bawal na Spell]`.
- A spell that runs longer than 10 seconds is stopped with a `Napagal ang Spell` message.
- Scanner errors (unclosed text, unknown symbol) are still shown in English.
- Errors never crash the studio.

## How it works

```
source text ──▶ ScannerStage ──▶ runes ──▶ WeaverStage ──▶ Python + line map ──▶ CasterStage ──▶ output
```

1. **Scanner** reads the text character by character and produces runes. A bad character, an unclosed string, or a forbidden word stops here, with the line and column.
2. **Weaver** swaps each spell for its Python equivalent and records which Mistika line every Python line came from.
3. **Caster** runs the Python in a subprocess with a time limit, rewrites the traceback line numbers using the line map, and explains the error in Filipino.

### Object-oriented design (`pipeline.py`)

| Pillar | Where it is used |
|---|---|
| Encapsulation | `Spell` keeps its data private (`_source`, `_runes`, ...) and exposes it only through getters and setters. `CasterStage.set_time_limit()` checks the value before saving it. |
| Abstraction | `Stage` only promises a `run()` method. Each stage decides how. |
| Inheritance | `ScannerStage`, `WeaverStage` and `CasterStage` are all `Stage`s. |
| Polymorphism | `SpellPipeline` calls `stage.run(spell)` on each stage without checking which one it is. |

## Known limitations

- Spells are reserved words outside strings and comments. A variable named `ivo` or `hati` is treated as the spell.
- The method check reads text inside strings as plain text, so a dot inside an f-string such as `f"{x.upper()}"` is not checked.
- Spells are defined in `spellbook.py`. There is no file save/open or multi-file support.
- The IDE runs your code with your Python interpreter and user permissions. Only run code you trust.

## Project layout

| File | Role |
|---|---|
| `spellbook.py` | `GRIMOIRE` (grouped spells) and `SPELLBOOK` (flat lookup) |
| `scanner.py` | `scan()` returns runes, or a problem with line and column (also rejects forbidden words) |
| `weaver.py` | `weave()` returns Python source and a line map |
| `caster.py` | `cast()` runs a subprocess with timeout, traceback remapping and Filipino error messages |
| `pipeline.py` | OOP layer: `Spell`, `Stage` and its subclasses, `SpellPipeline` |
| `studio.py` | tkinter IDE (`MystikaStudio`) |
| `main.py` | entry point |