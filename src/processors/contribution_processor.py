import logging
from collections import defaultdict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ContributionProcessor:
    def process(self, calendar_data: dict | None) -> dict:
        if not calendar_data:
            return {
                "total_contributions": 0,
                "weeks": [],
                "daily_stats": {},
                "streak": {"current": 0, "longest": 0},
                "averages": {"daily": 0, "weekly": 0, "monthly": 0},
                "weekday_stats": {},
            }

        weeks = calendar_data.get("weeks", [])
        total_contributions = calendar_data.get("totalContributions", 0)

        all_days = []
        for week in weeks:
            for day in week.get("contributionDays", []):
                all_days.append(day)

        streak = self._calculate_streak(all_days)
        averages = self._calculate_averages(all_days, total_contributions)
        weekday_stats = self._calculate_weekday_stats(all_days)

        monthly_stats = self._calculate_monthly_stats(all_days)
        weekly_stats = self._calculate_weekly_trend(weeks)

        return {
            "total_contributions": total_contributions,
            "weeks": weeks,
            "all_days": all_days,
            "streak": streak,
            "averages": averages,
            "weekday_stats": weekday_stats,
            "monthly_stats": monthly_stats,
            "weekly_trend": weekly_stats,
        }

    def _calculate_streak(self, all_days: list) -> dict:
        if not all_days:
            return {"current": 0, "longest": 0}

        sorted_days = sorted(all_days, key=lambda d: d.get("date", ""))

        current_streak = 0
        longest_streak = 0
        temp_streak = 0

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for i, day in enumerate(sorted_days):
            count = day.get("contributionCount", 0)
            if count > 0:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0

        current_streak = 0
        for day in reversed(sorted_days):
            if day.get("contributionCount", 0) > 0:
                current_streak += 1
            elif day.get("date", "") < today:
                break

        return {
            "current": current_streak,
            "longest": longest_streak,
        }

    def _calculate_averages(self, all_days: list, total_contributions: int) -> dict:
        if not all_days:
            return {"daily": 0, "weekly": 0, "monthly": 0}

        total_days = len(all_days)
        if total_days == 0:
            return {"daily": 0, "weekly": 0, "monthly": 0}

        daily = round(total_contributions / total_days, 1)
        weekly = round(total_contributions / (total_days / 7), 1) if total_days >= 7 else total_contributions
        monthly = round(total_contributions / (total_days / 30), 1) if total_days >= 30 else total_contributions

        return {
            "daily": daily,
            "weekly": weekly,
            "monthly": monthly,
        }

    def _calculate_weekday_stats(self, all_days: list) -> dict:
        weekday_counts = defaultdict(list)
        for day in all_days:
            weekday = day.get("weekday", 0)
            count = day.get("contributionCount", 0)
            weekday_counts[weekday].append(count)

        stats = {}
        weekday_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for wd, counts in weekday_counts.items():
            name = weekday_names[wd] if wd < len(weekday_names) else str(wd)
            stats[name] = {
                "total": sum(counts),
                "average": round(sum(counts) / len(counts), 1) if counts else 0,
                "max": max(counts) if counts else 0,
            }

        return stats

    def _calculate_monthly_stats(self, all_days: list) -> dict:
        monthly = defaultdict(int)
        for day in all_days:
            date_str = day.get("date", "")
            if date_str:
                month_key = date_str[:7]
                monthly[month_key] += day.get("contributionCount", 0)

        return dict(sorted(monthly.items()))

    def _calculate_weekly_trend(self, weeks: list) -> list:
        trend = []
        for week in weeks:
            total = sum(
                day.get("contributionCount", 0)
                for day in week.get("contributionDays", [])
            )
            first_day = ""
            days = week.get("contributionDays", [])
            if days:
                first_day = days[0].get("date", "")
            trend.append({
                "date": first_day,
                "count": total,
            })
        return trend
