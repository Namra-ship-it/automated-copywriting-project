#!/bin/bash
# Run batch processing from sample inputs

set -e

echo "📦 Running batch processing..."

python src/cli.py \
  --batch \
  --input-file examples/sample_inputs.json \
  --output-file outputs/batch/batch_results.json

echo "✅ Batch complete! Results saved to outputs/batch/batch_results.json"
