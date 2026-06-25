# LLM Fine-Tuning, Quantization & Cost Optimization — Simple Roadmap

A 6-month, hands-on path to take **one small open-source model**, **fine-tune it on your business domain**, **shrink it with quantization**, and **serve it cheaply** — all on a **Mac M4 Air + free Kaggle/Colab**, $0 spend.

> **Read [`LEARNING_RULES.md`](./LEARNING_RULES.md) before starting.** It defines *how* to learn deeply at each stage — Socratic AI prompts, primary-source web search, per-stage checkpoint quizzes you must pass without AI. This roadmap is the *what*; that file is the *how*.

---

## The Big Picture (read this first)

You will go through 5 simple stages. That's it.

```
1. LEARN  →  2. DATA  →  3. FINE-TUNE  →  4. SHRINK  →  5. SERVE
 basics       collect     teach the      quantize       run it
              and clean   model your     to 4-bit       cheap and
              the data    domain                        fast
```

At the end you'll have **one small model (3B–7B)** that:
- knows your business domain better than ChatGPT does
- runs on your Mac at 30+ tokens/sec
- costs $0 to operate
- is shareable on the internet (HuggingFace Spaces demo)

That artifact is the goal. Everything below is the path to it.

---

## Pick Your Domain First (Day 1)

Before anything: pick **one** real business area you'll work on the whole 6 months. Examples:

- Customer support for an e-commerce store
- Legal contract clause classifier
- Medical insurance claim summarizer
- Code reviewer for your own codebase
- Real-estate listing writer
- Financial earnings-call Q&A

Specificity is the entire point. A general "I'll do NLP" project will fail. A specific "I'll fine-tune a model to write product descriptions for shoe stores" project will succeed.

---

## Stage 1 — Learn the Basics (Weeks 1–4)

**Goal:** understand what you're about to do.

### What to know
- How a transformer works at a high level (attention, tokens, decoding)
- The difference between pre-training, fine-tuning, and RLHF/DPO
- What a tokenizer does and why token count = money
- What a LoRA adapter is and why people use it instead of full fine-tuning

### Where to learn (all free)
- **HuggingFace NLP Course** — chapters 1–4 → https://huggingface.co/learn/nlp-course
- **Karpathy on YouTube** — *Let's build GPT* and *Let's build the GPT tokenizer*
- **Sebastian Raschka** — *Build a Large Language Model From Scratch* (book + free GitHub notebooks)

### What to build this stage
A simple notebook on your Mac that:
1. Loads a tiny model (SmolLM2-360M or Qwen2.5-0.5B)
2. Generates some text
3. Counts tokens for a few sample inputs

**Done when:** you can explain to a friend what a token is, what a LoRA is, and why we don't full-fine-tune.

---

## Stage 2 — Build Your Dataset (Weeks 5–8)

**Goal:** get 2,000–10,000 high-quality examples for your domain. **This is 80% of the work.**

### The simple recipe

1. **Collect or generate** examples in this format:
   ```json
   { "instruction": "...", "input": "...", "output": "..." }
   ```
2. **Where to get data:**
   - Real data from your work / a public dataset / scraped (legal) source
   - **Or generate it for free** using Groq or Cerebras (Llama 3.3 70B, free tier)
3. **Clean it:**
   - Remove duplicates
   - Strip personal info (use `presidio`, free)
   - Hand-check 50 examples — if they look bad, fix them before continuing
4. **Split it:**
   - 80% train, 10% validation, 10% test
   - Hand-pick **200 "golden examples"** — these are how you'll judge every future model

### Tools (all free)
- `datasets` (HuggingFace) — load and split
- `distilabel` — synthetic data pipelines
- Groq / Cerebras / Google AI Studio — free LLM APIs to generate examples

### Done when
- You have a dataset CSV/JSONL with clean train/val/test splits
- You have 200 golden examples you trust
- You can confidently grade any model output as "good" or "bad" by hand

> **Rule:** if your data is bad, no fine-tuning trick will save you. Spend time here.

---

## Stage 3 — Fine-Tune Your Model (Weeks 9–14)

**Goal:** teach a small open model your domain using QLoRA.

### The simplest possible path

