from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Asset, AssetType, PriceHistory
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import date, datetime

router = APIRouter(
    prefix="/assets",
    tags=["assets"]
)

class AssetBase(BaseModel):
    code: str
    name: str
    type: AssetType

    # Pydantic v2 validator (field_validator)
    # Gelen kod ne olursa olsun büyük harfe çevir
    @field_validator('code')
    @classmethod
    def upper_case_code(cls, v: str) -> str:
        return v.upper()

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    
    class Config:
        from_attributes = True # orm_mode for pydantic v2

class PricePoint(BaseModel):
    date: datetime # date -> datetime olarak değiştirildi
    price: float

class AssetDetailResponse(AssetResponse):
    history: List[PricePoint] = []

@router.get("/", response_model=List[AssetResponse])
def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assets = db.query(Asset).offset(skip).limit(limit).all()
    return assets

@router.get("/{asset_id}", response_model=AssetDetailResponse)
def read_asset_detail(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # History sorted by date
    history = db.query(PriceHistory).filter(PriceHistory.asset_id == asset_id).order_by(PriceHistory.date.asc()).all()
    
    return {
        "id": asset.id,
        "code": asset.code,
        "name": asset.name,
        "type": asset.type,
        "history": history
    }

@router.post("/", response_model=AssetResponse)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    # Kod zaten validator ile büyütüldü
    db_asset = db.query(Asset).filter(Asset.code == asset.code).first()
    if db_asset:
        raise HTTPException(status_code=400, detail="Asset already exists")
    
    new_asset = Asset(code=asset.code, name=asset.name, type=asset.type)
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset
