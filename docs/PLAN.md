# Plan

Decisions: English only for now (i18n deferred); real product; hosted TTS API; Railway; multilingual by user location; real Postgres; security first.

## Milestones (one per branch/session)
1. Merge migration/enum fixes (done, branch `fix/migrations-and-enum-values`).
2. Security baseline: rate limits on auth, secrets from env only, strict CORS/hosts, password reset tokens expiry, upload size/type limits, remove `/auth/admin/reset` or lock it down, consent flow for voice cloning.
3. (DEFERRED) i18n: next-intl, locale detection (Accept-Language, then IP geolocation fallback), language switcher, `en` + `ne` first.
4. TTS provider: interface in `voice_engine/`, hosted provider adapter, drop Tortoise/torch from default deps.
5. Storage: S3-compatible bucket for audio; Railway Postgres + Redis.
6. Railway deploy: healthcheck, migrations on start, env docs, backups.
7. Billing/limits (optional).

## Open questions
- Which hosted TTS provider (voice cloning quality for Nepali/Hindi)?
- Free tier vs paid?
