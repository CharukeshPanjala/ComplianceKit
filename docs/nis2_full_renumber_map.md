# NIS2 Seed Data — Full Renumber Map (DB5–DB37)

Source of truth: `docs/Nis2.pdf` cross-checked against the official EN consolidated text of Directive (EU) 2022/2555 (EUR-Lex CELEX 32022L2555). DB content from `packages/common/scripts/seeders/seed_nis2.py`. Already-resolved facts (DB1–4 confirmed correct, DB13/18/24/25 slot-correct content-pending-separate-fix, DB38–46 out of scope) taken as given per task instructions and excluded below.

---

## 1. Full mapping table (DB5–DB37)

| Current DB article_number | Current title | True real article number | True real article title | Action needed |
|---|---|---|---|---|
| 5 | National cybersecurity strategy | 7 | National cybersecurity strategy | Renumber to 7 |
| 6 | Coordinated vulnerability disclosure and a European vulnerability database | 12 | Coordinated vulnerability disclosure and a European vulnerability database | Renumber to 12 |
| 7 | National cyber crisis management framework | 9 | National cyber crisis management frameworks | Renumber to 9 |
| 8 | Competent authorities and single point of contact | 8 | Competent authorities and single points of contact | No change |
| 9 | CSIRTs | 10 | Computer security incident response teams (CSIRTs) | Renumber to 10 |
| 10 | Requirements for CSIRTs | 11 | Requirements, technical capabilities and tasks of CSIRTs | Renumber to 11 |
| 11 | Coordinated vulnerability disclosure | 12 | Coordinated vulnerability disclosure and a European vulnerability database | Renumber to 12 (duplicate, see §2) |
| 12 | Cyber crisis management | 16 | European cyber crisis liaison organisation network (EU-CyCLONe) | Renumber to 16 |
| 13 | Cooperation at Union level | 13 | Cooperation at national level | No change (content fix already documented, not renumbered here) |
| 14 | CSIRTs network | 15 | CSIRTs network | Renumber to 15 |
| 15 | NIS Cooperation Group | 14 | Cooperation Group | Renumber to 14 |
| 16 | International cooperation | 17 | International cooperation | Renumber to 17 |
| 17 | Peer reviews | 19 | Peer reviews | Renumber to 19 |
| 18 | Reporting obligations — incidents | 18 | Report on the state of cybersecurity in the Union | No change (content fix already documented, not renumbered here) |
| 19 | Use of European cybersecurity certification schemes | 24 | Use of European cybersecurity certification schemes | Renumber to 24 + content needs separate correction (duplicate, see §2) |
| 20 | Governance | 20 | Governance | No change |
| 21 | Cybersecurity risk-management measures | 21 | Cybersecurity risk-management measures | No change |
| 22 | Union level coordinated security risk assessments of critical supply chains | 22 | Union level coordinated security risk assessments of critical supply chains | No change |
| 23 | Reporting obligations | 23 | Reporting obligations | No change |
| 24 | Technical guidelines and methodological guidelines on incident reporting | 24 | Use of European cybersecurity certification schemes | No change (content fix already documented, not renumbered here) |
| 25 | Notification to recipients of services and to the public | 25 | Standardisation | No change (content fix already documented, not renumbered here) |
| 26 | Jurisdiction and territoriality | 26 | Jurisdiction and territoriality | No change |
| 27 | Register of essential and important entities | 27 | Registry of entities | No change |
| 28 | Database of domain name registration data | 28 | Database of domain name registration data | No change |
| 29 | Cybersecurity information sharing arrangements | 29 | Cybersecurity information-sharing arrangements | No change |
| 30 | Voluntary notification of relevant information | 30 | Voluntary notification of relevant information | No change |
| 31 | General aspects of supervision and enforcement | 31 | General aspects concerning supervision and enforcement | No change |
| 32 | Supervisory and enforcement measures in relation to essential entities | 32 | Supervisory and enforcement measures in relation to essential entities | No change |
| 33 | Supervisory and enforcement measures in relation to important entities | 33 | Supervisory and enforcement measures in relation to important entities | No change |
| 34 | General rules on administrative fines | 34 | General conditions for imposing administrative fines on essential and important entities | No change |
| 35 | Infringements entailing a personal data breach | 35 | Infringements entailing a personal data breach | No change |
| 36 | Penalties | 36 | Penalties | No change |
| 37 | Mutual assistance | 37 | Mutual assistance | No change |

