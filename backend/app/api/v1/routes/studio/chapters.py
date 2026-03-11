"""Chapter CRUD（从 projects.py 拆分）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import apply_keyword_filter, apply_order, paginate
from app.dependencies import get_db
from app.models.studio import Chapter, Project
from app.schemas.common import ApiResponse, PaginatedData, paginated_response, success_response
from app.schemas.studio.projects import ChapterCreate, ChapterRead, ChapterUpdate

router = APIRouter()

CHAPTER_ORDER_FIELDS = {"index", "title", "created_at", "updated_at", "storyboard_count", "status"}


@router.get(
    "",
    response_model=ApiResponse[PaginatedData[ChapterRead]],
    summary="章节列表（分页）",
)
async def list_chapters(
    db: AsyncSession = Depends(get_db),
    project_id: str | None = Query(None, description="按项目过滤"),
    q: str | None = Query(None, description="关键字，过滤 title/summary"),
    order: str | None = Query(None, description="排序字段"),
    is_desc: bool = Query(False, description="是否倒序"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[ChapterRead]]:
    stmt = select(Chapter)
    if project_id:
        stmt = stmt.where(Chapter.project_id == project_id)
    stmt = apply_keyword_filter(stmt, q=q, fields=[Chapter.title, Chapter.summary])
    stmt = apply_order(
        stmt,
        model=Chapter,
        order=order,
        is_desc=is_desc,
        allow_fields=CHAPTER_ORDER_FIELDS,
        default="index",
    )
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response(
        [ChapterRead.model_validate(x) for x in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post(
    "",
    response_model=ApiResponse[ChapterRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建章节",
)
async def create_chapter(
    body: ChapterCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ChapterRead]:
    exists = await db.get(Chapter, body.id)
    if exists is not None:
        raise HTTPException(status_code=400, detail=f"Chapter with id={body.id} already exists")
    project = await db.get(Project, body.project_id)
    if project is None:
        raise HTTPException(status_code=400, detail="Project not found")
    obj = Chapter(**body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return success_response(ChapterRead.model_validate(obj), code=201)


@router.get(
    "/{chapter_id}",
    response_model=ApiResponse[ChapterRead],
    summary="获取章节",
)
async def get_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ChapterRead]:
    obj = await db.get(Chapter, chapter_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return success_response(ChapterRead.model_validate(obj))


@router.patch(
    "/{chapter_id}",
    response_model=ApiResponse[ChapterRead],
    summary="更新章节",
)
async def update_chapter(
    chapter_id: str,
    body: ChapterUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ChapterRead]:
    obj = await db.get(Chapter, chapter_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    update = body.model_dump(exclude_unset=True)
    if "project_id" in update:
        project = await db.get(Project, update["project_id"])
        if project is None:
            raise HTTPException(status_code=400, detail="Project not found")
    for k, v in update.items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return success_response(ChapterRead.model_validate(obj))


@router.delete(
    "/{chapter_id}",
    response_model=ApiResponse[None],
    summary="删除章节",
)
async def delete_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(Chapter, chapter_id)
    if obj is None:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)

