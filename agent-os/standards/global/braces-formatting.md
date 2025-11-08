# Braces & Formatting

- **Braces on a new line** for functions and blocks.

```cpp
// Good
int32 GetSize() const
{
    return Size;
}

// Avoid (inline single‑line)
int32 GetSize() const { return Size; }
```

- **Always include braces** for single‑statement blocks (`if`, `for`, `while`) to avoid errors in edits.
- Maintain consistent indentation (tabs/spaces per repo settings).
