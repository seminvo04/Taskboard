from fastapi import APIRouter
from app.api.v1.endpoints import auth, projects, tasks, ws

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(ws.router)
api_router.add_api_route(
    "/users/search",
    auth.search_users,
    methods=["GET"],
    response_model=list[auth.UserRead],
    tags=["users"],
)