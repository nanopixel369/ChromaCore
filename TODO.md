# TODO (Append-only Queue)

- [ ] TODO-001 (owner: task-author) Populate repo command primitives (build/test/lint/typecheck).
      Acceptance: `CHECKLIST.md` Code Integrity section has concrete commands (no placeholders) OR an explicit statement that commands are intentionally unavailable.
      Links: `CHECKLIST.md`

- [ ] TODO-010 (owner: algorithms) Determinism harness for Chromatic Gravity coordinate mapping.
      Acceptance: A repeatable verification hook exists showing identical hashtags → identical (L,a,b) outputs.
      Links: `Chromatic_Gravity_Spec.md`, `Semantic_Stack_Spec.md`

- [ ] TODO-020 (owner: database) Implement/verify SQLite schema + indexes + constraints for nodes.
      Acceptance: Schema matches spec (table definition + indexes) and a verification hook validates indexes exist.
      Links: `Chroma_Nodes_Specification.md`

- [ ] TODO-030 (owner: api) Align SDK public surface with spec (signatures, params, errors).
      Acceptance: Public API matches spec and has verification hook (tests or placeholder).
      Links: `Chroma_Core_SDK_API.md`

- [ ] TODO-040 (owner: plugins) Implement/verify Spectral Plugin hook semantics + API boundaries.
      Acceptance: Plugin registration, hook sequencing semantics, and boundary enforcement are tested/verified.
      Links: `Spectral_Plugins_Spec.md`

- [ ] TODO-050 (owner: backend) Implement/verify packer export/import/restore flows with integrity checks.
      Acceptance: .bpack manifest + payload integrity verification exists; import compatibility gates enforced.
      Links: `Chroma_Packer_Spec.md`

- [ ] TODO-060 (owner: frontend) Define client/UI consumption plan for SDK (no framework assumptions).
      Acceptance: A minimal client integration note exists (docs/tests), or a new frontend spec is added.
      Links: `Chroma_Core_SDK_API.md`

Rules:
- Append new items; do not reorder unless instructed.
- Mark done by checking the box and adding a short “Done:” note under the item.
- Every TODO must have measurable Acceptance criteria and an explicit owner persona.