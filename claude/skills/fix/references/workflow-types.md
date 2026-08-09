# Type Error Fix Workflow

Type errors are usually Quick: infer the mode and diagnose, edit, and check inline.

## Workflow

1. Run the project-native typecheck or the narrowest command that reproduces the
   named error.
2. Read the failing type, value origin, public contract, and local typing pattern.
3. Correct the root type or narrowing error; do not use `any`, unsafe assertions,
   or unrelated casts merely to silence the compiler.
4. Rerun the original typecheck and inspect direct dependents of the changed type.
5. Fix additional errors only when they share the same root cause or the user asked
   for the whole typecheck surface; report unrelated pre-existing failures.

Typical commands:

```bash
bun run typecheck
tsc --noEmit
npx tsc --noEmit
```

The fresh deterministic typecheck can be the regression proof. Add a runtime test
only when behavior, serialization, validation, or another runtime contract changed.
