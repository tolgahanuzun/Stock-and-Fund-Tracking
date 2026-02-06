from tefas import Crawler
from sqlalchemy.orm import Session
from backend.models import Asset, PriceHistory, AssetType
from datetime import datetime, date, timedelta
import logging

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_fund_prices(db: Session):
    """
    Fetches latest prices for all funds in the database from TEFAS and saves them.
    Optimized to minimize DB queries.
    """
    tefas = Crawler()
    
    # 1. Get all assets of type FUND
    funds = db.query(Asset).filter(Asset.type == AssetType.FUND.value).all()
    
    if not funds:
        logger.info("No funds found to track.")
        return

    # Create a map of Code -> ID for quick lookup
    fund_map = {fund.code: fund.id for fund in funds}
    fund_codes = list(fund_map.keys())
    
    # 2. Fetch data from TEFAS (Last 3 days to be safe)
    start_dt = date.today() - timedelta(days=3)
    
    try:
        # Fetching bulk data (TEFAS crawler might not support filtering by code in fetch, so we fetch all or range)
        # Note: tefas-crawler fetches all funds if columns are not specified or specific call structure.
        # Assuming fetch gets everything for the date range.
        result = tefas.fetch(start=start_dt.strftime("%Y-%m-%d"), 
                             columns=["code", "date", "price"])
        
        if result is None or result.empty:
            logger.warning("Could not fetch data from TEFAS.")
            return

        # 3. Filter only our funds
        result = result[result['code'].isin(fund_codes)]
        
        if result.empty:
            logger.info("No data found for tracked funds in the last few days.")
            return

        # 4. Prepare data for bulk processing
        # We need to check which (asset_id, date) pairs already exist to avoid duplicates
        # Get all relevant dates from the result
        result_dates = result['date'].apply(lambda x: x.date() if hasattr(x, 'date') else x).unique()
        
        # Query existing records for these assets and dates
        existing_records = db.query(PriceHistory.asset_id, PriceHistory.date).filter(
            PriceHistory.asset_id.in_(fund_map.values()),
            PriceHistory.date.in_(result_dates)
        ).all()
        
        # Create a set of existing (asset_id, date) tuples
        existing_set = set(existing_records)
        
        new_records = []
        
        for index, row in result.iterrows():
            code = row['code']
            asset_id = fund_map.get(code)
            
            raw_date = row['date']
            price_date = raw_date.date() if hasattr(raw_date, 'date') else raw_date
            price_val = float(row['price'])
            
            if (asset_id, price_date) not in existing_set:
                new_records.append(PriceHistory(
                    asset_id=asset_id,
                    date=price_date,
                    price=price_val
                ))
                # Add to set to prevent duplicates within the same batch if any
                existing_set.add((asset_id, price_date))
        
        # 5. Bulk Insert
        if new_records:
            db.bulk_save_objects(new_records)
            db.commit()
            logger.info(f"Added {len(new_records)} new price records.")
        else:
            logger.info("No new price records to add.")
            
    except Exception as e:
        logger.error(f"Data fetch error: {e}")
        db.rollback()
