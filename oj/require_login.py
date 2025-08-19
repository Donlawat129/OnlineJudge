from django.http import JsonResponse
import os
REQUIRE = os.environ.get("REQUIRE_LOGIN_FOR_PUBLIC", "1") == "1"
PROTECTED_PREFIXES = (
    "/api/announcement", "/api/announcements",
    "/api/problem", "/api/problems",
    "/api/submission", "/api/status",
    "/api/rank", "/api/acm-rank", "/api/oi-rank",
)
class RequireLoginForPublicAPIs:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        if REQUIRE:
            p = (request.path or "").rstrip("/")
            if any(p.startswith(x) for x in PROTECTED_PREFIXES):
                if not getattr(request, "user", None) or not request.user.is_authenticated:
                    return JsonResponse({"detail": "Authentication required"}, status=401)
        return self.get_response(request)
