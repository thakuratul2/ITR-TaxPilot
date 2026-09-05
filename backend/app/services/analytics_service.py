"""Analytics and launch telemetry service."""

import hashlib
import json
import logging
from collections import Counter
from datetime import datetime, timezone
import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import get_redis_client
from app.models.analytics import AnalyticsVisit
from app.schemas.analytics import (
    AnalyticsStatsResponse,
    GitHubRepoStats,
    TrackVisitRequest,
    TrackVisitResponse,
)

logger = logging.getLogger("app.services.analytics")

# In-memory fast counters and cache fallback
_IN_MEMORY_STATS = {
    "total_visits": 0,
    "unique_visitors": set(),
    "sources": Counter(),
    "recent_events": [],
}

_GITHUB_CACHE = {
    "repo": "thakuratul2/ITR-TaxPilot",
    "stars": 0,
    "forks": 0,
    "open_issues": 0,
    "cached_at": None,
    "last_fetch_ts": 0.0,
}


def classify_traffic_source(req: TrackVisitRequest, header_referrer: str | None = None) -> str:
    """Accurately classify traffic origin based on params, UTMs, and referrers."""
    # Check explicit ref
    ref_val = (req.ref or "").lower()
    utm_source_val = (req.utm_source or "").lower()
    referrer_val = (req.referrer or header_referrer or "").lower()

    if "producthunt" in ref_val or "producthunt" in utm_source_val or "producthunt.com" in referrer_val:
        return "producthunt"
    if "github" in ref_val or "github" in utm_source_val or "github.com" in referrer_val:
        return "github"
    if "twitter" in ref_val or "x.com" in referrer_val or "t.co" in referrer_val or "twitter.com" in referrer_val:
        return "twitter"
    if "linkedin" in ref_val or "linkedin.com" in referrer_val or "lnkd.in" in referrer_val:
        return "linkedin"
    if "google" in utm_source_val or "google.com" in referrer_val:
        return "google"
    if "reddit" in utm_source_val or "reddit.com" in referrer_val:
        return "reddit"

    if req.source and req.source.lower() not in ["direct", "unknown", ""]:
        return req.source.lower().strip()

    if referrer_val and not any(h in referrer_val for h in ["localhost", "127.0.0.1", "itr-taxpilot.onrender.com"]):
        # Extract host
        try:
            from urllib.parse import urlparse
            netloc = urlparse(referrer_val).netloc
            if netloc:
                return netloc.replace("www.", "")
        except Exception:
            pass

    return "direct"


async def fetch_github_stars(repo: str = "thakuratul2/ITR-TaxPilot", force_refresh: bool = False) -> GitHubRepoStats:
    """Fetch live GitHub stars & repository statistics with caching."""
    from app.core.config import get_settings
    settings = get_settings()

    if settings.APP_ENV == "test":
        return GitHubRepoStats(
            repo=repo,
            stars=12,
            forks=3,
            open_issues=0,
            cached_at=datetime.now(timezone.utc),
        )

    import time
    now_ts = time.time()

    # Return cached data if fetched in last 300 seconds (5 minutes)
    if not force_refresh and (now_ts - _GITHUB_CACHE["last_fetch_ts"] < 300) and _GITHUB_CACHE["cached_at"] is not None:
        return GitHubRepoStats(
            repo=_GITHUB_CACHE["repo"],
            stars=_GITHUB_CACHE["stars"],
            forks=_GITHUB_CACHE["forks"],
            open_issues=_GITHUB_CACHE["open_issues"],
            cached_at=_GITHUB_CACHE["cached_at"],
        )

    try:
        url = f"https://api.github.com/repos/{repo}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ITR-TaxPilot-LaunchTracker/1.0",
        }
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                _GITHUB_CACHE["repo"] = repo
                _GITHUB_CACHE["stars"] = int(data.get("stargazers_count", 0))
                _GITHUB_CACHE["forks"] = int(data.get("forks_count", 0))
                _GITHUB_CACHE["open_issues"] = int(data.get("open_issues_count", 0))
                _GITHUB_CACHE["cached_at"] = datetime.now(timezone.utc)
                _GITHUB_CACHE["last_fetch_ts"] = now_ts
                logger.info("Fetched live GitHub stars for %s: %s stars", repo, _GITHUB_CACHE["stars"])
            else:
                logger.warning("GitHub API returned status %s for %s: %s", resp.status_code, repo, resp.text[:100])
    except Exception as exc:
        logger.warning("Could not fetch live GitHub stars: %s (using cached fallback)", exc)

    return GitHubRepoStats(
        repo=_GITHUB_CACHE["repo"],
        stars=_GITHUB_CACHE["stars"],
        forks=_GITHUB_CACHE["forks"],
        open_issues=_GITHUB_CACHE["open_issues"],
        cached_at=_GITHUB_CACHE["cached_at"] or datetime.now(timezone.utc),
    )


