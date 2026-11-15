# QR code API

A small Flask API that creates a PNG QR code from text. The endpoint supports optional colors, size, error correction, and shape settings.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open [the interactive API documentation](http://127.0.0.1:5000/apidocs/) or request a QR code directly:

```text
http://127.0.0.1:5000/qrcode?text=Hello%20world
```

## `GET /qrcode`

`text` is required. Every other query parameter is optional.

| Parameter | Default | Allowed values |
| --- | --- | --- |
| `text` | — | Text to encode |
| `fill_color` | `000000` | Six-digit hexadecimal color, with or without `#` |
| `back_color` | `FFFFFF` | Six-digit hexadecimal color, with or without `#` |
| `box_size` | `10` | Integer from 1 to 20 (pixels per QR square) |
| `border` | `4` | Integer from 4 to 20 (width in QR squares) |
| `error_correction` | `M` | `L`, `M`, `Q`, or `H` |
| `style` | `square` | `square`, `rounded`, or `circle` |

Example with optional settings:

```text
http://127.0.0.1:5000/qrcode?text=Hello%20world&fill_color=1e3a8a&back_color=ffffff&box_size=12&error_correction=H&style=rounded
```

The response is a PNG image. Invalid or missing parameters return a JSON error with HTTP status 400. When using a `#` in a color value, encode it as `%23` in the URL.
