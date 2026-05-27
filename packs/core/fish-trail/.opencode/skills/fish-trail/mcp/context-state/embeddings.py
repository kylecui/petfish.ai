"""
Optional ONNX-based sentence embedding for semantic drift detection (Tier 2).

Requires: onnxruntime>=1.23, tokenizers>=0.13, huggingface_hub, numpy>=1.21
All dependencies are optional — graceful fallback when unavailable.
"""

import logging
import os
import platform
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from numpy import ndarray

logger = logging.getLogger(__name__)

# Lazy-checked dependency flags
_DEPS_AVAILABLE = None
_DEPS_LOCK = threading.Lock()

_REPO_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def _check_deps() -> bool:
    """Check if all optional dependencies are importable."""
    global _DEPS_AVAILABLE
    if _DEPS_AVAILABLE is not None:
        return _DEPS_AVAILABLE
    with _DEPS_LOCK:
        if _DEPS_AVAILABLE is not None:
            return _DEPS_AVAILABLE
        try:
            import numpy  # noqa: F401
            import onnxruntime  # noqa: F401
            import tokenizers  # noqa: F401

            _DEPS_AVAILABLE = True
        except (ImportError, OSError):
            _DEPS_AVAILABLE = False
    return _DEPS_AVAILABLE


def _is_platform_supported() -> bool:
    """Check if onnxruntime supports the current platform."""
    machine = platform.machine().lower()
    system = platform.system().lower()

    # macOS Intel dropped in ORT 1.24
    if system == "darwin" and machine in ("x86_64", "i386"):
        return False

    # Python < 3.11 not supported by ORT 1.25+
    if sys.version_info < (3, 11):
        return False

    return True


class EmbeddingManager:
    """Manages ONNX sentence embedding model for semantic similarity.

    Thread-safe singleton session. Lazy model download on first use.
    Returns None for all operations when deps unavailable or platform unsupported.
    """

    def __init__(self, base_dir: str, timeout_ms: int = 2000):
        self._base_dir = base_dir
        self._timeout_ms = timeout_ms
        self._session = None
        self._tokenizer = None
        self._lock = threading.Lock()
        self._loaded = False
        self._executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="embedding"
        )

    @property
    def available(self) -> bool:
        """True if deps are importable and platform is supported.
        Does NOT require model to be present (lazy download on first use).
        """
        return _check_deps() and _is_platform_supported()

    def similarity(self, text_a: str, text_b: str) -> float | None:
        """Compute cosine similarity between two texts.

        Returns float in [-1, 1] or None if unavailable/timeout/error.
        Model loading (including download) happens outside the timeout window.
        Only inference is subject to timeout.
        """
        if not self.available:
            return None

        # Ensure model is loaded (no timeout — download/load may take seconds)
        session, tokenizer = self._get_session()
        if session is None:
            return None

        try:
            future = self._executor.submit(self._similarity_sync, text_a, text_b)
            return future.result(timeout=self._timeout_ms / 1000.0)
        except FuturesTimeoutError:
            logger.warning("Embedding similarity timed out (%dms)", self._timeout_ms)
            return None
        except Exception as e:
            logger.warning("Embedding similarity failed: %s", e)
            return None

    def _similarity_sync(self, text_a: str, text_b: str) -> float | None:
        """Synchronous similarity computation."""
        emb_a = self._encode(text_a)
        emb_b = self._encode(text_b)
        if emb_a is None or emb_b is None:
            return None

        import numpy as np

        return float(np.dot(emb_a, emb_b))

    def _get_session(self) -> tuple:
        """Get or create the cached (session, tokenizer) tuple. Thread-safe."""
        if self._loaded:
            return (self._session, self._tokenizer)

        with self._lock:
            if self._loaded:
                return (self._session, self._tokenizer)
            try:
                self._session, self._tokenizer = self._load_model()
            except Exception as e:
                logger.warning("Failed to load embedding model: %s", e)
                self._session = None
                self._tokenizer = None
            self._loaded = True

        return (self._session, self._tokenizer)

    def _load_model(self) -> tuple:
        """Load ONNX model and tokenizer. May trigger download."""
        import onnxruntime as ort
        from tokenizers import Tokenizer

        model_path = self._ensure_model()
        tokenizer_path = self._ensure_tokenizer()

        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 2
        sess_options.inter_op_num_threads = 1
        sess_options.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )

        session = ort.InferenceSession(
            model_path, sess_options, providers=["CPUExecutionProvider"]
        )
        tokenizer = Tokenizer.from_file(tokenizer_path)

        # Warmup
        self._encode("warmup", session, tokenizer)

        return (session, tokenizer)

    def _ensure_model(self) -> str:
        """Locate or download the ONNX model file."""
        # 1. Env override
        env_path = os.environ.get("FISH_TRAIL_MODEL_PATH")
        if env_path and os.path.exists(env_path):
            return env_path

        # 2. Local cache in base_dir/models/
        variant = self._choose_variant()
        local_path = os.path.join(self._base_dir, "models", variant)
        if os.path.exists(local_path):
            return local_path

        # 3. Download via huggingface_hub
        from huggingface_hub import hf_hub_download

        return hf_hub_download(
            repo_id=_REPO_ID,
            filename=f"onnx/{variant}",
        )

    def _ensure_tokenizer(self) -> str:
        """Locate or download tokenizer.json."""
        # Check local
        local_path = os.path.join(self._base_dir, "models", "tokenizer.json")
        if os.path.exists(local_path):
            return local_path

        # Download
        from huggingface_hub import hf_hub_download

        return hf_hub_download(
            repo_id=_REPO_ID,
            filename="tokenizer.json",
        )

    def _choose_variant(self) -> str:
        """Select platform-appropriate quantized model variant."""
        machine = platform.machine().lower()

        if machine in ("aarch64", "arm64"):
            return "model_qint8_arm64.onnx"

        # Default: x86_64 AVX2 variant
        return "model_quint8_avx2.onnx"

    def _encode(self, text: str, session=None, tokenizer=None) -> "ndarray | None":
        """Encode text to 384-dim normalized embedding."""
        import numpy as np

        if session is None or tokenizer is None:
            session, tokenizer = self._get_session()
            if session is None:
                return None

        # Tokenize
        encoded = tokenizer.encode(text)
        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

        # Inference
        outputs = session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "token_type_ids": token_type_ids,
            },
        )

        # Mean pooling (pooling NOT included in ONNX export)
        token_embeddings = outputs[0]  # shape: (1, seq_len, 384)
        pooled = self._mean_pool(token_embeddings, attention_mask)

        # L2 normalize
        return self._normalize(pooled)[0]

    def _mean_pool(self, token_embeddings, attention_mask):
        """Apply mean pooling with attention mask."""
        import numpy as np

        # Expand mask to match embedding dims
        mask_expanded = np.expand_dims(attention_mask, axis=-1)  # (1, seq_len, 1)
        mask_expanded = np.broadcast_to(mask_expanded, token_embeddings.shape).astype(
            np.float32
        )

        # Sum masked embeddings
        sum_embeddings = np.sum(token_embeddings * mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)

        return sum_embeddings / sum_mask

    def _normalize(self, embeddings):
        """L2 normalize embeddings."""
        import numpy as np

        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.clip(norms, a_min=1e-9, a_max=None)
        return embeddings / norms
