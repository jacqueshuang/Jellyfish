"""资产相关 CRUD：ActorImage / Scene / Prop / Costume 及其图片表。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.utils import apply_keyword_filter, apply_order, paginate
from app.dependencies import get_db
from app.models.studio import (
    ActorImage,
    ActorImageImage,
    Costume,
    CostumeImage,
    Prop,
    PropImage,
    Scene,
    SceneImage,
)
from app.schemas.common import ApiResponse, PaginatedData, paginated_response, success_response
from app.schemas.studio.assets import (
    ActorImageImageRead,
    ActorImageRead,
    AssetCreate,
    AssetImageCreate,
    AssetImageUpdate,
    AssetUpdate,
    CostumeImageRead,
    CostumeRead,
    PropImageRead,
    PropRead,
    SceneImageRead,
    SceneRead,
)

router = APIRouter()

ASSET_ORDER_FIELDS = {"name", "created_at", "updated_at"}
IMAGE_ORDER_FIELDS = {"id", "quality_level", "view_angle", "created_at", "updated_at"}


async def _ensure_single_primary(
    db: AsyncSession,
    *,
    table: type,
    parent_field: str,
    parent_id: str,
    keep_id: int | None,
) -> None:
    """同一父实体下只允许一张主图：把其他行 is_primary 置 false。"""
    parent_col = getattr(table, parent_field)
    stmt = update(table).where(parent_col == parent_id)
    if keep_id is not None:
        stmt = stmt.where(table.id != keep_id)
    stmt = stmt.values(is_primary=False)
    await db.execute(stmt)


def _asset_list_stmt(model: type, *, project_id: str | None, chapter_id: str | None):
    stmt = select(model)
    if project_id is not None:
        stmt = stmt.where(model.project_id == project_id)
    if chapter_id is not None:
        stmt = stmt.where(model.chapter_id == chapter_id)
    return stmt


# ---------- ActorImage ----------


@router.get(
    "/actor-images",
    response_model=ApiResponse[PaginatedData[ActorImageRead]],
    summary="演员形象列表（分页）",
)
async def list_actor_images(
    db: AsyncSession = Depends(get_db),
    project_id: str | None = Query(None),
    chapter_id: str | None = Query(None),
    q: str | None = Query(None, description="关键字，过滤 name/description"),
    order: str | None = Query(None),
    is_desc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[ActorImageRead]]:
    stmt = _asset_list_stmt(ActorImage, project_id=project_id, chapter_id=chapter_id)
    stmt = apply_keyword_filter(stmt, q=q, fields=[ActorImage.name, ActorImage.description])
    stmt = apply_order(stmt, model=ActorImage, order=order, is_desc=is_desc, allow_fields=ASSET_ORDER_FIELDS, default="created_at")
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response([ActorImageRead.model_validate(x) for x in items], page=page, page_size=page_size, total=total)


@router.post(
    "/actor-images",
    response_model=ApiResponse[ActorImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建演员形象",
)
async def create_actor_image(
    body: AssetCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ActorImageRead]:
    exists = await db.get(ActorImage, body.id)
    if exists is not None:
        raise HTTPException(status_code=400, detail=f"ActorImage with id={body.id} already exists")
    obj = ActorImage(**body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return success_response(ActorImageRead.model_validate(obj), code=201)


@router.get(
    "/actor-images/{actor_image_id}",
    response_model=ApiResponse[ActorImageRead],
    summary="获取演员形象",
)
async def get_actor_image(
    actor_image_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ActorImageRead]:
    obj = await db.get(ActorImage, actor_image_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="ActorImage not found")
    return success_response(ActorImageRead.model_validate(obj))


@router.patch(
    "/actor-images/{actor_image_id}",
    response_model=ApiResponse[ActorImageRead],
    summary="更新演员形象",
)
async def update_actor_image(
    actor_image_id: str,
    body: AssetUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ActorImageRead]:
    obj = await db.get(ActorImage, actor_image_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="ActorImage not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return success_response(ActorImageRead.model_validate(obj))


@router.delete(
    "/actor-images/{actor_image_id}",
    response_model=ApiResponse[None],
    summary="删除演员形象",
)
async def delete_actor_image(
    actor_image_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(ActorImage, actor_image_id)
    if obj is None:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)


# --- ActorImage images ---


@router.get(
    "/actor-images/{actor_image_id}/images",
    response_model=ApiResponse[PaginatedData[ActorImageImageRead]],
    summary="演员形象图片列表（分页）",
)
async def list_actor_image_images(
    actor_image_id: str,
    db: AsyncSession = Depends(get_db),
    order: str | None = Query(None),
    is_desc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[ActorImageImageRead]]:
    stmt = select(ActorImageImage).where(ActorImageImage.actor_image_id == actor_image_id)
    stmt = apply_order(stmt, model=ActorImageImage, order=order, is_desc=is_desc, allow_fields=IMAGE_ORDER_FIELDS, default="id")
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response([ActorImageImageRead.model_validate(x) for x in items], page=page, page_size=page_size, total=total)


@router.post(
    "/actor-images/{actor_image_id}/images",
    response_model=ApiResponse[ActorImageImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建演员形象图片",
)
async def create_actor_image_image(
    actor_image_id: str,
    body: AssetImageCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ActorImageImageRead]:
    parent = await db.get(ActorImage, actor_image_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="ActorImage not found")
    obj = ActorImageImage(actor_image_id=actor_image_id, **body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    if obj.is_primary:
        await _ensure_single_primary(db, table=ActorImageImage, parent_field="actor_image_id", parent_id=actor_image_id, keep_id=obj.id)
        await db.refresh(obj)
    return success_response(ActorImageImageRead.model_validate(obj), code=201)


@router.patch(
    "/actor-images/{actor_image_id}/images/{image_id}",
    response_model=ApiResponse[ActorImageImageRead],
    summary="更新演员形象图片",
)
async def update_actor_image_image(
    actor_image_id: str,
    image_id: int,
    body: AssetImageUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ActorImageImageRead]:
    obj = await db.get(ActorImageImage, image_id)
    if obj is None or obj.actor_image_id != actor_image_id:
        raise HTTPException(status_code=404, detail="ActorImageImage not found")
    update_data = body.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    if update_data.get("is_primary") is True:
        await _ensure_single_primary(db, table=ActorImageImage, parent_field="actor_image_id", parent_id=actor_image_id, keep_id=obj.id)
        await db.refresh(obj)
    return success_response(ActorImageImageRead.model_validate(obj))


@router.delete(
    "/actor-images/{actor_image_id}/images/{image_id}",
    response_model=ApiResponse[None],
    summary="删除演员形象图片",
)
async def delete_actor_image_image(
    actor_image_id: str,
    image_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(ActorImageImage, image_id)
    if obj is None or obj.actor_image_id != actor_image_id:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)


# ---------- Scene ----------


@router.get(
    "/scenes",
    response_model=ApiResponse[PaginatedData[SceneRead]],
    summary="场景列表（分页）",
)
async def list_scenes(
    db: AsyncSession = Depends(get_db),
    project_id: str | None = Query(None),
    chapter_id: str | None = Query(None),
    q: str | None = Query(None, description="关键字，过滤 name/description"),
    order: str | None = Query(None),
    is_desc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[SceneRead]]:
    stmt = _asset_list_stmt(Scene, project_id=project_id, chapter_id=chapter_id)
    stmt = apply_keyword_filter(stmt, q=q, fields=[Scene.name, Scene.description])
    stmt = apply_order(stmt, model=Scene, order=order, is_desc=is_desc, allow_fields=ASSET_ORDER_FIELDS, default="created_at")
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response([SceneRead.model_validate(x) for x in items], page=page, page_size=page_size, total=total)


@router.post(
    "/scenes",
    response_model=ApiResponse[SceneRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建场景",
)
async def create_scene(
    body: AssetCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SceneRead]:
    exists = await db.get(Scene, body.id)
    if exists is not None:
        raise HTTPException(status_code=400, detail=f"Scene with id={body.id} already exists")
    obj = Scene(**body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return success_response(SceneRead.model_validate(obj), code=201)


@router.get(
    "/scenes/{scene_id}",
    response_model=ApiResponse[SceneRead],
    summary="获取场景",
)
async def get_scene(
    scene_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SceneRead]:
    obj = await db.get(Scene, scene_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Scene not found")
    return success_response(SceneRead.model_validate(obj))


@router.patch(
    "/scenes/{scene_id}",
    response_model=ApiResponse[SceneRead],
    summary="更新场景",
)
async def update_scene(
    scene_id: str,
    body: AssetUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SceneRead]:
    obj = await db.get(Scene, scene_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Scene not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return success_response(SceneRead.model_validate(obj))


@router.delete(
    "/scenes/{scene_id}",
    response_model=ApiResponse[None],
    summary="删除场景",
)
async def delete_scene(
    scene_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(Scene, scene_id)
    if obj is None:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)


@router.get(
    "/scenes/{scene_id}/images",
    response_model=ApiResponse[PaginatedData[SceneImageRead]],
    summary="场景图片列表（分页）",
)
async def list_scene_images(
    scene_id: str,
    db: AsyncSession = Depends(get_db),
    order: str | None = Query(None),
    is_desc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[SceneImageRead]]:
    stmt = select(SceneImage).where(SceneImage.scene_id == scene_id)
    stmt = apply_order(stmt, model=SceneImage, order=order, is_desc=is_desc, allow_fields=IMAGE_ORDER_FIELDS, default="id")
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response([SceneImageRead.model_validate(x) for x in items], page=page, page_size=page_size, total=total)


@router.post(
    "/scenes/{scene_id}/images",
    response_model=ApiResponse[SceneImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建场景图片",
)
async def create_scene_image(
    scene_id: str,
    body: AssetImageCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SceneImageRead]:
    parent = await db.get(Scene, scene_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="Scene not found")
    obj = SceneImage(scene_id=scene_id, **body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    if obj.is_primary:
        await _ensure_single_primary(db, table=SceneImage, parent_field="scene_id", parent_id=scene_id, keep_id=obj.id)
        await db.refresh(obj)
    return success_response(SceneImageRead.model_validate(obj), code=201)


@router.patch(
    "/scenes/{scene_id}/images/{image_id}",
    response_model=ApiResponse[SceneImageRead],
    summary="更新场景图片",
)
async def update_scene_image(
    scene_id: str,
    image_id: int,
    body: AssetImageUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SceneImageRead]:
    obj = await db.get(SceneImage, image_id)
    if obj is None or obj.scene_id != scene_id:
        raise HTTPException(status_code=404, detail="SceneImage not found")
    update_data = body.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    if update_data.get("is_primary") is True:
        await _ensure_single_primary(db, table=SceneImage, parent_field="scene_id", parent_id=scene_id, keep_id=obj.id)
        await db.refresh(obj)
    return success_response(SceneImageRead.model_validate(obj))


@router.delete(
    "/scenes/{scene_id}/images/{image_id}",
    response_model=ApiResponse[None],
    summary="删除场景图片",
)
async def delete_scene_image(
    scene_id: str,
    image_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(SceneImage, image_id)
    if obj is None or obj.scene_id != scene_id:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)


# ---------- Prop ----------


@router.get(
    "/props",
    response_model=ApiResponse[PaginatedData[PropRead]],
    summary="道具列表（分页）",
)
async def list_props(
    db: AsyncSession = Depends(get_db),
    project_id: str | None = Query(None),
    chapter_id: str | None = Query(None),
    q: str | None = Query(None, description="关键字，过滤 name/description"),
    order: str | None = Query(None),
    is_desc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[PropRead]]:
    stmt = _asset_list_stmt(Prop, project_id=project_id, chapter_id=chapter_id)
    stmt = apply_keyword_filter(stmt, q=q, fields=[Prop.name, Prop.description])
    stmt = apply_order(stmt, model=Prop, order=order, is_desc=is_desc, allow_fields=ASSET_ORDER_FIELDS, default="created_at")
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response([PropRead.model_validate(x) for x in items], page=page, page_size=page_size, total=total)


@router.post(
    "/props",
    response_model=ApiResponse[PropRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建道具",
)
async def create_prop(
    body: AssetCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PropRead]:
    exists = await db.get(Prop, body.id)
    if exists is not None:
        raise HTTPException(status_code=400, detail=f"Prop with id={body.id} already exists")
    obj = Prop(**body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return success_response(PropRead.model_validate(obj), code=201)


@router.get(
    "/props/{prop_id}",
    response_model=ApiResponse[PropRead],
    summary="获取道具",
)
async def get_prop(
    prop_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PropRead]:
    obj = await db.get(Prop, prop_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Prop not found")
    return success_response(PropRead.model_validate(obj))


@router.patch(
    "/props/{prop_id}",
    response_model=ApiResponse[PropRead],
    summary="更新道具",
)
async def update_prop(
    prop_id: str,
    body: AssetUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PropRead]:
    obj = await db.get(Prop, prop_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Prop not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return success_response(PropRead.model_validate(obj))


@router.delete(
    "/props/{prop_id}",
    response_model=ApiResponse[None],
    summary="删除道具",
)
async def delete_prop(
    prop_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(Prop, prop_id)
    if obj is None:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)


@router.get(
    "/props/{prop_id}/images",
    response_model=ApiResponse[PaginatedData[PropImageRead]],
    summary="道具图片列表（分页）",
)
async def list_prop_images(
    prop_id: str,
    db: AsyncSession = Depends(get_db),
    order: str | None = Query(None),
    is_desc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[PropImageRead]]:
    stmt = select(PropImage).where(PropImage.prop_id == prop_id)
    stmt = apply_order(stmt, model=PropImage, order=order, is_desc=is_desc, allow_fields=IMAGE_ORDER_FIELDS, default="id")
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response([PropImageRead.model_validate(x) for x in items], page=page, page_size=page_size, total=total)


@router.post(
    "/props/{prop_id}/images",
    response_model=ApiResponse[PropImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建道具图片",
)
async def create_prop_image(
    prop_id: str,
    body: AssetImageCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PropImageRead]:
    parent = await db.get(Prop, prop_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="Prop not found")
    obj = PropImage(prop_id=prop_id, **body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    if obj.is_primary:
        await _ensure_single_primary(db, table=PropImage, parent_field="prop_id", parent_id=prop_id, keep_id=obj.id)
        await db.refresh(obj)
    return success_response(PropImageRead.model_validate(obj), code=201)


@router.patch(
    "/props/{prop_id}/images/{image_id}",
    response_model=ApiResponse[PropImageRead],
    summary="更新道具图片",
)
async def update_prop_image(
    prop_id: str,
    image_id: int,
    body: AssetImageUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PropImageRead]:
    obj = await db.get(PropImage, image_id)
    if obj is None or obj.prop_id != prop_id:
        raise HTTPException(status_code=404, detail="PropImage not found")
    update_data = body.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    if update_data.get("is_primary") is True:
        await _ensure_single_primary(db, table=PropImage, parent_field="prop_id", parent_id=prop_id, keep_id=obj.id)
        await db.refresh(obj)
    return success_response(PropImageRead.model_validate(obj))


@router.delete(
    "/props/{prop_id}/images/{image_id}",
    response_model=ApiResponse[None],
    summary="删除道具图片",
)
async def delete_prop_image(
    prop_id: str,
    image_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(PropImage, image_id)
    if obj is None or obj.prop_id != prop_id:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)


# ---------- Costume ----------


@router.get(
    "/costumes",
    response_model=ApiResponse[PaginatedData[CostumeRead]],
    summary="服装列表（分页）",
)
async def list_costumes(
    db: AsyncSession = Depends(get_db),
    project_id: str | None = Query(None),
    chapter_id: str | None = Query(None),
    q: str | None = Query(None, description="关键字，过滤 name/description"),
    order: str | None = Query(None),
    is_desc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[CostumeRead]]:
    stmt = _asset_list_stmt(Costume, project_id=project_id, chapter_id=chapter_id)
    stmt = apply_keyword_filter(stmt, q=q, fields=[Costume.name, Costume.description])
    stmt = apply_order(stmt, model=Costume, order=order, is_desc=is_desc, allow_fields=ASSET_ORDER_FIELDS, default="created_at")
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response([CostumeRead.model_validate(x) for x in items], page=page, page_size=page_size, total=total)


@router.post(
    "/costumes",
    response_model=ApiResponse[CostumeRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建服装",
)
async def create_costume(
    body: AssetCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CostumeRead]:
    exists = await db.get(Costume, body.id)
    if exists is not None:
        raise HTTPException(status_code=400, detail=f"Costume with id={body.id} already exists")
    obj = Costume(**body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return success_response(CostumeRead.model_validate(obj), code=201)


@router.get(
    "/costumes/{costume_id}",
    response_model=ApiResponse[CostumeRead],
    summary="获取服装",
)
async def get_costume(
    costume_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CostumeRead]:
    obj = await db.get(Costume, costume_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Costume not found")
    return success_response(CostumeRead.model_validate(obj))


@router.patch(
    "/costumes/{costume_id}",
    response_model=ApiResponse[CostumeRead],
    summary="更新服装",
)
async def update_costume(
    costume_id: str,
    body: AssetUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CostumeRead]:
    obj = await db.get(Costume, costume_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Costume not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return success_response(CostumeRead.model_validate(obj))


@router.delete(
    "/costumes/{costume_id}",
    response_model=ApiResponse[None],
    summary="删除服装",
)
async def delete_costume(
    costume_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(Costume, costume_id)
    if obj is None:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)


@router.get(
    "/costumes/{costume_id}/images",
    response_model=ApiResponse[PaginatedData[CostumeImageRead]],
    summary="服装图片列表（分页）",
)
async def list_costume_images(
    costume_id: str,
    db: AsyncSession = Depends(get_db),
    order: str | None = Query(None),
    is_desc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PaginatedData[CostumeImageRead]]:
    stmt = select(CostumeImage).where(CostumeImage.costume_id == costume_id)
    stmt = apply_order(stmt, model=CostumeImage, order=order, is_desc=is_desc, allow_fields=IMAGE_ORDER_FIELDS, default="id")
    items, total = await paginate(db, stmt=stmt, page=page, page_size=page_size)
    return paginated_response([CostumeImageRead.model_validate(x) for x in items], page=page, page_size=page_size, total=total)


@router.post(
    "/costumes/{costume_id}/images",
    response_model=ApiResponse[CostumeImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建服装图片",
)
async def create_costume_image(
    costume_id: str,
    body: AssetImageCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CostumeImageRead]:
    parent = await db.get(Costume, costume_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="Costume not found")
    obj = CostumeImage(costume_id=costume_id, **body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    if obj.is_primary:
        await _ensure_single_primary(db, table=CostumeImage, parent_field="costume_id", parent_id=costume_id, keep_id=obj.id)
        await db.refresh(obj)
    return success_response(CostumeImageRead.model_validate(obj), code=201)


@router.patch(
    "/costumes/{costume_id}/images/{image_id}",
    response_model=ApiResponse[CostumeImageRead],
    summary="更新服装图片",
)
async def update_costume_image(
    costume_id: str,
    image_id: int,
    body: AssetImageUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CostumeImageRead]:
    obj = await db.get(CostumeImage, image_id)
    if obj is None or obj.costume_id != costume_id:
        raise HTTPException(status_code=404, detail="CostumeImage not found")
    update_data = body.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    if update_data.get("is_primary") is True:
        await _ensure_single_primary(db, table=CostumeImage, parent_field="costume_id", parent_id=costume_id, keep_id=obj.id)
        await db.refresh(obj)
    return success_response(CostumeImageRead.model_validate(obj))


@router.delete(
    "/costumes/{costume_id}/images/{image_id}",
    response_model=ApiResponse[None],
    summary="删除服装图片",
)
async def delete_costume_image(
    costume_id: str,
    image_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    obj = await db.get(CostumeImage, image_id)
    if obj is None or obj.costume_id != costume_id:
        return success_response(None)
    await db.delete(obj)
    await db.flush()
    return success_response(None)

