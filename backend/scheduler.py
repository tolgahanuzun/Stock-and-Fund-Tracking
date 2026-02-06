from apscheduler.schedulers.background import BackgroundScheduler
from backend.services.fetcher import fetch_fund_prices
from backend.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def update_prices_job():
    logger.info("Scheduled job started: Price Update")
    db = SessionLocal()
    try:
        fetch_fund_prices(db)
    finally:
        db.close()
    logger.info("Scheduled job finished.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every day at 20:00 (TEFAS is usually updated in the evening)
    scheduler.add_job(update_prices_job, 'cron',  hour=10, minute=0)
    # Run once on startup (for testing)
    # scheduler.add_job(update_prices_job, 'date', run_date=datetime.now() + timedelta(seconds=10)) 
    scheduler.start()
    logger.info("Scheduler started.")
