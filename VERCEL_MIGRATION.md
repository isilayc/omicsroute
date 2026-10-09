# One Vercel project for OmicsRoute

The Next.js frontend and FastAPI backend are separate Vercel Services in one
deployment. Services is currently a Vercel beta feature. The project root must
be the repository root, not `frontend`.

- `/` and Next.js assets route to the static export in `frontend/out`.
  The planner runs in the browser; its server requests go to FastAPI.
- `/health`, `/v1/*`, `/docs`, `/openapi.json` and `/redoc` route to `api.main:app`.
- Production browser requests use the current origin. A stale Render API URL
  in the dashboard is overridden by `frontend/next.config.mjs`.
- `pyproject.toml` declares Python 3.12 and the API dependencies; the legacy
  Streamlit `app.py` is not the Vercel entrypoint.
- Catalogue audits run only when requested. Ordinary API requests time out
  after 30 seconds; literature and audit requests have a longer deadline.

## Deploy the migration

1. In the existing Vercel project, Settings -> Build and Deployment, change
   Root Directory from `frontend` to the repository root (empty field / `.`).
2. Remove old project-wide install/build/output overrides. Each service's
   framework and build settings are supplied by the root `vercel.json`.
3. Remove `NEXT_PUBLIC_OMICSROUTE_API_URL` pointing to Render from Production
   and Preview. It is no longer required. If external literature/reference API
   credentials were configured in Render, copy their values privately into
   Vercel Environment Variables, preserving the names used in `services/`.
4. Deploy the migration branch as a Preview first, then check the page and run
   the live HTTP test below against that Preview's URL. If Vercel protects the
   Preview, test through an authenticated browser; do not disable protection.
5. After verifying sample selection, organism identification, workflow exports,
   and a literature/reference lookup, merge and deploy to Production.
6. Verify the production URL before suspending Render. Retain Render until
   this check succeeds so the previous deployment remains recoverable.

## Tests

```sh
python -m pip install -r requirements.txt httpx
python tests/vercel_migration/test_http_flow.py
python tests/all_selection_matrix_v1/validate_all_selection_matrix_v1.py
python tests/web_parity_v1/validate_web_parity_v1.py
cd frontend
npm ci
npm run build
```

Live HTTP test (run from repository root):

```sh
python tests/vercel_migration/test_http_flow.py https://YOUR-DEPLOYMENT.vercel.app
```

Vercel CLI 63.1.0 recognizes both configured services. Local tests and Next.js
build success do not prove cloud deployment success; the live checks above
remain required. External literature providers may still be slow or rate-limit
requests. Moving hosting does not remove those provider delays.

## Rollback

Restore the previous Vercel deployment and project Root Directory `frontend`.
Restore the previous Render API URL environment variable if it was removed.
Keep Render running until production acceptance is complete.

References:
- https://vercel.com/docs/services
- https://vercel.com/docs/services/routing
- https://vercel.com/docs/frameworks/backend/fastapi
