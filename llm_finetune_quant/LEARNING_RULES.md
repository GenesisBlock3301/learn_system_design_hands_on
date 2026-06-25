# LEARNING RULES — How To Actually Get Deep In The AI Era

> Companion to `ROADMAP.md`. The roadmap tells you **what** to do. This file tells you **how to learn it deeply**, so you don't end up six months later with a shipped repo and a shallow brain.

---

## The Real Problem (read once, internalize forever)

AI makes the *output* easy and the *learning* invisible. You can ship working code without ever forming a mental model. Six months later you can't debug it, can't extend it, can't explain it in an interview. You become a typist for a machine.

**The struggle IS the learning.** Every time you ask AI for the answer instead of attempting it yourself, you trade understanding for speed. Sometimes that trade is fine (boilerplate). For your 6-month capstone, it is poison.

The rules below exist to make sure you actually *learn* the LLM stack, not just *complete* the roadmap.

---

## The 8 Core Rules

### Rule 1 — Try first, ask second (the 25-minute rule)
Before asking AI or googling, spend **25 minutes** attempting the concept/code yourself. Use only the official docs and your existing knowledge. Write down what you tried and where you got stuck. Only *then* go to AI — and feed it your stuck-point, not the whole problem.

**Why:** the stuck-point is where learning happens. Skipping it means skipping the learning.

### Rule 2 — Use AI as a Socratic tutor, not an answer machine
Never ask "give me the code for X." Instead ask:
- "Quiz me on X — five questions, hardest first, don't give answers yet."
- "I think LoRA works like *<my explanation>*. Where am I wrong?"
- "What would break my mental model of X? Give me three edge cases."
- "Play devil's advocate against my decision to use *<choice>*."

**Why:** an explanation you read fades in a week. A wrong answer you got corrected on stays for years.

### Rule 3 — The Feynman checkpoint
Before moving from one stage to the next, **write a 1-page explanation in your own words**, no AI, no copy-paste, no looking. If you can't, you haven't learned it. Go back.

Save these in `llm_finetune_quant/notes/stage-N.md`. They become your portfolio of understanding.

### Rule 4 — Primary sources > blogs > AI summaries
Hierarchy of trust:
1. **The original paper** (arxiv.org) — slow, hard, correct
2. **Official docs** (HuggingFace, PyTorch, llama.cpp README)
3. **Reference implementations** (Karpathy, Unsloth, llama.cpp source)
4. **Reputable blogs** (Sebastian Raschka, Lilian Weng, Chip Huyen)
5. **AI summary** — only after 1–4, to fill specific gaps

Most people invert this. Don't.

### Rule 5 — Build before you read
For every concept, write the *toy version* before reading the production version.
- Before reading PEFT's LoRA code → implement LoRA in 30 lines of PyTorch.
- Before using `bitsandbytes` → quantize a single tensor by hand to 4-bit.
- Before using `llama.cpp` → load a tiny model with raw `transformers` and generate token-by-token in a loop.

The toy version reveals the *real* problem the library is solving. Without it, the library is magic.

### Rule 6 — Verify everything (AI hallucinates, blogs go stale)
Every claim — from AI, from a blog, from this file — gets verified by:
- Running the code yourself
- Reading the source of the function being called
- Checking the API still exists in the version you're using

If a memory or tutorial says "use `X.from_pretrained_quantized()`" — grep the library. It may have been renamed or removed.

### Rule 7 — Spaced repetition on the hard concepts
Maintain a `llm_finetune_quant/flashcards.md` file. Each time you hit a non-obvious idea, add a Q/A pair. Examples:
- Q: Why does QLoRA need double quantization? A: …
- Q: What does `Q4_K_M` mean letter-by-letter? A: …
- Q: Why does prompt caching work for the prefix but not the suffix? A: …

Review it for 10 minutes every Monday. This is the difference between "I read about it" and "I know it."

### Rule 8 — Teach it back
At the end of each stage, write a **public** artifact:
- A blog post, a Twitter thread, a YouTube whiteboard, or a README explainer.
- Public is the point — the fear of being wrong forces you to actually verify.

If month 6 is your *only* public artifact, stages 1–5 will be lazy.

---

## How To Use AI (concrete prompts that produce learning)

These replace the lazy "explain X to me" prompt.

| Goal | Lazy prompt | Deep-learning prompt |
|---|---|---|
| Understand a concept | "Explain LoRA." | "I think LoRA freezes the base model and trains two low-rank matrices A and B such that ΔW = BA. Where is my explanation wrong, missing nuance, or oversimplified? Don't re-explain from scratch — only correct me." |
| Read a paper | "Summarize the QLoRA paper." | "I'll read the QLoRA paper section by section. After each section I'll tell you what I understood. You quiz me with one hard question per section. Don't summarize ahead of me." |
| Debug | "Fix this error." | "Here's the error and what I think is happening: *<theory>*. Tell me if my theory is right before suggesting a fix. If wrong, ask me what I'd check next, don't just give me the answer." |
| Choose a tool | "Should I use Unsloth or PEFT?" | "List the trade-offs Unsloth vs PEFT in a table. Then ask me three questions about my use case. Then *I* will pick — you don't pick for me." |
| Code review | "Review my training script." | "Review my training script and find three things that are *subtly wrong* — not style issues. Don't tell me what they are; tell me where to look and what symptom they'd cause." |

Pin this table somewhere visible.

---

## How To Web Search (with direction)

Most "search the web" defaults to Google → first blog. That's how shallow learning happens. Direct yourself:

