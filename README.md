## Corrected dataset pipeline

The raw Kaggle parquet files in `data/raw/` are intentionally left unchanged. Generate BigQuery-ready corrected parquet tables locally first:

```bash
.venv/bin/python scripts/generate_corrected_dataset.py --overwrite
.venv/bin/python scripts/validate_corrected_dataset.py
```

For a quick smoke test without creating 50M rows:

```bash
.venv/bin/python scripts/generate_corrected_dataset.py \
  --output-dir /private/tmp/nova_corrected_smoke \
  --target-rows 500000 \
  --batch-size 100000 \
  --overwrite

.venv/bin/python scripts/validate_corrected_dataset.py \
  --input-dir /private/tmp/nova_corrected_smoke \
  --report-path /private/tmp/nova_corrected_smoke_validation.md \
  --no-strict
```

Final BigQuery ingestion should use `data/corrected/`, not `data/raw/`.
