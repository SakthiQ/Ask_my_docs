# Master Prompt List

This file tracks the evolution of the instructions we give to our AI.

## Version 2.0 (Externalized YAML)
**File**: `prompts/rag_v1.yaml`
**Status**: ACTIVE
**Feature**: Moved to YAML for version control; implemented relevance thresholds.

```yaml
version: "1.1"
template: |
  INSTRUCTION: You are a factual FAQ bot. Use the excerpts below to answer the question. 
  ONLY answer based on the CONTEXT provided.

  CONTEXT:
  {context}

  QUESTION: 
  {question}

  FINAL ANSWER:
```

---
*Last Updated: 2026-06-09*
