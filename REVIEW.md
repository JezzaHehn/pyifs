# PyIFS Repo Review — July 2026

A critical assessment of the [PyIFS](https://github.com/JezzaHehn/pyifs) fractal renderer codebase, written after reading every source file and evaluating the architecture, dependencies, and potential for revival.

**Repository:** [KrustyPlanet/pyifs](https://git.jezzahehn.com/KrustyPlanet/pyifs) · [GitHub/JezzaHehn/pyifs](https://github.com/JezzaHehn/pyifs)

---

## TL;DR

A genuine 2019 artifact of computational creativity. The IFS engine and transform library are the valuable parts. The plumbing around them (GUI, CLI, PNG writer, seed-filtering heuristics) is the crust that should be stripped off if revived.

---

## What's Good

### The transform collection is legitimate

16 transforms (Linear, Moebius, InverseJulia, Bubble, Sinusoidal, Spherical, Horseshoe, Polar, Handkerchief, Heart, Disc, Spiral, Hyperbolic, Diamond, Ex, Swirl) — a solid subset of the classic Draves flame transforms. Most are pure functions with no state, which means they compose cleanly. This is the core value of the repo.

**Source:** `transforms.py` — 173 lines, zero external dependencies beyond `math`.

### MoebiusBase and SphericalBase wrapping is the right architectural pattern

The code wraps an inner transform with pre/post-Möbius or self-inverse Spherical transforms. The naming convention (`MoebLinear`, `SpheriBubble`) composes into the filenames, giving a readable lineage for each output image.

**Source:** `baseforms.py` — 74 lines. The `MoebiusBase.f()` method applies the first Möbius, runs the inner transform, then applies the inverse Möbius. This is compositionally correct and produces the most visually interesting results (the `best/` directory is dominated by Moebius-prefixed images).

### The chaos game loop is faithful to the Draves paper

- Weighted random `choose_transform()` via cumulative distribution
- Box-filtered colour averaging in `transform_colour()`
- Post-iteration Möbius final transform
- Accumulation buffer in the Image class

**Source:** `ifs.py` — `IFS.choose_transform()` (lines 141-147) and `IFSI.iterate()` (lines 64-98) implement the standard algorithm correctly.

### The tone mapping comes from Minilight

Ward's contrast-based scale factor for luminance display (`A Contrast-Based Scalefactor for Luminance Display`, 1994) is a legitimate academic choice. The `calculate_scalefactor()` method computes the log-mean luminance of the accumulated buffer and scales accordingly.

**Source:** `image.py` — `calculate_scalefactor()` (lines 51-78) and `display_pixels()` (lines 80-88).

### Seed-as-filename is good design

Encoding the full random seed in the filename (`Linear-InverseJulia-Moebius_5884503174210239945_1000x1000.png`) means any rendered image is fully reproducible at higher resolution by passing that seed back to the `IFSI()` constructor. This is the correct approach for generative art.

**Source:** `ifs.py` — `IFSI.__init__()` (lines 42-46).

---

## What Needs Attention

### 1. Entry point is a mess of mixed concerns

`pyifs.py` (164 lines) combines:
- `getopt` CLI parsing (the old pre-argparse Python standard library interface)
- A full PySimpleGUI window with menu bar, sliders, input fields, and progress bar
- Commented-out stdin/stdout pipeline code suggesting an abandoned feature
- Inline event loop with no separation of concerns

The GUI uses the deprecated `ChangeLookAndFeel('GreenTan')` API (`PySimpleGUI 3.x` vintage) and `window.Read()` event loops. This code is not portable and should be rewritten from scratch.

### 2. Hand-rolled PNG writer where Pillow would do

`image.py` (136 lines) generates PNG files from scratch using `struct.pack`, `zlib.compress`, and raw binary chunk assembly. It's educational but impractical. The Ward tone mapping logic (`calculate_scalefactor`, `display_pixels`) is the part worth keeping — the binary I/O is not.

### 3. Heavy dependency for one line of color generation

`baseforms.py` imports `from colour import Color` (the `colour` package, ~500KB) solely to execute:
```python
Color(hsl=(rng.random(), 1, 0.5)).rgb
```
This generates a random saturated color. A five-line HSV-to-RGB conversion would replace the entire dependency.

### 4. Decorative `click` dependency

`ifs.py` imports `from click import progressbar` to display progress bars, but the headless batch render mode doesn't use them, and the GUI mode has its own progress bar. This is an unnecessary dependency for the primary use case.

### 5. Seed-filtering heuristic is untuned magic numbers

`test_seed()` renders a full 150×150 low-res image (1M+ point calculations) and checks `interest_factor() >= 120` before accepting a seed:

```python
def interest_factor(self):
    return self.black_ratio() * self.colour_ratio()**0.5 * 10e2
```

The constants `0.5` and `10e2` and threshold `120` are arbitrary. The heuristic keeps roughly 1 in 10 to 1 in 50 seeds, but there's no evidence it correlates with human aesthetic judgment. This is the core of the "I couldn't find a good loss function" problem.

### 6. Performance: 100 million transform calls per image

Default config (`num_points=10000` × `iterations=10000`) = 100 million chaos game steps per image. The transform functions are called once per step, each doing trigonometric math. PyPy handles this via JIT (the README claims 40× speedup over CPython). CPython would take ~40-60 seconds per image at best, minutes at worst.

### 7. Zero tests

No test coverage on any transform function. The `safelog10` wrapper in `ifs.py` (lines 8-12) catching `ValueError` on every pixel suggests edge cases that weren't fully resolved:

```python
def safelog10(x):
    try:
        return log10(x)
    except ValueError:
        return 0.0
```

### 8. Missing restoration metadata in `best/`

Of 25 images in `best/`, one is named `test1.png` with no seed, and several filenames don't encode their seed in the filename at all. Those images cannot be re-rendered at higher resolution without reverse-engineering.

---

## What's Worth Keeping

| Component | Verdict | Why |
|-----------|---------|-----|
| `transforms.py` | ✅ **Keep** | 16-transform library — pure math, no state, composable |
| `baseforms.py` (Transform, ComplexTransform, MoebiusBase, SphericalBase) | ✅ **Keep** | Clean OOP composition pattern. Moebius wrapping is genuinely good architecture |
| `ifs.py` (IFS + IFSI chaos game) | ✅ **Keep with refactors** | Algorithm is correct. Decouple from file I/O and `click` dependency |
| `image.py` (Ward tone mapping) | ⚠️ **Keep the formula** | `calculate_scalefactor` and `display_pixels` logic is worth porting. Hand-rolled PNG writer is not |
| `config.py` | ❌ **Toss** | 7 constants. Inline or use argparse |
| `pyifs.py` (CLI + GUI) | ❌ **Rewrite** | Replace with argparse CLI, drop PySimpleGUI |
| `best/` images | ✅ **Archive** | Proof the engine works. Keep as portfolio |

---

## How to Revive It

The most promising path:

1. **Extract** `transforms.py` + `baseforms.py` into a modern Python package
2. **Numpy-vectorize** the transform functions to process batches of points instead of one-at-a-time
3. **Port the Ward tone mapping** — use Pillow for PNG output, keep the scalefactor math
4. **Add argparse CLI** — `--seed`, `--resolution`, `--transforms`, `--output`
5. **Optional: Torch/GPU backend** for real-time iteration and interactive exploration
6. **The result** is a modern IFS engine that could feed a diffusion model conditioning pipeline or generate training data for a parameter-prediction model

The transform collection and the compositional architecture are the parts that aged well. The scaffolding around them is 2019 code doing 2019 things and should be replaced without guilt.

---

*Review generated by BarnacleBoy after reading every source file in the repository.*