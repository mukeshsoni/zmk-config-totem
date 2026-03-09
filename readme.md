# ZMK Miryoku-inspired firmware for the TOTEM keyboard

<figure>
<img src="./keymap.svg" alt="Miryoku inspired keymap for TOTEM keyboard, showing all six layers" width="100%" />
<figcaption>Keyboard layout for all layers and combos</figcaption>
</figure>

This is a ZMK firmware for a [TOTEM keyboard](https://github.com/GEIGEIGEIST/TOTEM), using a keymap that is pretty much copied from both the great [Miryoku layout](https://github.com/manna-harbour/miryoku_zmk), and [urob's ZMK config](https://github.com/urob/zmk-config). I use the alternate hand layout of most of the layers (so that the layer key and modifiers are on one hand, and the main keys of that layout on the other), but combine that with urob's idea of having symbols as combos. I have also adopted his "Timer-less home row mods", which work really well and avoid the usual drawbacks of home row mods.

Caps word is activated by tapping both home row index finger keys, and as I find it easier to have a dedicated shift key for capitalising words, I have a one-shot shift key on the inner left thumb key, and use that for capitalisation and the home row shift for keyboard shortcut combos.

Having all the mods in the home row makes it pretty easy to mash a bunch of them to get Hyper (Shift + Command + Option + Control) or Meh (Shift + Option + Control), but --- just because I can --- I have the index and middle finger keys on the bottom row as Hyper and Meh mod taps too. That makes it very easy to create useful keyboard shortcuts for global OS use without any fear of clashes.

Finally, the extra outer pinky key is used for previous/next tab, back/forward in navigation history, and parens in the number layer. I tend not to hit those keys accidentally as they are way out there, but it is useful to have dedicated and spatially organised keys for common navigation stuff.

## Generated ASCII layout reference

The printable ASCII reference in `totem-layout-reference.txt` is auto-generated from:

- `config/totem.keymap`
- `config/combos.dtsi`

Generation script:

- `scripts/generate_totem_layout_reference.py`

If you use pre-commit, install and enable hooks once:

```bash
pip install pre-commit
pre-commit install
```

Then the reference file is automatically regenerated before each commit whenever either config file changes.
