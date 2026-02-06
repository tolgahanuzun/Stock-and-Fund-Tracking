from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, tuple_
from backend.database import get_db
from backend.models import Portfolio, Asset, PriceHistory, User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"]
)

class PortfolioBase(BaseModel):
    asset_id: int
    quantity: float
    average_cost: float

class TransactionCreate(PortfolioBase):
    user_id: int = 1 # Default user

class PortfolioItemResponse(PortfolioBase):
    id: int
    asset_code: str
    asset_name: str
    current_price: float
    total_value: float
    profit_loss: float
    profit_loss_percent: float
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[PortfolioItemResponse])
def read_portfolio(user_id: int = 1, db: Session = Depends(get_db)):
    # 1. Fetch user portfolio
    items = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    
    if not items:
        return []

    # 2. Get all asset IDs in portfolio
    asset_ids = [item.asset_id for item in items]

    # 3. Batch Fetch Latest Prices (Optimized Query)
    # Subquery to find the max date for each asset
    subquery = db.query(
        PriceHistory.asset_id,
        func.max(PriceHistory.date).label('max_date')
    ).filter(PriceHistory.asset_id.in_(asset_ids)).group_by(PriceHistory.asset_id).subquery()

    # Join to get the prices
    latest_prices_query = db.query(PriceHistory).join(
        subquery,
        (PriceHistory.asset_id == subquery.c.asset_id) & 
        (PriceHistory.date == subquery.c.max_date)
    ).all()

    # Map prices for O(1) lookup
    price_map = {p.asset_id: p.price for p in latest_prices_query}
    
    result = []
    for item in items:
        # Asset info (Already loaded via relationship or join could be used, but lazy load is OK for small N)
        asset = item.asset
        
        # Get price from map
        current_price = price_map.get(asset.id, item.average_cost)
        
        total_value = item.quantity * current_price
        cost_basis = item.quantity * item.average_cost
        profit_loss = total_value - cost_basis
        profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        result.append(PortfolioItemResponse(
            id=item.id,
            asset_id=asset.id,
            quantity=item.quantity,
            average_cost=item.average_cost,
            asset_code=asset.code,
            asset_name=asset.name,
            current_price=current_price,
            total_value=total_value,
            profit_loss=profit_loss,
            profit_loss_percent=profit_loss_percent
        ))
        
    return result

@router.get("/asset/{asset_id}", response_model=PortfolioItemResponse)
def read_portfolio_asset(asset_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    # This endpoint is single item, so optimization is less critical but still good practice to use efficient queries.
    item = db.query(Portfolio).filter(Portfolio.user_id == user_id, Portfolio.asset_id == asset_id).first()
    
    # Check if user owns it or not
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
         raise HTTPException(status_code=404, detail="Asset not found")

    # Get latest price
    last_price_entry = db.query(PriceHistory)\
        .filter(PriceHistory.asset_id == asset.id)\
        .order_by(PriceHistory.date.desc())\
        .first()
    
    current_price = last_price_entry.price if last_price_entry else 0

    if not item:
        return PortfolioItemResponse(
            id=0,
            asset_id=asset.id,
            quantity=0,
            average_cost=0,
            asset_code=asset.code,
            asset_name=asset.name,
            current_price=current_price,
            total_value=0,
            profit_loss=0,
            profit_loss_percent=0
        )
    
    # Calculate for owned item
    total_value = item.quantity * current_price
    cost_basis = item.quantity * item.average_cost
    profit_loss = total_value - cost_basis
    profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
    
    return PortfolioItemResponse(
        id=item.id,
        asset_id=asset.id,
        quantity=item.quantity,
        average_cost=item.average_cost,
        asset_code=asset.code,
        asset_name=asset.name,
        current_price=current_price,
        total_value=total_value,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent
    )

@router.post("/transaction")
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    # Check if user exists, create if not (for convenience)
    user = db.query(User).filter(User.id == transaction.user_id).first()
    if not user:
        user = User(id=transaction.user_id, username="default", full_name="Default User")
        db.add(user)
        db.commit()
    
    # Check if asset exists in portfolio
    portfolio_item = db.query(Portfolio).filter(
        Portfolio.user_id == transaction.user_id,
        Portfolio.asset_id == transaction.asset_id
    ).first()
    
    if portfolio_item:
        # Calculate weighted average cost
        total_quantity = portfolio_item.quantity + transaction.quantity
        total_cost = (portfolio_item.quantity * portfolio_item.average_cost) + (transaction.quantity * transaction.average_cost)
        new_average_cost = total_cost / total_quantity if total_quantity > 0 else 0
        
        portfolio_item.quantity = total_quantity
        portfolio_item.average_cost = new_average_cost
    else:
        portfolio_item = Portfolio(
            user_id=transaction.user_id,
            asset_id=transaction.asset_id,
            quantity=transaction.quantity,
            average_cost=transaction.average_cost
        )
        db.add(portfolio_item)
    
    db.commit()
    return {"message": "Transaction successful"}
