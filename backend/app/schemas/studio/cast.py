"""演员/角色及关联表 schemas。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ActorBase(BaseModel):
    id: str = Field(..., description="演员 ID")
    project_id: str | None = Field(None, description="归属项目 ID（可空=全局演员）")
    name: str = Field(..., description="演员名称")
    description: str = Field("", description="演员描述/备注")
    thumbnail: str = Field("", description="演员头像/缩略图")
    tags: list[str] = Field(default_factory=list, description="标签")


class ActorCreate(ActorBase):
    pass


class ActorUpdate(BaseModel):
    project_id: str | None = None
    name: str | None = None
    description: str | None = None
    thumbnail: str | None = None
    tags: list[str] | None = None


class ActorRead(ActorBase):
    class Config:
        from_attributes = True


class CharacterBase(BaseModel):
    id: str = Field(..., description="角色 ID")
    project_id: str = Field(..., description="所属项目 ID")
    name: str = Field(..., description="角色名称")
    description: str = Field("", description="角色描述")
    actor_id: str | None = Field(None, description="演员 ID（可空）")
    costume_id: str | None = Field(None, description="服装 ID（可空）")


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    project_id: str | None = None
    name: str | None = None
    description: str | None = None
    actor_id: str | None = None
    costume_id: str | None = None


class CharacterRead(CharacterBase):
    class Config:
        from_attributes = True


class CharacterPropLinkBase(BaseModel):
    id: int = Field(..., description="关联行 ID")
    character_id: str = Field(..., description="角色 ID")
    prop_id: str = Field(..., description="道具 ID")
    index: int = Field(0, description="角色道具排序")
    note: str = Field("", description="备注")


class CharacterPropLinkCreate(BaseModel):
    character_id: str
    prop_id: str
    index: int = 0
    note: str = ""


class CharacterPropLinkUpdate(BaseModel):
    index: int | None = None
    note: str | None = None


class CharacterPropLinkRead(CharacterPropLinkBase):
    class Config:
        from_attributes = True


class ShotCharacterLinkBase(BaseModel):
    id: int = Field(..., description="关联行 ID")
    shot_id: str = Field(..., description="镜头 ID")
    character_id: str = Field(..., description="角色 ID")
    index: int = Field(0, description="镜头内角色排序")
    note: str = Field("", description="备注")


class ShotCharacterLinkCreate(BaseModel):
    shot_id: str
    character_id: str
    index: int = 0
    note: str = ""


class ShotCharacterLinkUpdate(BaseModel):
    index: int | None = None
    note: str | None = None


class ShotCharacterLinkRead(ShotCharacterLinkBase):
    class Config:
        from_attributes = True

