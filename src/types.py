from typing import TypedDict, NotRequired


class UserInfo(TypedDict):
    login: str
    name: str
    bio: str
    avatar_url: str
    location: str
    company: str
    blog: str
    public_repos: int
    followers: int
    following: int
    created_at: str
    account_age_days: int
    account_age_years: float
    total_stars: NotRequired[int]


class RepoInfo(TypedDict):
    name: str
    full_name: str
    description: str
    language: str
    stars: int
    forks: int
    updated_at: str
    html_url: str


class RepoResult(TypedDict):
    total_repos: int
    total_stars: int
    total_forks: int
    repos_by_language: dict[str, int]
    top_by_stars: list[RepoInfo]
    top_by_forks: list[RepoInfo]
    all_repos: list[RepoInfo]


class LanguageInfo(TypedDict):
    name: str
    bytes: int
    percentage: float
    color: str


class LanguageResult(TypedDict):
    languages: list[LanguageInfo]
    total_bytes: int
    total_language_count: NotRequired[int]
    top_n: int


class StreakInfo(TypedDict):
    current: int
    longest: int


class AveragesInfo(TypedDict):
    daily: float
    weekly: float
    monthly: float


class WeekdayStat(TypedDict):
    total: int
    average: float
    max: int


class MonthlyStat(TypedDict):
    pass


class WeeklyTrendItem(TypedDict):
    date: str
    count: int


class ContributionResult(TypedDict):
    total_contributions: int
    weeks: list[dict]
    all_days: NotRequired[list[dict]]
    streak: StreakInfo
    averages: AveragesInfo
    weekday_stats: dict[str, WeekdayStat]
    monthly_stats: NotRequired[dict[str, int]]
    weekly_trend: NotRequired[list[WeeklyTrendItem]]
