# Hosted FastInfra Kokoro beta setup

Provider: https://api.fastinfra.ai

Never paste provider API keys into GitHub or chat. Create a FastInfra account and API key. Review pricing and authorize a small prepaid balance only if you choose.

Set these variables in the existing Reading Assistant Render service:

- ENABLE_NEURAL_TTS=1
- KOKORO_API_URL=https://api.fastinfra.ai
- KOKORO_API_KEY=<FastInfra API key; secret>
- NEURAL_ACCESS_TOKEN=<separate long random private beta token; secret>

The browser asks for NEURAL_ACCESS_TOKEN, never KOKORO_API_KEY. The backend sends the request to https://api.fastinfra.ai/v1/audio/speech with model hexgrad/kokoro-82m, requesting WAV audio. The provider key is kept server-side.

Keep neural speech disabled until the key and private token are configured. Do not share the beta token publicly. The beta gate is not a replacement for durable user quotas, distributed rate limiting, authentication, billing caps, and abuse controls. Keep prepaid credits minimal.

Smoke test: after configuring variables, upload a PDF, prepare a page, enter your beta access token, and press Play current page with neural voice. The neural preview covers only the first 800 characters of the page. The regular device voice can still read the whole document.

Before public rollout, add per-user limits, cost monitoring, chunking/caching, and a secure account system.