1. Open **Kaggle** (30 free GPU hours/week — best free GPU you can get)
2. Fork an **Unsloth notebook** → https://github.com/unslothai/unsloth
3. Replace their dataset with yours
4. Pick a model: **Llama-3.2-3B-Instruct** or **Qwen2.5-3B-Instruct** to start
5. Click run. Wait 1–3 hours. Done.

### What to actually learn while doing this

- **LoRA rank** — try 8, 16, 64. Plot quality vs adapter size.
- **Learning rate** — start at 2e-4 for QLoRA. Don't change it until you understand why.
- **Sequence length** — match your data's actual length. Don't waste GPU on padding.
- **Eval after training** — run your 200 golden examples, compare to the base model. **If you can't see improvement, your data is bad** (back to Stage 2).

### Optional: Preference Tuning (DPO)
After SFT works, try DPO to nudge the model toward "preferred" answers:
1. Take 500 outputs from your fine-tuned model
2. Hand-fix 500 of them → now you have (bad, good) pairs
3. Run DPO (Unsloth has a free notebook for this too)
4. Compare on golden set

Skip DPO if your SFT model is already good enough. Don't add complexity for its own sake.

### Done when
- Your fine-tuned model **clearly beats** the base model on your golden 200 examples
- You can reproduce the training run from a single config file
- The adapter is saved on your HuggingFace account

---

## Stage 4 — Shrink the Model (Weeks 15–18)

**Goal:** make your model 4–8× smaller and faster, with little quality loss.

### The simple version

On your Mac, run `llama.cpp` or `mlx-lm convert` to turn your 7B model from ~14GB to ~4GB. That's it.

### What to actually do

1. **Convert** your fine-tuned model to GGUF (`llama.cpp` does this in one command).
2. **Quantize** it 3 ways: `Q8_0` (8-bit, near-perfect), `Q5_K_M` (5-bit, balanced), `Q4_K_M` (4-bit, smallest).
3. **Re-run your golden 200 examples** on each version.
4. **Pick the smallest one** that still passes your quality bar.

That's the whole "Pareto frontier" — quality vs size. You'll feel where the cliff is once you do it.

### What to know (don't memorize, just understand)

| Format | What it is | When to use |
|---|---|---|
| **GGUF (Q4_K_M)** | `llama.cpp` 4-bit | Mac, CPU, edge — your default |
| **MLX 4-bit** | Apple-native | Best speed on M-series Macs |
| **AWQ / GPTQ** | GPU 4-bit | Skip for now — needs CUDA |
| **bitsandbytes NF4** | Training-time 4-bit | What you used in Stage 3 |

### Done when
- You have a `.gguf` file under 5GB that runs on your Mac
- You wrote one paragraph explaining which quant level you chose and why

---

## Stage 5 — Serve It Cheap and Fast (Weeks 19–22)

**Goal:** turn the model into a usable API/demo, and learn cost levers.

### The simple version

```bash
ollama create mymodel -f Modelfile
ollama run mymodel
```

That's a working local API. Now layer on the optimizations.

### Five cost levers (each one a real win)

1. **Quantization** — already done in Stage 4. Biggest win.
2. **Prompt caching** — if you have a long system prompt, cache it. Free 50–90% input cost reduction.
3. **Batching** — `llama.cpp server` does continuous batching. Run multiple requests at once.
4. **Speculative decoding** — small "draft" model + your 7B model = 2× faster. Free.
5. **Output limits** — cap `max_tokens` and use stop sequences. Cheap output > expensive output.

### Free tools to use

- **Ollama** — one-line local serving
- **llama.cpp server** — production-grade, continuous batching, prefix caching
- **MLX-LM server** — Mac-native, OpenAI-compatible API
- **HuggingFace Spaces** — free public demo with Gradio

### Token / Prompt Optimization (works even without fine-tuning)

These save money before you even fine-tune. Most teams overspend 3–10× on tokens just from sloppy prompts.

- **Tighten the schema** — return JSON with enums, not prose
- **Cache stable system prompts** — Anthropic / OpenAI / Gemini all support it
- **Compress with LLMLingua** — shrink long context 3–10× with little quality loss
- **Route cheap → expensive** — try a small model first, escalate only when needed
- **RAG vs fine-tune** — if knowledge changes weekly, use RAG. If style/behavior must change, fine-tune.

### Done when
- Your model serves on your Mac at ≥30 tokens/sec
- You have a public Gradio demo on HuggingFace Spaces
- You measured "$/1k requests if I were renting a GPU" and can compare to GPT-4o-mini

