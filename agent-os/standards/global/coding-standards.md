# Coding Standard (Project‑Level)

This document summarizes the rules we adopt from Epic’s official standard and clarifies how we apply them in this project.

## Class Organization
- Order members for *readers*, not writers: **public → protected → private**.
- Keep headers minimal and stable; push heavy includes into `.cpp` when possible.

## Copyright Header
For engine‑facing or distributable sources, the first line **must** be:

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
```

(For internal project files, use the studio’s copyright header if different.)

## Functions & Booleans
- Bool functions ask a **true/false** question: `IsVisible()`, `ShouldClearBuffer()`.
- Procedures (void) use **strong verb + object**: `InitializeSubsystem()`, `RegisterInput()`.
- When returning `bool`, make the meaning of `true` obvious (e.g., `IsTeaFresh()` rather than `CheckTea()`).
