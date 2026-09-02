# Cloudflare Zero Trust deployment

The production route is **Netlify browser → Cloudflare Access → Cloudflare Tunnel → FastAPI 127.0.0.1:8000 → Ollama 127.0.0.1:11434**.

Do not open router ports 8000 or 11434. Do not create a tunnel to Ollama.

1. Own/use a domain in Cloudflare and enable Zero Trust.
2. Run `install-cloudflared.bat`, then authenticate with `cloudflared tunnel login`.
3. Create a tunnel: `cloudflared tunnel create qa-matrix-ai`.
4. Create DNS routing: `cloudflared tunnel route dns qa-matrix-ai qa-api.example.com`.
5. Copy `config.yml.example` to your local Cloudflared config location and fill in your tunnel UUID, credentials path, and hostname. Never commit the credential JSON.
6. In Cloudflare Zero Trust → Access → Applications, create a **Self-hosted** application for `qa-api.example.com`. Use deny-by-default and allow only approved identities. This gives browser users the Cloudflare Access layer before FastAPI's own login.
7. Run the tunnel: `cloudflared tunnel run qa-matrix-ai`. For 24/7 Windows operation you can install the tunnel as a Windows service using Cloudflare's supported service command after the config is verified.
8. Put the final `https://qa-api.example.com/api` value in Netlify as `VITE_API_BASE_URL`, and set the exact Netlify origin in backend `.env` under `CORS_ORIGINS`.

Never put a Cloudflare service-token secret in Vite. A browser bundle is public. If you later need machine-to-machine service tokens, keep those in a trusted server component such as a Netlify Function, not React.
