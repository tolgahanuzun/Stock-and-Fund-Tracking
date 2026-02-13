from tefas import Crawler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import cast, Date, func, select, desc
from backend.models import Asset, PriceHistory, AssetType
from datetime import datetime, date, timedelta, time
import logging
import requests
from bs4 import BeautifulSoup
import time
import random

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_fund_prices(db: AsyncSession):
    """
    Fetches latest prices for all funds in the database from TEFAS web page HTML and saves them.
    Iterates through all tracked funds and scrapes the price individually.
    Implements ordering by last update time (oldest first) and retry mechanism.
    """
    
    # 1. Get all assets of type FUND, ordered by last price update date ascending (nulls first)
    # We want funds that haven't been updated recently to be processed first.
    
    # Subquery to find the max date for each asset
    subquery = (
        select(PriceHistory.asset_id, func.max(PriceHistory.date).label("last_update"))
        .group_by(PriceHistory.asset_id)
        .subquery()
    )

    # Main query joining Asset with the subquery
    query = (
        select(Asset, subquery.c.last_update)
        .outerjoin(subquery, Asset.id == subquery.c.asset_id)
        .filter(Asset.type == AssetType.FUND.value)
        .order_by(subquery.c.last_update.asc().nullsfirst())
    )
    
    result = await db.execute(query)
    funds_data = result.all()
    
    if not funds_data:
        logger.info("No funds found to track.")
        return

    today = date.today()
    one_hour_ago = datetime.now() - timedelta(hours=1)
    new_records_count = 0

    # Initialize Session with browser-like headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:148.0) Gecko/20100101 Firefox/148.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    })

    # Initial request to main page to get cookies/session tokens
    try:
        logger.info("Initializing TEFAS session...")
        session.get("https://www.tefas.gov.tr/Default.aspx", timeout=10)
        time.sleep(1) # Wait a bit after initial connection
    except Exception as e:
        logger.warning(f"Initial session setup failed, continuing might fail: {e}")

    for row in funds_data:
        fund = row[0]
        last_update = row[1]
        
        # Check if updated in last 1 hour
        if last_update:
            # last_update might be datetime or string depending on DB driver
            if isinstance(last_update, str):
                 try:
                     last_update_dt = datetime.fromisoformat(last_update)
                 except:
                     last_update_dt = None
            else:
                 last_update_dt = last_update
                 
            if last_update_dt and last_update_dt > one_hour_ago:
                logger.info(f"Skipping {fund.code}, updated recently at {last_update_dt}")
                continue

        retry_count = 0
        max_retries = 10
        price = None
        
        while retry_count < max_retries:
            try:
                # Add random delay to avoid WAF blocking (increasing with retries)
                delay = random.uniform(0.5, 2.0) + (retry_count * 0.5)
                time.sleep(delay)
                
                # Fetch price from web using the shared session
                price = fetch_fund_price_from_web(fund.code, session)
                
                if price is not None:
                    break # Success
                
                # If price is None (e.g. CAPTCHA or parse error), retry
                retry_count += 1
                logger.warning(f"Attempt {retry_count}/{max_retries} failed for {fund.code}. Retrying...")
                
            except Exception as e:
                logger.error(f"Error processing fund {fund.code} (Attempt {retry_count + 1}): {e}")
                retry_count += 1
        
        if price is None:
            logger.error(f"Failed to fetch price for {fund.code} after {max_retries} attempts. Skipping.")
            continue

        if price == 0:
            logger.warning(f"Fetched price is 0 for {fund.code}. Skipping update.")
            continue

        try:
            # Check existence
            existing_query = select(PriceHistory).filter(
                PriceHistory.asset_id == fund.id,
                cast(PriceHistory.date, Date) == today
            )
            existing_result = await db.execute(existing_query)
            existing_record = existing_result.scalars().first()
            
            if existing_record:
                # Update existing record if needed
                if existing_record.price != price:
                    existing_record.price = price
                    existing_record.date = datetime.now()
                    logger.info(f"Updated price for {fund.code}: {price}")
            else:
                # Create new record
                new_record = PriceHistory(
                    asset_id=fund.id,
                    date=datetime.now(),
                    price=price
                )
                db.add(new_record)
                new_records_count += 1
                logger.info(f"New price for {fund.code}: {price}")
        except Exception as e:
             logger.error(f"Database error for {fund.code}: {e}")

    try:
        await db.commit()
        if new_records_count > 0:
            logger.info(f"Successfully added {new_records_count} new price records.")
    except Exception as e:
        logger.error(f"Database commit error: {e}")
        await db.rollback()

def fetch_fund_price_from_web(fund_code: str, session: requests.Session = None) -> float | None:
    """
    Fetches the latest price of a specific fund directly from TEFAS web page HTML.
    Target URL: https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fund_code}
    Uses a requests.Session if provided to maintain cookies.
    """
    url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fund_code.upper()}"
    
    try:
        # Use provided session or create a new temporary one
        if session:
            req_obj = session
        else:
            req_obj = requests
            # If creating new request without session, at least add User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:148.0) Gecko/20100101 Firefox/148.0'
            }
        
        # If using session, headers are already set in session
        if session:
            response = req_obj.get(url, timeout=10)
        else:
            response = req_obj.get(url, headers=headers, timeout=10)
            
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for CAPTCHA/WAF page by looking for specific elements or title
        if "captcha" in response.text.lower() or "support id" in response.text.lower():
            logger.warning(f"CAPTCHA/WAF detected for {fund_code}")
            return None

        # Find top-list ul
        top_list = soup.find('ul', class_='top-list')
        if not top_list:
            # logger.warning(f"Could not find .top-list for fund {fund_code}")
            # Silently fail or log debug to avoid spamming logs if WAF blocks structure
            return None
            
        # Get first li element which usually contains the Last Price
        first_li = top_list.find('li')
        if not first_li:
            return None
            
        # Find the span inside the li that contains the value
        span = first_li.find('span')
        if not span:
            return None
            
        price_text = span.get_text(strip=True)
        # Format: 5,348167 -> 5.348167
        clean_price = price_text.replace('.', '').replace(',', '.')
        
        return float(clean_price)

    except Exception as e:
        logger.error(f"Error fetching price for {fund_code} from web: {e}")
        return None
