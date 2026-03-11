# DivineDocs

> All-in-one PDF toolkit — convert, protect, merge and split documents with ease.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

## Features

| Conversion | Direction |
|-----------|-----------|
| Word → PDF | ✅ |
| JPG / WebP → PDF | ✅ |
| HTML → PDF | ✅ |
| Text → PDF | ✅ |
| PDF → Excel | ✅ |
| PDF → Word | ✅ |
| Protect PDF | ✅ (password encryption) |

## Getting Started

```bash
git clone https://github.com/prasangapokharel/divine-docs.git
cd divine-docs
pip install -r requirement.txt
python app.py
```

Open `http://localhost:5000`

## Project Structure

```
divine-docs/
├── app.py              # Main Flask app
├── htmltopdf.py        # HTML → PDF converter
├── jpgtopdf.py         # JPG/WebP → PDF converter
├── texttopdf.py        # Text → PDF converter
├── webptopdf.py        # WebP → PDF converter
├── withdraw.py         # PDF protection utility
├── static/             # CSS, JS, assets
├── templates/          # Jinja2 HTML templates
└── uploads/            # Temp upload folder
```

## License

MIT License — © 2025 Prasanga Pokharel