### Search operators that find primary sources
- `site:arxiv.org "QLoRA"` — find the paper, not summaries of it
- `site:github.com "lora" language:python stars:>500` — reference implementations
- `"llama.cpp" Q4_K_M site:github.com` — official discussion of the format
- `inurl:huggingface.co/docs` — official docs only
- `intitle:"from scratch" LoRA` — implementations that teach by building

### The 3-source rule
Before believing any non-trivial claim, find it in **three independent sources**, at least one of which is primary (paper or official docs). If you can only find it on one Medium post, treat it as unverified.

### Ranked sources for this roadmap
**Papers (arxiv):**
- LoRA: 2106.09685 · QLoRA: 2305.14314 · DPO: 2305.18290 · GPTQ: 2210.17323 · AWQ: 2306.00978 · Speculative decoding: 2211.17192

**Official docs:**
- huggingface.co/docs/peft · huggingface.co/docs/transformers · huggingface.co/docs/trl · github.com/ggerganov/llama.cpp · github.com/ml-explore/mlx · github.com/unslothai/unsloth

**People worth reading deeply (not just skimming):**
- Andrej Karpathy (YouTube + nanoGPT) · Sebastian Raschka (book + blog) · Lilian Weng (lilianweng.github.io) · Chip Huyen (huyenchip.com) · Hamel Husain (hamel.dev — evals) · Eugene Yan (eugeneyan.com)

**YouTube channels:**
- 3Blue1Brown (intuition for transformers) · Karpathy (build-from-scratch) · Yannic Kilcher (paper deep-dives) · Umar Jamil (line-by-line implementations)

If a source isn't on this list and isn't a primary doc — be suspicious. Most LLM blogspam is wrong or outdated within months.

---

## Per-Stage Deep Checkpoints

You may not move to the next stage until you can answer these **without looking, without AI**. Write the answers in `notes/stage-N.md`.

### After Stage 1 (Basics)
1. Walk through one forward pass of a transformer with concrete tensor shapes for batch=2, seq=4, d_model=8, heads=2.
2. Why does the attention mechanism scale dot products by `1/sqrt(d_k)`?
3. What does a tokenizer's BPE merge rule look like? Hand-tokenize the word "tokenization."
4. Why is causal masking necessary in a decoder? What breaks without it?
5. In one sentence: why is LoRA cheaper than full fine-tuning in *memory*, not just compute?

### After Stage 2 (Data)
1. What's the worst kind of label noise for instruction tuning, and why?
2. Show me one bad example from your dataset. Explain *why* it's bad, then how you fixed it.
3. Why 200 golden examples and not 20 or 2000? What changes at each scale?
4. How do you know your train/val/test split has no leakage?

### After Stage 3 (Fine-tune)
1. With LoRA rank `r=16`, alpha=32 — what is the effective scaling factor and why?
2. What is the dtype of: (a) frozen base weights in QLoRA, (b) LoRA adapters, (c) gradients, (d) optimizer states? Why each?
3. Why does QLoRA use double quantization? What does it save?
4. If your loss is going down but golden-set quality is going down — what is happening?
5. SFT vs DPO vs RLHF — one sentence each on what signal they use.

### After Stage 4 (Quantize)
1. What does `Q4_K_M` mean, letter by letter?
2. Why does quantization hurt some layers more than others? Which layers?
3. On your golden 200, what was the quality drop from Q8 → Q4? Why is it nonlinear?
4. Why is GGUF Q4 fine on a Mac but you'd want AWQ on a GPU?

### After Stage 5 (Serve)
1. Continuous batching vs static batching — what's the difference and when does it matter?
2. How does prefix caching work? Why can it cache the system prompt but not the user message?
3. Speculative decoding — when does it slow you *down*?
4. Walk through what happens, step by step, when a request hits `llama.cpp server`.

### After Stage 6 (Eval)
1. Why is perplexity a bad eval for instruction-tuned models?
2. LLM-as-judge — name three failure modes and how to mitigate each.
3. Your golden set is 200 examples. What's the statistical confidence on a 5% quality difference? (Hint: it's smaller than you think.)

If you can't answer 80% of these per stage — **don't move on**. The roadmap is sequential for a reason; later stages compound earlier confusion.

---

## Anti-Patterns To Catch Yourself Doing

- **Tab-storm without notes.** 40 tabs open, brain empty. Close them. Open one. Take notes.
- **Copy-paste from AI without retyping.** Retyping is mechanical but it's the last line of defense against not-reading.
- **"It works, ship it."** Working ≠ understood. If you can't explain *why* it works, you have a black box, not a skill.
- **Skipping the paper because the blog is shorter.** The blog is shorter because it's wrong about the parts that matter.
- **Asking AI to write your golden eval set.** That set is your taste, your judgment, your moat. Hand-pick it.
- **Optimizing prematurely.** Don't quantize before fine-tuning works. Don't add DPO before SFT works. Don't add caching before throughput is measured.
- **Confusing activity with progress.** A weekend of "exploring HuggingFace" with no artifact is a wasted weekend.

---

## Weekly Cadence

| When | What |
|---|---|
| **Monday (10 min)** | Review `flashcards.md`. Add any new cards from last week. |
| **Mid-week (1 hr)** | Read one primary source (paper section or docs page). Write 5 sentences in your own words. |
| **Friday (30 min)** | Update `notes/stage-N.md`. What did I learn? What am I still confused about? |
| **End of stage** | Public artifact (blog/thread/repo update). Pass the checkpoint quiz with no AI. |

This is non-negotiable scaffolding. Without it, six months will pass and you will have a working repo and no understanding to show for it.

---

## The One-Sentence Rule

**If AI is doing the thinking, you are not learning. Use AI to test your thinking, not replace it.**

Tape it above your monitor.
