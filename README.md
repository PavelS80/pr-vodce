# Pražský průvodce — materiály pro guiding

Sada materiálů pro vyprávění o Praze při procházkách (klienti, přátelé, děti) —
česky i anglicky, s důsledným oddělením faktů, legend a průvodcovských historek.

## Výstupy

| Soubor | Popis |
|---|---|
| `Povidani-o-Praze.pdf` / `index.html` | Bilingvní kniha CZ+EN: souvislé mluvené povídání o celé Praze — 16 vyprávěcích kapitol napříč časem + mistrovské skripty (5/10/30 min) + on-location (Karlův most, Staroměstské náměstí) + tahák + fact-check. |
| `Prague-Storybook.pdf` / `storybook.html` | Anglická sbírka **138 průvodcovských historek** v 8 kategoriích (funny history, legends, ghosts, dark history, kings, writers, curiosities, rituals). Každá se štítkem pravdivosti a řádky Where/Tip. |
| `Prazske-skripty.pdf` / `skripty.html` | Terénní verze — jen souvislé mistrovské výklady (CZ+EN) k přednesu. |
| `povidani.md` | Textová verze povídání. |

Každá historka / tvrzení je označené: **doloženo / legenda / tradiční historka / nejisté**
(`documented / legend / traditional tale / uncertain`).

## Struktura

- `data/*.json` — zdroj bilingvní knihy (16 kapitol `seg-*`, skripty `master-*` / `spot-*`, `signatures`, `intro`, `_audit-all`).
- `stories/cat-*.json` — zdroj storybooku (8 kategorií, 138 historek).
- `build_povidani.py` — renderuje `index.html` + `skripty.html` + `povidani.md`.
- `build_storybook.py` — renderuje `storybook.html`.

## Přegenerování

```bash
python3 build_povidani.py      # -> index.html, skripty.html, povidani.md
python3 build_storybook.py     # -> storybook.html
```

PDF se generuje z HTML přes Chrome (headless):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="Povidani-o-Praze.pdf" "file://$PWD/index.html"
```

Obsah je oddělený od vzhledu — stačí upravit JSON a spustit build skript.
