#!/bin/bash
echo "Seeding local database..."
uv run python infrastructure/scripts/seed.py
echo "Done."