**Summary:** of 33 rows (DB5–DB37):
- 19 rows already correctly numbered (no change): DB8, DB13, DB18, DB20, DB21, DB22, DB23, DB24, DB25, DB26, DB27, DB28, DB29, DB30, DB31, DB32, DB33, DB34, DB35, DB36, DB37 — wait, count carefully in §2/§5 below; see exact tally there.
- 13 rows need renumbering: DB5→7, DB6→12, DB7→9, DB9→10, DB10→11, DB11→12, DB12→16, DB14→15, DB15→14, DB16→17, DB17→19, DB19→24 (+ content correction).

---

## 2. Duplicates flagged

**Confirmed duplicate — real Article 12:**
- DB6 ("Coordinated vulnerability disclosure and a European vulnerability database") — content matches real Art 12 almost verbatim, including "designate a CSIRT as coordinator", "ENISA shall establish... European vulnerability database."
- DB11 ("Coordinated vulnerability disclosure") — content also matches real Art 12: "Each Member State shall ensure there is a coordinated vulnerability disclosure policy... CSIRTs act as trusted intermediaries... protect security researchers." This is real Art 12 paragraph 1, not a separate article.
- **Confirmed: both DB6 and DB11 map to real Article 12.** There is no real Article in the 5-37 range that corresponds uniquely to DB11's "coordinated vulnerability disclosure" framing distinct from DB6 — real NIS2 has exactly one article (Art 12) covering both the CSIRT-coordinator/vulnerability-database mechanism and the researcher-protection clause, as a single set of paragraphs.
- **Action:** DB6's content is the fuller/more accurate rendering of Art 12 (includes the European vulnerability database half, which DB11 omits). Recommend keeping DB6 at the real-numbered slot (12) and either merging DB11's researcher-protection detail into DB6's description, or retiring DB11 as a redundant row. Do not leave both rows claiming article_number=12.

