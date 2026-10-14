#!/usr/bin/env bash
# Запуск для Linux / macOS / GitHub Codespaces
python -m pip install -r requirements.txt
python seed_data.py
python app.py
