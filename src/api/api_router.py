from fastapi import APIRouter

from ..api.v1.endpoints import courses, domains, modules, lessons, auth,segments

api_router = APIRouter()
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(segments.router, prefix="/segments", tags=["segments"])

api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(domains.router, prefix="/domain", tags=["domain"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])