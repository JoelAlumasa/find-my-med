#!/bin/bash
# Quick start script for FindMyMed

cd "$(dirname "$0")"
source venv/bin/activate
streamlit run app.py

