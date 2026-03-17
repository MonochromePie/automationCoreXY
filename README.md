# CoreXY Cursor Game Controller

This project now has two sides:

- Pico firmware (`main.py`) that receives USB serial commands and drives CoreXY via `stepper.py`
- Laptop app (`cursor_game_controller.py`) that opens a game window and tracks cursor movement

## Coordinate system

- Game window origin for control is **bottom-left**: `(0,0)` at bottom-left
- Window size defaults to `800x600`
- Cursor movement is converted to mm using `--mm-per-pixel`

## Pico side

Flash these files to your Pico:

- `stepper.py`
- `main.py`

`main.py` listens for commands over USB serial:

- `ENABLE,1` / `ENABLE,0`
- `HOME`
- `MOVE,dx_mm,dy_mm,speed_mm_s`
- `STOP`

## Laptop side

Install dependencies in your laptop Python environment:

```bash
pip install pygame pyserial
```

Run:

```bash
python cursor_game_controller.py --port /dev/ttyACM0 --width 800 --height 600 --mm-per-pixel 0.1 --speed 50
```

## Controls

- `E` toggle motor enable
- `H` home axes
- `C` clear cursor trail
- `ESC` quit
