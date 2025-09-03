
# 🤖 InfinitePay Support Chatbot

This project was developed as part of the **Software Engineer Challenge – CloudWalk**.It implements a **multi-agent chatbot system** with:

- **RouterAgent (LLM + regex fallback)** → decides which agent should handle a message.
- **MathAgent (LLM + AST parser)** → evaluates mathematical expressions securely.
- **KnowledgeAgent (RAG + Redis)** → retrieves knowledge from InfinitePay Help Center articles via embeddings.

The stack includes:

- **Frontend:** React + TailwindCSS
- **Backend:** FastAPI
- **Redis Stack:** stores chat history + embeddings (RediSearch)
- **Kubernetes Manifests:** organized for Deployment, Service, Ingress
- **Structured logging**
- **Unit + e2e tests**

---

## 🖼️ Screens

- Conversation view + sources
- Multi-conversation sidebar
<img width="1118" height="711" alt="Screenshot 2025-09-03 at 18 07 25" src="https://github.com/user-attachments/assets/4a8afbf7-3d7a-4fbc-ad26-266acd6ba239" />


---

## 🌐 Public Demo

- **Frontend:** [https://modular-chatbot-cw.vercel.app/](https://modular-chatbot-cw.vercel.app/)
- **Backend:** [https://chatbot-backend-z6ga.onrender.com](https://chatbot-backend-z6ga.onrender.com)

> Deployment was done using **Render (backend + Redis Cloud)** and **Vercel (frontend)**.
> Details can be found in the [Deployment](#-deployment) section.
> The frontend is configured with `VITE_API_BASE=https://<your-backend-domain>`.

---

## 🛠️ Architecture

```text
Frontend (React + Tailwind)
         │
         ▼
Backend (FastAPI)
   ┌───────────────┐
   │ RouterAgent   │───► MathAgent (LLM + AST parser)
   │ (LLM + regex) │
   └───────────────┘
            │
            └────► KnowledgeAgent (RAG + Redis)
                           │
                           ▼
                   Redis Stack (RediSearch + JSON)
                   └── stores: embeddings + chat history
```

- **RouterAgent:** Uses an LLM (`gpt-4o-mini`) to classify messages with fallback regex for robustness.
- **MathAgent:** Converts natural language math to expressions → parses with Python `ast` → safe calculation (no `eval`).
- **KnowledgeAgent:** Embeddings stored in Redis RediSearch, retrieval of top-k chunks, then LLM generates contextual answers with cited sources.
- **Logs:** Structured with `structlog` → includes agent name, latency, conversation_id, user_id, etc.
- **Security:** Prompt-injection filter + AST parser for math.

---

## 📦 Run Locally (Docker Compose)

Requirements:

- Docker + Docker Compose installed
- `.env` file configured (see `.env.example`)

<pre class="overflow-visible!" data-start="2350" data-end="2484"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span># Build and start everything</span><span>
docker compose up --build

</span><span># Backend: http://localhost:8000</span><span>
</span><span># Frontend: http://localhost:5173</span><span>
</span></span></code></div></div></pre>

### Endpoints

<pre class="overflow-visible!" data-start="2501" data-end="2717"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span># Healthcheck</span><span>
curl http://localhost:8000/health

</span><span># Chat</span><span>
curl -X POST http://localhost:8000/api/chat \
  -H </span><span>"Content-Type: application/json"</span><span> \
  -d </span><span>'{"message":"2+2","user_id":"u1","conversation_id":"c1"}'</span><span>
</span></span></code></div></div></pre>

---

## Environment variables table

```md
## 🔧 Environment Variables

| Variable           | Where            | Example / Notes                                   |
|--------------------|------------------|---------------------------------------------------|
| `OPENAI_API_KEY`   | Backend          | OpenAI API key                                    |
| `REDIS_URL`        | Backend          | `redis://localhost:6379/0` or `rediss://…:port/0` |
| `KB_INDEX`         | Backend (opt)    | Default: `kb_idx`                                 |
| `KB_PREFIX`        | Backend (opt)    | Default: `kb:doc:`                                |
| `KB_TOP_K`         | Backend (opt)    | Default: `3`                                      |
| `EMBED_MODEL`      | Backend (opt)    | Default: `text-embedding-3-small`                 |
| `MATH_LLM_MODEL`   | Backend (opt)    | Default: `gpt-4o-mini`                            |
| `ROUTER_LLM_MODEL` | Backend (opt)    | Default: `gpt-4o-mini`                            |
| `VITE_API_BASE`    | Frontend build   | e.g. `https://<your-backend-domain>`              |
```

---

## ☸️ Run with Kubernetes (Minikube)

Requirements:

- `kubectl` and `minikube` installed
- Start cluster: `minikube start`
- Enable ingress: `minikube addons enable ingress`

<pre class="overflow-visible!" data-start="2899" data-end="3045"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span># Create namespace</span><span>
kubectl create ns cw-chat

</span><span># Apply all manifests</span><span>
kubectl -n cw-chat apply -f k8s/

</span><span># Tunnel ingress</span><span>
minikube tunnel
</span></span></code></div></div></pre>

Then open:

- **Frontend:** [http://chatbot.local/](http://chatbot.local/?utm_source=chatgpt.com)
- **Backend:** [http://chatbot.local/api/health]()

> ⚠️ Add this line to `/etc/hosts`:

<pre class="overflow-visible!" data-start="3180" data-end="3211"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>127.0</span><span>.0</span><span>.1</span><span> chatbot.</span><span>local</span><span>
</span></span></code></div></div></pre>

---

## 📂 Project Structure

`app/
  backend/         # FastAPI + agents + services
  frontend/        # React + Tailwind UI
docker-compose.yml # Local development
k8s/               # Kubernetes manifests (Deploy, Service, Ingress)
tests/             # Unit + e2e tests
tools/             # build_kb_redis.py → ingest KB docs into Redis`

## 📊 Example Logs

<pre class="overflow-visible!" data-start="3585" data-end="4164"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>
  </span><span>"timestamp"</span><span>:</span><span></span><span>"2025-08-28T16:16:29.700Z"</span><span>,</span><span>
  </span><span>"level"</span><span>:</span><span></span><span>"INFO"</span><span>,</span><span>
  </span><span>"agent"</span><span>:</span><span></span><span>"RouterAgent"</span><span>,</span><span>
  </span><span>"conversation_id"</span><span>:</span><span></span><span>"c1"</span><span>,</span><span>
  </span><span>"user_id"</span><span>:</span><span></span><span>"u1"</span><span>,</span><span>
  </span><span>"decision"</span><span>:</span><span></span><span>"KnowledgeAgent"</span><span>,</span><span>
  </span><span>"execution_time_ms"</span><span>:</span><span></span><span>155</span><span>,</span><span>
  </span><span>"mode"</span><span>:</span><span></span><span>"llm"</span><span>,</span><span>
  </span><span>"confidence"</span><span>:</span><span></span><span>0.92</span><span>,</span><span>
  </span><span>"reason"</span><span>:</span><span></span><span>"Message classified as informational"</span><span>
</span><span>}</span><span>
</span><span>{</span><span>
  </span><span>"timestamp"</span><span>:</span><span></span><span>"2025-08-28T16:16:29.701Z"</span><span>,</span><span>
  </span><span>"level"</span><span>:</span><span></span><span>"INFO"</span><span>,</span><span>
  </span><span>"agent"</span><span>:</span><span></span><span>"KnowledgeAgent"</span><span>,</span><span>
  </span><span>"conversation_id"</span><span>:</span><span></span><span>"c1"</span><span>,</span><span>
  </span><span>"user_id"</span><span>:</span><span></span><span>"u1"</span><span>,</span><span>
  </span><span>"execution_time_ms"</span><span>:</span><span></span><span>112</span><span>,</span><span>
  </span><span>"summary"</span><span>:</span><span></span><span>{</span><span>
    </span><span>"sources"</span><span>:</span><span></span><span>[</span><span>"https://ajuda.infinitepay.io/pt-BR/articles/6645035-o-que-e-o-infinitetap"</span><span>]</span><span>
  </span><span>}</span><span>
</span><span>}</span><span>
</span></span></code></div></div></pre>

---

## 🧪 Tests

Run all tests:

<pre class="overflow-visible!" data-start="4199" data-end="4220"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>pytest -q
</span></span></code></div></div></pre>

Covers:

- Router classification (unit)
- MathAgent calculations (unit)
- Chat endpoint end-to-end

---

## “How KB is built” (simple, actionable)

```md
## 📚 Knowledge Base (RAG)

Content is fetched from InfinitePay Help Center, saved as markdown, embedded, and upserted into Redis (RediSearch).

Add/refresh content:
```

```bash
# 1) Fetch pages to markdown (app/backend/data/knowledge/*.md)
python tools/ingest_urls.py \
  "https://ajuda.infinitepay.io/pt-BR/articles/6645035-o-que-e-o-infinitetap" \
  "<add-more-help-center-urls-here>"

# 2) Embed + upsert into Redis (uses OPENAI_API_KEY + REDIS_URL)
python tools/build_kb_redis.py
```

---

## 🔐 Security

- Regex + heuristics against **prompt injection**
- Safe AST evaluation for math (no `eval`)
- Error handlers → return JSON only, no stack traces

---

## 🌐 Deployment

### Backend (Cloud Run)

- Image: `docker.io/tomazdimas/chatbot-backend:vX`
- Env vars set in Cloud Run console
- Redis hosted on Redis Cloud (Free Tier)
- Public URL: `https://chatbot-backend-xxxx.a.run.app`

### Frontend (Vercel)

- Deployed from GitHub repo
- Env `VITE_API_BASE` points to backend
- Public URL: `https://chatbot-frontend.vercel.app`

---

## 📝 Troubleshooting

- **500 Internal Error** → check backend logs:
  <pre class="overflow-visible!" data-start="5235" data-end="5307"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl -n cw-chat logs deploy/chatbot-backend --</span><span>tail</span><span>=50
  </span></span></code></div></div></pre>
- **Ingress timeout** → ensure `minikube tunnel` is running and `/etc/hosts` has `chatbot.local`
- **KB empty** → rerun ingestion script:
  <pre class="overflow-visible!" data-start="5448" data-end="5500"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>python tools/build_kb_redis.py <url>
  </span></span></code></div></div></pre>

---

## 🚀 Deployment

- **Backend:** Render (Docker)
  - Dockerfile at repo root (`WORKDIR /app`, runs `uvicorn app.backend.main:app`)
  - Env: `OPENAI_API_KEY`, `REDIS_URL`, etc.
- **Frontend:** Vercel
  - Build: `npm run build`
  - Output: `dist`
  - Env: `VITE_API_BASE=https://<backend>`

- **Redis:** Redis Cloud (Free tier)
  - `REDIS_URL=rediss://default:<pwd>@<host>:<port>/0`

---

## ✅ Challenge Checklist

- [X] RouterAgent (LLM + fallback)
- [X] MathAgent (LLM + AST)
- [X] KnowledgeAgent (RAG + Redis)
- [X] Structured logging
- [X] Security measures (prompt injection, no eval)
- [X] Frontend (multi-conversation UI)
- [X] Tests (unit + e2e)
- [X] Docker Compose
- [X] Kubernetes (Deploy + Service + Ingress)
- [X] README (documentation)
- [X] Public deployment link (Cloud Run + Vercel)

---

## 👤 Author

**Tomaz Dimas**

[LinkedIn](https://www.linkedin.com/in/tomazdimas/) • [GitHub](https://github.com/TomazDimas)