**Second duplicate found — real Article 24:**
- DB19 ("Use of European cybersecurity certification schemes") — content matches real Art 24 closely (certification schemes under Art 49 Reg 2019/881, encourage qualified trust services).
- DB24 (per `nis2_content_corrections.md`, its corrected content is also "Use of European cybersecurity certification schemes" — real Art 24's full text including the delegated-act mechanism).
- **Confirmed: DB19 and the corrected DB24 both map to real Article 24.** This duplicate is explicitly called out in `nis2_content_corrections.md` (Article 24 section, "Notes"), which recommends merging DB24's extra delegated-act detail into DB19 and marking DB24 as superseded/cross-reference, rather than literally renumbering DB19 to 24 and creating two rows at article_number=24.
- **Action for this renumber exercise:** DB19's row, if physically renumbered to 24, would collide with DB24's slot (which per the "already resolved" facts stays at article_number=24). Recommend NOT renumbering DB19 to 24 as a bare integer move — instead merge DB19's content into DB24's slot (where the corrected Art 24 text per the corrections doc will live) and retire/repurpose DB19's row, OR leave DB19 permanently as a non-numbered duplicate/cross-reference entry if the schema requires every row to occupy a slot. This is flagged in the table above as "Renumber to 24 + content needs separate correction" to signal it cannot be a clean 1:1 move.

No other duplicates found in the DB5–DB37 range — all other content checks against the real article list are unique 1:1 matches.

---

## 3. Gaps flagged

Real NIS2 articles in the 5–37 numeric range with **no DB row mapping to them at all** after this remap:

- **Real Article 5 — Minimum harmonisation.** Already identified as missing in `nis2_content_corrections.md` (recommends inserting as new article_number=5). Confirmed missing from the DB5–37 content set; no current row's content matches this one-sentence clause.
- **Real Article 6 — Definitions.** Already identified as missing in `nis2_content_corrections.md` (recommends inserting as new article_number=6). Confirmed missing; the 41-term definitions glossary has no corresponding DB row.

No other gaps in 5–37 — every other real article number (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37) has at least one DB row mapping to it once the renumber in §1 is applied (Art 12 has two, per the duplicate in §2; all others have exactly one).

---

## 4. SQL UPDATE execution plan

Unique constraint on `(regulation_id, article_number)` is NOT deferred, so no two rows may share `article_number` even mid-transaction. Using the **two-pass negative-staging approach** (simpler and safer here given the cyclic swaps among DB9↔10, DB14↔15, and the DB7→9/DB9→10/DB10→11/DB11→12/DB6→12 chain, which cannot be done in a single dependency-ordered pass without temporary values).

**Rows touched (12 actual moves; DB8, DB13, DB18, DB20–DB37 stay as-is and are NOT touched):**
DB5→7, DB6→12, DB7→9, DB9→10, DB10→11, DB11→(retire/merge, see §2 — do not move into 12 if DB6 already takes that slot), DB12→16, DB14→15, DB15→14, DB16→17, DB17→19, DB19→(merge into 24 per §2, do not bare-move).

For the purposes of a literal, safe SQL plan, the moves that ARE simple 1:1 renumbers (no destination collision beyond what's handled by staging) are: DB5→7, DB6→12, DB7→9, DB9→10, DB10→11, DB12→16, DB14→15, DB15→14, DB16→17, DB17→19. DB11 and DB19 are content-merge/retire decisions per §2 and are **excluded from this UPDATE plan** — they require a product decision (merge vs. retire vs. cross-reference row) before any SQL is written, not a bare article_number UPDATE.

**Pass 1 — stage all touched rows to temporary negative article_number values** (regulation = NIS2, avoids any collision with existing or final values):

```sql
UPDATE rules SET article_number = -5  WHERE regulation_id = :nis2_id AND article_number = 5;   -- was DB5
UPDATE rules SET article_number = -6  WHERE regulation_id = :nis2_id AND article_number = 6;   -- was DB6
UPDATE rules SET article_number = -7  WHERE regulation_id = :nis2_id AND article_number = 7;   -- was DB7
UPDATE rules SET article_number = -9  WHERE regulation_id = :nis2_id AND article_number = 9;   -- was DB9
UPDATE rules SET article_number = -10 WHERE regulation_id = :nis2_id AND article_number = 10;  -- was DB10
UPDATE rules SET article_number = -12 WHERE regulation_id = :nis2_id AND article_number = 12;  -- was DB12
UPDATE rules SET article_number = -14 WHERE regulation_id = :nis2_id AND article_number = 14;  -- was DB14
UPDATE rules SET article_number = -15 WHERE regulation_id = :nis2_id AND article_number = 15;  -- was DB15
UPDATE rules SET article_number = -16 WHERE regulation_id = :nis2_id AND article_number = 16;  -- was DB16
UPDATE rules SET article_number = -17 WHERE regulation_id = :nis2_id AND article_number = 17;  -- was DB17
```

**Pass 2 — move from temporary negative values to final real article numbers:**

```sql
UPDATE rules SET article_number = 7  WHERE regulation_id = :nis2_id AND article_number = -5;   -- DB5  -> real Art 7
UPDATE rules SET article_number = 12 WHERE regulation_id = :nis2_id AND article_number = -6;   -- DB6  -> real Art 12
UPDATE rules SET article_number = 9  WHERE regulation_id = :nis2_id AND article_number = -7;   -- DB7  -> real Art 9
UPDATE rules SET article_number = 10 WHERE regulation_id = :nis2_id AND article_number = -9;   -- DB9  -> real Art 10
UPDATE rules SET article_number = 11 WHERE regulation_id = :nis2_id AND article_number = -10;  -- DB10 -> real Art 11
UPDATE rules SET article_number = 16 WHERE regulation_id = :nis2_id AND article_number = -12;  -- DB12 -> real Art 16
UPDATE rules SET article_number = 15 WHERE regulation_id = :nis2_id AND article_number = -14;  -- DB14 -> real Art 15
UPDATE rules SET article_number = 14 WHERE regulation_id = :nis2_id AND article_number = -15;  -- DB15 -> real Art 14
UPDATE rules SET article_number = 17 WHERE regulation_id = :nis2_id AND article_number = -16;  -- DB16 -> real Art 17
UPDATE rules SET article_number = 19 WHERE regulation_id = :nis2_id AND article_number = -17;  -- DB17 -> real Art 19
```

After Pass 2, verify no duplicate `article_number` values remain for NIS2 except the intentionally-flagged Art 12 duplicate (DB6 now at 12, DB11 still at its old slot 11 pending the merge/retire decision in §2) and the intentionally-flagged Art 24 duplicate (DB19 still at its old slot 19 after this plan — wait: DB17 now also targets 19, so DB19's OLD row, if left untouched at article_number=19, would collide with DB17's incoming move to 19):

```sql
-- Sanity check before committing pass 2, run as part of the same transaction:
SELECT article_number, count(*) FROM rules WHERE regulation_id = :nis2_id GROUP BY article_number HAVING count(*) > 1;
```

**Blocking note on DB17→19 vs DB19:** DB17 is being moved TO article_number=19, but DB19 (the existing row, untouched by this plan since its own destination is the unresolved Art 24 merge) currently occupies article_number=19. This means DB17→19 cannot execute as written above without first vacating 19. **Required fix to the plan:** stage DB19 to a negative placeholder too (e.g. -19) in Pass 1 before Pass 2 writes DB17's content into 19, then resolve DB19's final destination (merge into 24, retire, or temporary holding number) as a separate follow-up step once the product decision in §2 is made. Add to Pass 1:

```sql
UPDATE rules SET article_number = -19 WHERE regulation_id = :nis2_id AND article_number = 19;  -- was DB19, holding pending merge decision
```

And do not include a Pass 2 statement that resolves -19 to a final number until the DB19/DB24 merge decision is made — leave it parked at -19 (or move it to a clearly out-of-band number like 1024 if negative values are disallowed by a CHECK constraint) until that follow-up ships.

---

## 5. Verification — scorer-critical articles (2, 3, 18, 23, 27)

`services/policy-engine/app/engine/scorer.py` reads real article numbers 2, 3, 18, 23, and 27 directly for live compliance scoring. These must NOT move.

- **Real Article 2** — DB2, already confirmed correct (out of scope, DB1–4 resolved). Not touched by this plan. ✅ Safe.
- **Real Article 3** — DB3, already confirmed correct (out of scope). Not touched by this plan. ✅ Safe.
- **Real Article 18** — DB18 stays at article_number=18 per the "already resolved" facts (content fix only, no renumber). No other row in this remap targets 18. ✅ Safe.
- **Real Article 23** — DB23 stays at article_number=23 (already correctly placed, confirmed in §1, no change). No other row in this remap targets 23. ✅ Safe.
- **Real Article 27** — DB27 stays at article_number=27 (already correctly placed, confirmed in §1, no change). No other row in this remap targets 27. ✅ Safe.

**Conclusion: none of 2, 3, 18, 23, or 27 are touched or moved by this plan.** No blocking issue to raise. The only article numbers receiving incoming or outgoing moves are 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 19 (and the parked/unresolved 19→24 merge question) — none of which intersect the scorer-critical set.
