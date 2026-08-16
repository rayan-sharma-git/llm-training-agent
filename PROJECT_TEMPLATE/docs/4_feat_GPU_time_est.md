# GPU Training Time Estimator — Feature Report

**Feature Status:** Already implemented but broken/incomplete — now fixed and extended

---

## 1. What It Was Before

The repository already contained a **`CostEstimator`** module at `backend/analyzers/cost_estimator.py`. This was the original GPU/time estimation logic. It worked as follows:

- Used a **hard-coded GPU database** with 10 GPUs (RTX 4090 → GTX 3060, A100, H100, etc.)
- **Always assumed an RTX 4090 (163 TFLOPS FP16)** as the reference GPU regardless of the user's actual hardware
- Extracted model parameter count from the model name (e.g., "7b" → 7B parameters)
- Computed estimates using the standard FLOPs formula: `6 × P × tokens`
- Used regex to extract `batch_size`, `epochs`, `max_seq_length`, `gradient_accumulation_steps` from config files
- Produced a `CostEstimate` schema with:
  - `estimated_training_time` (string like `"0.5x-1.5x"`)
  - `estimated_gpu_hours` (float)
  - `estimated_vram_usage` (string)
  - `estimated_checkpoint_size` (string)
  - `estimated_storage_requirement` (string)
  - `compatible_hardware` (list of GPU names)
  - `assumptions` (list)
  - `confidence` (low/medium/high)

## 2. Why It Was a Problem

The original `CostEstimator` had several severe issues:

1. **No automatic GPU detection** — it always used RTX 4090 specs regardless of actual hardware
2. **Scanner hardware detection was a stub** — `scanner.py` `_detect_hardware()` always returned `{"gpu_available": False, "cpu_count": 4}`
3. **No multi-GPU support** — always assumed a single GPU
4. **No heterogeneous GPU detection** — couldn't detect or warn about mixed GPU setups
5. **No VRAM feasibility check** — couldn't tell if the model would fit on the actual GPU
6. **No calibration benchmark** — no way to measure actual throughput
7. **No quick/calibrated dual-mode estimation**
8. **Misleading time ranges** — the estimate was formatted as `0.5x-1.5x` (i.e., 50% to 150% of a single reference time), not an actual time range
9. **No UI integration** — the GPU estimate was buried in the report JSON, not shown in the chat sidebar
10. **Fixed GPU dropdown approach** — users couldn't add new GPUs

## 3. How It Was Fixed

### New Files Created

| File | Purpose |
|------|---------|
| `backend/hardware/__init__.py` | Hardware module initializer |
| `backend/hardware/gpu_detector.py` | Automatic GPU detection (PyTorch CUDA, nvidia-smi, CUDA env) |
| `backend/hardware/gpu_time_estimator.py` | Estimation engine (theoretical + calibrated) |
| `backend/tests/test_gpu_time_estimator.py` | 27 unit tests (all pass) |

### Files Modified

| File | Change |
|------|--------|
| `backend/scanner/scanner.py` | `_detect_hardware()` now calls `detect_gpus()` instead of returning a stub |
| `backend/models/schemas.py` | Added `GPUInfo`, `HardwareInfo`, `GPUTimeEstimate`, `CalibrationResult` schemas; added `gpu_time_estimate` and `hardware_detection` fields to `EngineeringReport` |
| `backend/api/routes.py` | Added `GET /gpu/detect`, `GET /gpu/specs`, `POST /gpu/estimate`, `POST /gpu/calibrate` endpoints; integrated GPU estimation into `/project/analyze` |
| `backend/reports/generator.py` | Added `gpu_time_estimate` and `hardware_detection` parameters to `generate()` |
| `backend/analyzers/cost_estimator.py` | Kept as fallback legacy estimator (extended with new GPU DB lookup) |
| `extension/src/services/apiClient.ts` | Added `detectGpu()`, `listGpuSpecs()`, `estimateGpuTime()`, `calibrateGpu()` methods |
| `extension/src/views/chatWebviewProvider.ts` | Added `postAssistantMessage()` public method |
| `extension/src/commands/analyzerCommands.ts` | GPU estimate results are formatted and displayed in the chat sidebar after analysis |
| `extension/src/extension.ts` | Passes `chatProvider` to `registerAnalyzerCommands` |

## 4. How It Works Now

### GPU Detection
The system detects GPUs using three strategies in order:

1. **PyTorch CUDA APIs** — `torch.cuda.is_available()`, `torch.cuda.device_count()`, `torch.cuda.get_device_properties()`
2. **nvidia-smi** — runs `nvidia-smi --query-gpu=...` to get GPU name, VRAM, driver version, compute capability, utilization
3. **Environment variables** — checks `CUDA_VISIBLE_DEVICES`, `CUDA_VERSION`

