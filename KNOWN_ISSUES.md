# Known Issues — Sprint 5 QA Pass

Found during manual end-to-end walkthrough on `fix/sprint-5-touchups`. Logged here to fix later.

---

## OPEN — Dashboard doesn't reliably redirect to onboarding for incomplete profile

**Found:** 2026-06-25
**Severity:** High — new users can land on a blank dashboard instead of onboarding

**Scenario:**
1. Signed up with an account, started onboarding, hit an error on step 1, never completed it
2. Later signed in with the same account via Google → landed directly on `/portal/dashboard` instead of `/onboarding/step/1` → blank page (no data)
3. Reloaded `localhost:3000` → this time correctly redirected to `/onboarding/step/1`

**Suspected area:** `/portal/dashboard` and `/portal` layout both independently call `GET /api/v1/profile` and redirect via `if (!profile?.is_complete) redirect(...)` (`frontend/src/app/(portal)/dashboard/page.tsx:25`, `frontend/src/app/(portal)/layout.tsx`). Backend logs for the account checked during this session showed a clean `404` (no profile row, no `is_complete: true` anywhere) — so the inconsistency wasn't reproduced server-side in this session. Possible causes not yet confirmed:
- Race condition right after Clerk OAuth redirect — token/org claims not fully synced on the very first server-rendered request
- Duplicated profile-check logic across layout/page (3 copies total — see `frontend/src/app/(onboarding)/onboarding/step/[step]/page.tsx` too) getting inconsistent results between near-simultaneous requests

**Next step:** reproduce with browser devtools open — capture Network tab response for `/api/v1/profile` at the moment the blank dashboard shows, and the console errors, plus confirm which account/tenant_id so logs can be matched.

**Not yet fixed.**
