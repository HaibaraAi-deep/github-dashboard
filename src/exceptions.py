class DashboardError(Exception):
    def __init__(self, message: str = "An error occurred in the GitHub Dashboard") -> None:
        self.message: str = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class APIError(DashboardError):
    def __init__(self, message: str = "API request failed", status_code: int | None = None, url: str | None = None) -> None:
        self.status_code: int | None = status_code
        self.url: str | None = url
        super().__init__(message)

    def __str__(self) -> str:
        parts: list[str] = [self.message]
        if self.status_code is not None:
            parts.append(f"status_code={self.status_code}")
        if self.url is not None:
            parts.append(f"url={self.url}")
        return " | ".join(parts)


class RateLimitError(DashboardError):
    def __init__(self, message: str = "API rate limit exceeded", reset_at: str | None = None) -> None:
        self.reset_at: str | None = reset_at
        super().__init__(message)

    def __str__(self) -> str:
        parts: list[str] = [self.message]
        if self.reset_at is not None:
            parts.append(f"reset_at={self.reset_at}")
        return " | ".join(parts)


class ValidationError(DashboardError):
    def __init__(self, message: str = "Input validation failed") -> None:
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class RenderError(DashboardError):
    def __init__(self, message: str = "Rendering failed") -> None:
        super().__init__(message)

    def __str__(self) -> str:
        return self.message
