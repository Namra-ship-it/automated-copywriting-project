#!/bin/bash
# Run a real-time copy generation request

set -e

echo "🚀 Running real-time copy generation..."

python src/cli.py \
  --product "EcoCharge Pro" \
  --description "A portable solar power bank with 20000mAh capacity, waterproof, and built-in LED flashlight" \
  --platform "Instagram" \
  --tone "Eco-conscious" \
  --audience "Outdoor enthusiasts and eco-friendly travelers" \
  --cta "Shop now and go green" \
  --char-limit 2200 \
  --temperature 0.8 \
  --top-p 0.9

echo "✅ Done!"
