# Embedding Setup Guide

Fish-trail v0.7.0 adds optional ONNX-based sentence embedding for improved semantic drift detection.

## Quick Start

```bash
pip install onnxruntime>=1.23 tokenizers>=0.13 huggingface_hub numpy
```

That's it. The model downloads automatically on first use (~118MB).

## How It Works

- **Tier 1 (always active):** Bilingual keyword Jaccard overlap — fast (<1ms), zero dependencies
- **Tier 2 (optional):** ONNX embedding cosine similarity — only fires in the "ambiguous zone" where keyword overlap is inconclusive (0.0 < relevance < 0.10)

Most messages never reach Tier 2. Expected Tier 2 hit rate: <15% of all `topic_detect` calls.

## Platform Support

| Platform | Status | Model Variant |
|----------|--------|---------------|
| Linux x86_64 | ✅ | `model_quint8_avx2.onnx` |
| Linux aarch64 | ✅ | `model_qint8_arm64.onnx` |
| macOS ARM64 (Apple Silicon) | ✅ | `model_qint8_arm64.onnx` |
| macOS x86_64 (Intel) | ❌ Fallback to keyword-only | — |
| Windows x64 | ✅ | `model_quint8_avx2.onnx` |
| Windows ARM64 | ✅ | `model_qint8_arm64.onnx` |

**Python requirement:** >=3.11

## Configuration

Create or edit `.petfish/fish-trail/config.json`:

```json
{
  "embedding": {
    "enabled": true,
    "preload": false,
    "timeout_ms": 2000
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `true` | Set `false` to disable embedding entirely |
| `preload` | `false` | Reserved for future use (load model at server start) |
| `timeout_ms` | `2000` | Max time for a single inference call |

If `config.json` is missing, defaults apply (embedding enabled, 2s timeout).

## Offline / Air-Gapped Setup

Three options:

### Option 1: Environment variable
```bash
export FISH_TRAIL_MODEL_PATH=/path/to/model_quint8_avx2.onnx
```

### Option 2: Local model directory
Place files in `.petfish/fish-trail/models/`:
```
.petfish/fish-trail/models/
├── model_quint8_avx2.onnx   (or model_qint8_arm64.onnx)
└── tokenizer.json
```

### Option 3: Pre-populate HuggingFace cache
```bash
# On a machine with internet:
huggingface-cli download sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
  onnx/model_quint8_avx2.onnx tokenizer.json

# Copy ~/.cache/huggingface/ to the air-gapped machine, then:
export HF_HUB_OFFLINE=1
```

## Performance

| Operation | Time | When |
|-----------|------|------|
| Model load (cold start) | 1-3s | First ambiguous-zone hit per server lifetime |
| Inference (warm) | 20-50ms | Each subsequent Tier 2 call |
| Memory | ~250-350MB peak | While model is loaded |

## Troubleshooting

**"EmbeddingManager not available"**
- Check: `python -c "import onnxruntime, tokenizers, numpy; print('ok')"`
- Check Python version: >=3.11 required
- Check platform: macOS Intel is not supported

**Model download fails**
- Check network access to `huggingface.co`
- Use offline setup (see above)
- Set `HF_HUB_DISABLE_SYMLINKS_WARNING=1` on Windows if you see symlink warnings

**Timeout errors**
- Increase `timeout_ms` in config.json
- First call is always slower (cold start) — subsequent calls are fast

**Disable embedding entirely**
```json
{"embedding": {"enabled": false}}
```
