# Optional Kokoro neural speech integration

The main web app uses browser speech by default, with no neural inference cost.

## Architecture

Browser -> Reading Assistant FastAPI `POST /neural-speech` -> separately hosted
Kokoro-compatible `POST /v1/audio/speech` -> MP3 -> browser audio player.

Kokoro inference is **not** installed on the Render free web service.
The optional backend expects an OpenAI-compatible speech API that accepts:
`{model:"kokoro", input:"...", voice:"af_heart", response_format:"mp3", speed:1.0}`.

Set these Render environment variables only after deploying and testing a
compatible provider:

- `ENABLE_NEURAL_TTS=1`
- `KOKORO_API_URL=https://your-secure-kokoro-host`
- `KOKORO_API_KEY=<secret>` (if the provider requires bearer authentication)

The endpoint limits text to 800 characters and limits the returned audio to 8 MB.
The UI intentionally generates only the first 800 characters of the selected page.
This is a proof of integration, **not** yet full-page or full-book neural narration.

## Public deployment safety

**Do not enable neural TTS on a public service yet.** The application currently
has no end-user authentication, per-user quotas, or rate limiting; enabling the
proxy would expose the paid/compute-backed Kokoro service to unrestricted requests.
Add those controls before activation.

## Test plan

1. Verify `GET /neural-status` reports `enabled:false` without configuration.
2. Verify `POST /neural-speech` returns 503 when disabled.
3. Deploy an authenticated Kokoro-compatible API independently.
4. Add server-side rate limits, user authentication, and request quotas.
5. Enable environment variables, verify a short audio sample, then test browser
   playback on desktop and mobile.

The original Colab TTS notebook and experimental checkpoint are separate from
this pretrained neural-voice integration.
