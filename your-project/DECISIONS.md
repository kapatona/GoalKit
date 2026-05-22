# DECISIONS

Append-only durable decisions for the active `/goal`.

Do not rewrite old rows. If a decision changes, append a new row and point the
old row at the reversal.

Format:

```text
[D# YYYY-MM-DD] decision=<short>; evidence=<path/command>; reversed_by=<D#|n/a>
```

Rows:

```text
none
```
