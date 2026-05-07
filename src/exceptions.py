class DashboardError(Exception):
    def __init__(self, message="An error occurred in the GitHub Dashboard"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class APIError(DashboardError):
    def __init__(self, message="API request failed", status_code=None, url=None):
        self.status_code = status_code
        self.url = url
        super().__init__(message)

    def __str__(self):
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"status_code={self.status_code}")
        if self.url is not None:
            parts.append(f"url={self.url}")
        return " | ".join(parts)


class RateLimitError(DashboardError):
    def __init__(self, message="API rate limit exceeded", reset_at=None):
        self.reset_at = reset_at
        super().__init__(message)

    def __str__(self):
        parts = [self.message]
        if self.reset_at is not None:
            parts.append(f"reset_at={self.reset_at}")
        return " | ".join(parts)


class ValidationError(DashboardError):
    def __init__(self, message="Input validation failed"):
        super().__init__(message)

    def __str__(self):
        return self.message


class RenderError(DashboardError):
    def __init__(self, message="Rendering failed"):
        super().__init__(message)

    def __str__(self):
        return self.message
