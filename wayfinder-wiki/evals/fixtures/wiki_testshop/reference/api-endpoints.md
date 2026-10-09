---
layer: L4
scope: HTTP API lookup
read_when: [api, endpoint, route, http]
parent: 01_MAP.md
source: src/ordering/router.py
---

# API Endpoints

| Method | Path | Domain | Notes |
|--------|------|--------|-------|
| POST | /orders | ordering | Create order |
| DELETE | /orders/:id | ordering | Full order cancel only |
| GET | /orders/:id | ordering | Order detail |
