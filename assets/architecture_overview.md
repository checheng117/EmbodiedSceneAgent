# Architecture Overview

```mermaid
flowchart LR
    OBS[Observation] --> MEM[Scene Memory]
    MEM --> PLN[Planner]
    PLN --> EXE[Executor]
    EXE --> VER[Verifier]
    VER --> REP[Replanner]
    REP --> SAFETY{Semantic acceptance filter}
    SAFETY -- accept --> EXE
    SAFETY -- reject --> REP
    VER --> GUARD[Repeated-no-effect guard]
    GUARD --> REP
    MODEL[Tuned model path: Qwen2.5-VL-3B LoRA] --> PLN
    MODEL --> REP
```

Notes:

- The semantic acceptance filter blocks schema-valid but scene-inconsistent revised plans before execution.
- The repeated-no-effect guard stops repeated ineffective retries and writes explicit terminal evidence.
- The tuned model path is currently centered on `Qwen/Qwen2.5-VL-3B-Instruct` minimal LoRA artifacts.