Detected GPUs are stored as a list of `GPUInfo` objects, each containing:
- GPU index, name, VRAM (MB and GB), compute capability, driver version, CUDA version, utilization

The detector also computes aggregate properties:
- `gpu_count` — number of GPUs
- `heterogeneous` — true if GPUs have different names
- `total_vram_mb`, `max_vram_mb`, `min_vram_mb`

### Multi-GPU Support
- GPUs are represented as a **list**, not a single object
- Scaling factors are applied per distribution strategy:
  - `single`: 1.0
  - `dp` (Data Parallel): 0.90
  - `ddp` (DistributedDataParallel): 0.85
  - `fsdp` (Fully Sharded Data Parallel): 0.80
  - `deepspeed`: 0.80
  - `accelerate`: 0.85
- **Heterogeneous GPUs** are explicitly detected and warned about — effective scaling is reduced
- Multi-GPU time is **not** simply Single-GPU ÷ N; communication overhead is accounted for

### Training Configuration Extraction
The `extract_training_config_from_context()` function reads:
- **Model name** and parameter count (from model name patterns like "7b", "1.1b")
- **Dataset samples** (from `project_statistics`)
- **Batch size** (from `per_device_train_batch_size`)
- **Gradient accumulation** (from `gradient_accumulation_steps`)
- **Epochs** (from `num_train_epochs`)
- **Max steps** (from `max_steps`)
- **Sequence length** (from `max_seq_length`)
- **Precision** (fp16, bf16, 8bit, 4bit detection)
- **Training method** (full, lora, qlora, peft detection)
- **Gradient checkpointing**, **dataloader workers**
- **Framework** and **distributed strategy** (huggingface, pytorch, deepspeed, fsdp, accelerate)

### Estimation Engine (`GPUTimeEstimator`)

**Quick Estimate mode:**
- Uses FLOPs formula: `total_flops = 6 × P × tokens`
- Applies precision factor (`fp32`: 1.0, `fp16`/`bf16`: 0.5, `8bit`: 0.4, `4bit`: 0.3)
- Applies training method factor (`full`: 1.0, `lora`: 0.7, `qlora`: 0.6, `peft`: 0.7)
- Uses actual detected GPU TFLOPS from performance database
- If GPU is unknown, uses a conservative generic estimate (25 TFLOPS) with lower confidence
- Multi-GPU scaling applied with communication overhead
- GPU utilization assumed ~85%
- Data loading overhead accounted for
- **Returns**: estimated time, lower/upper bound, confidence, throughput, total steps

**Calibrated Estimate mode:**
- Uses measured `steps_per_sec` from a short benchmark
- Higher confidence (high vs medium/low)
- Tighter bounds (±15% vs ±20%/±35%)

### VRAM Feasibility
The estimator computes estimated VRAM usage based on:
- Model weights (`precision × params`)
- Optimizer states (full: 8 bytes/param, LoRA/QLoRA: 0.08 bytes/param)
- Activations (based on batch size × seq length)
- Gradients
- Overhead

If estimated VRAM > available VRAM, a warning is generated with suggested fixes.

### Calibration Benchmark
- Uses a small representative Transformer model (max 1B params, adjusted to fit GPU)
- Runs for 30 seconds by default (clamped to 10-60 seconds)
- Measures: steps/sec, samples/sec, tokens/sec
- Never starts full training
- Explicitly initiated by the user via the API
- Falls back to theoretical estimator if benchmark fails

### UI Integration
After running **Analyze Project** (`llmTrainingAgent.analyzeProject`), the GPU estimate is automatically **displayed in the chat sidebar** with:
- GPU hardware summary (name, VRAM, CUDA version)
- Estimated training time
- Likely range
- Confidence level
- Estimation mode (Quick vs Calibrated)
- Throughput (steps/sec)
- VRAM feasibility check
- Warnings and assumptions

## 5. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/gpu/detect` | GET | Detect GPU hardware |
| `/api/v1/gpu/specs` | GET | List known GPU specs in database |
| `/api/v1/gpu/estimate` | POST | Estimate GPU training time |
| `/api/v1/gpu/calibrate` | POST | Run calibration benchmark |

## 6. Testing

All tests pass:
- **27 new tests** for GPU detection, estimation, config extraction, calibration
- **57 total tests** pass across the full backend test suite
- **Real GPU detection tested** on this machine: NVIDIA GeForce RTX 2050, 4GB VRAM, CUDA 13.0
- **Real estimation test**: TinyLlama 1.1B QLoRA on RTX 2050 → ~5.3 days (range 4.2d–6.3d, medium confidence)

## 7. Limitations

- Estimates are theoretical approximations based on FLOPs calculations — actual performance varies with model architecture
- The GPU performance database is authoritative for known GPUs; unknown GPUs get generic estimates with lower confidence
- Calibration benchmark uses a simplified model, not the actual model architecture
- VRAM estimation is approximate
- Calibration requires PyTorch with CUDA installed