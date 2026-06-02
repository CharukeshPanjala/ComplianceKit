from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common.models.regulation import Regulation
from common.models.rule import Rule
from common.db.session import get_admin_session

router = APIRouter(prefix="/api/v1/regulations", tags=["regulations"])


@router.get("")
async def list_regulations(session: AsyncSession = Depends(get_admin_session)):
    result = await session.execute(select(Regulation).order_by(Regulation.name))
    regulations = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "full_name": r.full_name,
            "jurisdiction": r.jurisdiction,
            "authority": r.authority,
            "status": r.status,
            "effective_date": r.effective_date,
            "source_url": r.source_url,
        }
        for r in regulations
    ]


@router.get("/{regulation_name}/rules")
async def list_rules(
    regulation_name: str,
    category: str | None = Query(None),
    severity: str | None = Query(None),
    check_type: str | None = Query(None),
    session: AsyncSession = Depends(get_admin_session),
):
    reg_result = await session.execute(
        select(Regulation).where(Regulation.name == regulation_name.upper())
    )
    regulation = reg_result.scalar_one_or_none()
    if not regulation:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Regulation '{regulation_name}' not found")

    query = select(Rule).where(Rule.regulation_id == regulation.id, Rule.is_active == True)

    if category:
        query = query.where(Rule.category == category.lower())
    if severity:
        query = query.where(Rule.severity == severity.lower())
    if check_type:
        query = query.where(Rule.check_type == check_type.lower())

    query = query.order_by(Rule.article_number)
    result = await session.execute(query)
    rules = result.scalars().all()

    return {
        "regulation": regulation_name.upper(),
        "total": len(rules),
        "rules": [
            {
                "id": str(r.id),
                "rule_id": r.rule_id,
                "article": r.article,
                "article_number": r.article_number,
                "title": r.title,
                "chapter": r.chapter,
                "category": r.category,
                "plain_english": r.plain_english,
                "severity": r.severity,
                "fine_tier": r.fine_tier,
                "is_mandatory": r.is_mandatory,
                "check_type": r.check_type,
                "applies_to_b2c": r.applies_to_b2c,
                "applies_to_b2b": r.applies_to_b2b,
                "remediation_hint": r.remediation_hint,
            }
            for r in rules
        ],
    }