async def record_visit(
    req: TrackVisitRequest,
    db: AsyncSession | None = None,
    client_ip: str | None = None,
    user_agent: str | None = None,
    header_referrer: str | None = None,
) -> TrackVisitResponse:
    """Record a page visit and update real-time telemetry counters."""
    classified_source = classify_traffic_source(req, header_referrer)

    # Hash IP for anonymous unique counting without storing raw PII
    ip_hash = None
    if client_ip:
        ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()[:16]

    visitor_key = req.visitor_id or ip_hash or "anon"

    # 1. Update in-memory fast metrics
    _IN_MEMORY_STATS["total_visits"] += 1
    _IN_MEMORY_STATS["unique_visitors"].add(visitor_key)
    _IN_MEMORY_STATS["sources"][classified_source] += 1

    event_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": classified_source,
        "path": req.path,
        "ref": req.ref,
        "utm_source": req.utm_source,
        "referrer": (req.referrer or header_referrer or "")[:100],
    }
    _IN_MEMORY_STATS["recent_events"].insert(0, event_record)
    if len(_IN_MEMORY_STATS["recent_events"]) > 50:
        _IN_MEMORY_STATS["recent_events"].pop()

    # 2. Redis atomic counters (if connected and not in test mode)
    from app.core.config import get_settings
    settings = get_settings()
    if settings.APP_ENV != "test":
        try:
            redis_client = await get_redis_client()
            if redis_client:
                pipe = redis_client.pipeline()
                pipe.incr("analytics:total_visits")
                pipe.incr(f"analytics:source:{classified_source}")
                pipe.sadd("analytics:unique_visitors", visitor_key)
                await pipe.execute()
        except Exception as exc:
            logger.debug("Redis analytics increment skipped: %s", exc)

    # 3. Database persistence (if DB session provided)
    if db:
        try:
            visit_record = AnalyticsVisit(
                visitor_id=req.visitor_id,
                source=classified_source,
                ref=req.ref,
                utm_source=req.utm_source,
                utm_medium=req.utm_medium,
                utm_campaign=req.utm_campaign,
                referrer=req.referrer or header_referrer,
                path=req.path or "/",
                user_agent=(user_agent or "")[:512],
                ip_hash=ip_hash,
            )
            db.add(visit_record)
            await db.commit()
        except Exception as exc:
            logger.warning("Database analytics recording fallback: %s", exc)
            await db.rollback()

    return TrackVisitResponse(
        recorded=True,
        source=classified_source,
        visitor_id=req.visitor_id,
        message="Visit recorded successfully",
    )


async def get_analytics_stats(db: AsyncSession | None = None) -> AnalyticsStatsResponse:
    """Aggregate total visits, Product Hunt visits, and live GitHub stars."""
    github_stats = await fetch_github_stars()

    # Base counts from in-memory / cache
    total_visits = _IN_MEMORY_STATS["total_visits"]
    unique_visitors = len(_IN_MEMORY_STATS["unique_visitors"])
    sources_breakdown = dict(_IN_MEMORY_STATS["sources"])
    recent_referrers = list(_IN_MEMORY_STATS["recent_events"][:15])

    # Check database for persistent lifetime totals
    if db:
        try:
            # Query count by source
            stmt = select(AnalyticsVisit.source, func.count(AnalyticsVisit.id)).group_by(AnalyticsVisit.source)
            result = await db.execute(stmt)
            db_counts = dict(result.all())

            if db_counts:
                db_total = sum(db_counts.values())
                # Merge with in-memory if db has higher count
                if db_total >= total_visits:
                    total_visits = db_total
                    sources_breakdown = db_counts

                # Unique visitors
                unique_stmt = select(func.count(func.distinct(AnalyticsVisit.visitor_id)))
                unique_res = await db.execute(unique_stmt)
                db_unique = unique_res.scalar() or 0
                if db_unique > unique_visitors:
                    unique_visitors = db_unique
        except Exception as exc:
            logger.debug("Database stats query fallback: %s", exc)

    ph_visits = sources_breakdown.get("producthunt", 0)
    gh_visits = sources_breakdown.get("github", 0)
    direct_visits = sources_breakdown.get("direct", 0)
    other_visits = max(0, total_visits - (ph_visits + gh_visits + direct_visits))

    ph_percentage = round((ph_visits / total_visits * 100), 1) if total_visits > 0 else 0.0

    return AnalyticsStatsResponse(
        total_visits=total_visits,
        unique_visitors=max(unique_visitors, 1 if total_visits > 0 else 0),
        product_hunt_visits=ph_visits,
        github_visits=gh_visits,
        direct_visits=direct_visits,
        other_visits=other_visits,
        product_hunt_percentage=ph_percentage,
        sources_breakdown=sources_breakdown,
        github_stats=github_stats,
        recent_referrers=recent_referrers,
    )