---

## Stage 6 — Measure Everything (Weeks 23–24)

**Goal:** prove your model is actually good.

### Three things to set up

1. **Auto-eval on your golden 200** — runs on every change, fails if quality drops >2%
2. **Observability** — pipe requests through **Langfuse** (free 50k events/mo cloud)
3. **A simple cost dashboard** — $/1k requests, tokens in, tokens out, p95 latency

### Tools (all free)
- **Langfuse** — production observability, free cloud or self-host
- **Arize Phoenix** — fully free OSS, runs on your Mac
- **lm-evaluation-harness** — automated benchmark runner

### Done when
- A regression in your fine-tune fails CI before you ship it
- You can see token cost per request live on a dashboard

---

## The Capstone (the actual deliverable)

By month 6, you should have **one repo** with:

1. ✅ A 5k+ example domain dataset with 200 golden examples
2. ✅ A QLoRA-fine-tuned 3B–7B model (with training config)
3. ✅ A 4-bit GGUF quantized version
4. ✅ A `make run` command that serves it locally
5. ✅ A public HuggingFace Space demo
6. ✅ A `cost.md` showing $/1k requests vs GPT-4o-mini
7. ✅ A `README.md` telling the whole story

**Success criteria:**
- Your fine-tune is at least **80% as good** as GPT-4o-mini on your golden set
- It runs at **≥30 tokens/sec** on your M4 Air
- A stranger could clone the repo and reproduce it

Ship it on GitHub + write a short blog post. **That's your portfolio piece.**

---

## Free Hardware & Tools Cheatsheet

| What you need | Use | Why |
|---|---|---|
| **Long training runs** | Kaggle (30 hrs/wk dual T4) | Best free GPU, period |
| **Quick experiments** | Google Colab Free | Fast to iterate |
| **Inference + dev** | Your M4 Air | Always-on, MLX is fast |
| **Synthetic data** | Groq / Cerebras / Google AI Studio | Free Llama 70B / Gemini Flash |
| **Public demo** | HuggingFace Spaces | Free, shareable URL |
| **Observability** | Langfuse cloud free | 50k events/mo |
| **Experiment tracking** | Weights & Biases free | Unlimited personal projects |

**Total cost: $0**

---

## Recommended Models by Stage

| Stage | Model | Size | Where it runs |
|---|---|---|---|
| Learning | SmolLM2-360M | 360MB | M4 in seconds |
| First fine-tune | Llama-3.2-1B | 1GB | M4 directly |
| Real fine-tune | Llama-3.2-3B or Qwen2.5-3B | 3GB | Kaggle T4, 1–3 hrs |
| Capstone | Llama-3.1-8B or Qwen2.5-7B | 7–8GB | Kaggle dual-T4 + Unsloth |

All Apache 2.0 / Llama / MIT licensed. Free for learning **and** commercial use.

---

## 6-Month Calendar

| Month | What you do |
|---|---|
| **1** | Stage 1: Learn basics. Build first toy notebook. |
| **2** | Stage 2: Build your dataset. Hand-pick 200 golden examples. |
| **3** | Stage 3: First QLoRA fine-tune on Kaggle. Beat the base model. |
| **4** | Stage 4 + 5: Quantize. Serve locally. Add caching + batching. |
| **5** | Stage 6: Eval pipeline + observability. Polish prompts. |
| **6** | Capstone: HF Spaces demo, blog post, GitHub repo. |

---

## Top 5 Mistakes to Avoid

1. **Fine-tuning before trying a great prompt + RAG.** Often you don't need to fine-tune.
2. **Bad data, hoping the model fixes it.** It won't. Fix data first.
3. **No golden eval set.** Then you literally can't tell if you improved anything.
4. **Quantizing without re-evaluating on your domain.** Generic perplexity lies.
5. **Picking a base model by leaderboard.** Pick by *your* eval set, on *your* hardware.

---

## The One-Sentence Summary

**Pick a domain → make a small clean dataset → QLoRA-fine-tune a 3B–7B model on Kaggle → quantize it to 4-bit GGUF on your Mac → serve it with Ollama → demo it on HuggingFace Spaces.**

Everything else in this file is just detail on those eight steps. If you do them, you'll have a real, shippable, hireable LLM project — for $0.
