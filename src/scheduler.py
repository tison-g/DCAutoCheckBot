import schedule
import time
import subprocess
import random
from datetime import datetime, timedelta
from loguru import logger
import os
import platform
import asyncio

def get_random_time(start_hour: int, end_hour: int) -> str:
    """Generate a random time between start_hour and end_hour"""
    random_hour = random.randint(start_hour, end_hour - 1)
    random_minute = random.randint(0, 59)
    return f"{random_hour:02d}:{random_minute:02d}"

def schedule_next_checkin(start_hour: int, end_hour: int) -> str:
    """Schedule next check-in for tomorrow at a random time"""
    tomorrow = datetime.now() + timedelta(days=1)
    random_time = get_random_time(start_hour, end_hour)
    next_run = tomorrow.strftime(f"%Y-%m-%d {random_time}")

    logger.info(f"Next check-in scheduled for: {next_run}")
    return next_run

def run_checkin():
    try:
        logger.info("Starting daily check-in process")
        script_path = os.path.join(os.path.dirname(__file__), "daily_checkin.py")
        subprocess.run(["python", script_path], check=True)
        logger.info("Daily check-in process completed")

        # Schedule next run after completion
        start_hour = 7  # 修改为当前小时
        end_hour = 22
        next_run = schedule_next_checkin(start_hour, end_hour)

        # Clear existing jobs and schedule new one
        schedule.clear()
        schedule.every().day.at(next_run.split()[1]).do(run_checkin)

    except Exception as e:
        logger.error(f"Failed to run check-in: {e}")

def main():
    # Configure logging
    os.makedirs("logs", exist_ok=True)
    logger.add("logs/scheduler.log", rotation="1 day")

    # 设置为当前时间后几分钟
    now = datetime.now()
    schedule_time = (now + timedelta(minutes=1)).strftime("%H:%M")

    # 立即安排任务在1分钟后执行
    logger.info(f"Scheduling first check-in for: {schedule_time}")
    schedule.every().day.at(schedule_time).do(run_checkin)

    logger.info("Scheduler started")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
