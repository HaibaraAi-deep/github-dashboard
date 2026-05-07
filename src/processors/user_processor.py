import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class UserProcessor:
    def process(self, user_data: dict | None) -> dict:
        if user_data is None:
            return {}

        created_at = user_data.get("created_at", "")
        account_age_days = 0
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                account_age_days = (now - created).days
            except (ValueError, TypeError):
                logger.warning(f"Failed to parse created_at: {created_at}")

        return {
            "login": user_data.get("login", ""),
            "name": user_data.get("name", "") or user_data.get("login", ""),
            "bio": user_data.get("bio", "") or "",
            "avatar_url": user_data.get("avatar_url", ""),
            "location": user_data.get("location", "") or "",
            "company": user_data.get("company", "") or "",
            "blog": user_data.get("blog", "") or "",
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "created_at": created_at,
            "account_age_days": account_age_days,
            "account_age_years": round(account_age_days / 365.25, 1),
        }
