# rsp-mvp
rsp-mvp
Below is a **copy-paste prompt** you can hand straight to Codex (or any code-gen LLM).
It asks for a **minimal, compilable repo scaffold** that matches the spec we just drafted, but keeps the request small enough that the model can complete in one shot.

---

### 📋 Prompt for Codex (you send exactly this)

````text
# Goal
Create a new Git repository named `rsp-mvp`.  
It must compile and run “hello world” end-to-end for the RSP project.

## 1. Root layout
.
├── README.md
├── .gitignore
├── Cargo.toml          # Rust workspace
├── rsp_core/           # Rust crate: envelope codec
│   ├── Cargo.toml
│   └── src/lib.rs
├── rsp_cli/
│   ├── Cargo.toml
│   └── src/main.rs     # simple encode/decode CLI
├── py_binding/
│   ├── pyproject.toml
│   └── rsp_core_py/__init__.py  # calls Rust via pyo3 stub
└── tests/
    └── codec_roundtrip.rs

## 2. Content & constraints
* Workspace `Cargo.toml` declares two members: `rsp_core`, `rsp_cli`.
* `rsp_core::envelope` exports:
  ```rust
  pub struct Envelope { pub token: String }
  impl Envelope {
      pub fn encode(&self) -> Vec<u8>;
      pub fn decode(b: &[u8]) -> Self;
  }
````

Encode/Decode can be trivial (length-prefixed string) so it compiles.

* `rsp_cli`:

  * `cargo run -- encode "fire"` → prints hex bytes
  * `cargo run -- decode <hex>`  → prints token back
* `py_binding` uses `maturin` with `pyo3` to expose `encode`/`decode` to Python.
* Test `codec_roundtrip.rs` asserts encode→decode round-trip.
* README contains build instructions for Rust and Python.

## 3. Non-functional

* Must build on Rust 1.77+, edition 2021.
* `cargo test` passes.
* `maturin develop` installs the wheel and `python -c "import rsp_core_py as r; print(r.decode(r.encode('fire')))"` prints `fire`.

Generate all files in full.  No placeholder ellipses—every file must be complete and compilable.  Begin your answer with “\`\`\`bash” and output the file tree, then each file in fenced blocks.  End with a short note: “Scaffold ready.”  Do not explain further.

````

---

### 🏃‍♂️ How to use it

1. **Create an empty repo** (or Codespace).  
2. Paste the prompt above into Codex/ChatGPT with “Generate code” or similar.  
3. Copy the returned files into your repo.  
4. Run:
   ```bash
   cargo test
   cargo run --manifest-path rsp_cli/Cargo.toml -- encode "fire"
   maturin develop -m py_binding/pyproject.toml
   python - <<'PY'
   import rsp_core_py as r
   print(r.decode(r.encode("fire")))
   PY
````

You’ll have a compiling Rust workspace, a CLI, Python bindings, and a green test—all ready for the real RSP logic.

---

Need a deeper scaffold (graph store, API gateway, etc.)?
Just iterate: ask Codex to “add a RocksDB-backed store under `rsp_store/`” or “expand the CLI with `/fetch`”.

Let me know if you hit any bumps!
