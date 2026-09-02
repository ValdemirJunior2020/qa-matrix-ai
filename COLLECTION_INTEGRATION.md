# Open-source collection note

No large external repository was copied into QA Matrix AI because doing so would add unnecessary code and attack surface. The architecture already uses the focused open-source components requested: FastAPI, openpyxl/pandas, LlamaIndex, ChromaDB, Ollama, React/Vite and SQLite.

DeepSeek Harness and Strix remain optional and isolated. They are not required for normal QA Matrix questions, authentication, indexing, scoring guardrails, or server operation.
