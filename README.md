# zmk-config

Diagram auto-generated with: https://github.com/caksoylar/keymap-drawer

![my_keymap(4)](https://user-images.githubusercontent.com/28645381/230996226-c7cbf84d-432e-4702-84ad-1d3873b66430.svg)

## Building

`./scripts/build.sh -h`

## Flashing

1. Go on layer having `&bootloader` (usually BLT)
2. USB one half (best to start from Rx) -> press `&bootloader`, it will appear as storage device
3. paste firmware (.uf2) and wait until the storage unmounts itself
4. do the same for the other half, but copy the other side firmware
5. done, no need to manually reboot

## ToDo by Priority
- [ ] rearrange symbols, and maybe move the most used ones on easy combos
- [ ] find low error-prone and fast way to delete words (Ctrl+Bspc)
	- combo? tap-dance? replace backspace?
	- for now I'm using homerow Ctrl+Bspc, but I often get false negatives when fast typing

## References history
- [Ben Vallack](https://youtube.com/c/BenVallack)
	- Introduced me into the **ergo split rabbit hole**
	- First layout I've tried, but I could not grow a liking for his "tap-tap" approach (tapping for layer switching may be more comfortable than holding/chording, but writing characters on alternating layers was just hell)
- [Callum Oakley](https://github.com/callum-oakley/qmk_firmware/tree/master/users/callum)
	- Simple and intuitive, **dedicated modifiers** approach is faster and less error prone that modtap homerow
	- This is where my actual layout has it roots. The first steps from this point onwards  concerned space optimization (thought that dedicated homerow mods on every layer may be unnecessary), and the adaptation of the layout for left-handedness (in part also to be more mouse-friendly)
- [Miryoku](https://github.com/manna-harbour/miryoku)
	- Not really the layout per-se, but terminology and features
- [Seniply](https://stevep99.github.io/seniply)
	- Thumb cluster, except I've switched the inner thumb keys since I don't need dedicated shift in Sym layer. I much prefer being able to press space without leaving the layer instead.
	- Strong inspiration for **Extend layer**, but with navigation cluster on the left side
	- Pretty much copied the function layer.
- [Robert Urob](https://github.com/urob/zmk-config)
	- Awesome **timeless homerow mods approach**, which made me switch fron Callum style mods, and thus free many keys.
	- convinced me to use **combos** (especially for esc, enter, and brackets)
	- **mod-morp** some keys like comma and dot
	- He mentions that ZMK does not yet support **tap-only combos** ([#544](https://github.com/zmkfirmware/zmk/issues/544)), that is, in the official ZMK implementation holding a set of keys in the homerow in order to trigger multiple mods, would instead trigger a combo if is assigned to that exact set of keys. His workaround is to press the needed mods sequentially so that the combo does not trigger.
		- My **fix** is to add the corresponding mods to the hold-behavior of the combo. This  has the same effect as the desired tap-only combo behavior.
- [Rafael Romao](https://github.com/rafaelromao/keyboards)
