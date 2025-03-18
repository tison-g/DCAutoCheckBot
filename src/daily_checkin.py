import asyncio
import csv
import random
from dataclasses import dataclass
from datetime import datetime
from loguru import logger
from curl_cffi.requests import AsyncSession
import os
import codecs
import platform
import time

@dataclass
class Account:
    token: str
    proxy: str
    index: int = 0

@dataclass
class CheckInConfig:
    index: int
    project: str
    guild_id: str
    channel_id: str
    message: str

async def send_checkin_message(
    account: Account,
    config: CheckInConfig,
    session: AsyncSession
) -> bool:
    try:
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "authorization": account.token,
            "content-type": "application/json",
            "origin": "https://discord.com",
            "referer": f"https://discord.com/channels/{config.guild_id}/{config.channel_id}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "Etc/GMT-2"
        }

        # 随机延迟 10-30 秒
        delay = random.uniform(10, 30)
        logger.info(f"Account {account.index} | Waiting {delay:.2f} seconds before sending message to [{config.index}] {config.project}")
        await asyncio.sleep(delay)

        json_data = {
            "content": config.message,
            "nonce": str(int(datetime.now().timestamp() * 1000 - 1420070400000) << 22),
            "tts": False,
            "flags": 0
        }

        response = await session.post(
            f"https://discord.com/api/v9/channels/{config.channel_id}/messages",
            headers=headers,
            json=json_data
        )

        if response.status_code == 200:
            logger.success(f"Account {account.index} | Check-in message sent successfully to [{config.index}] {config.project}")
            return True
        else:
            logger.error(f"Account {account.index} | Failed to send check-in to [{config.index}] {config.project}: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Account {account.index} | Error sending check-in to [{config.index}] {config.project}: {e}")
        return False

async def check_token(account: Account, session: AsyncSession) -> bool:
    try:
        response = await session.get(
            "https://discord.com/api/v9/users/@me",
            headers={"Authorization": account.token}
        )

        if response.status_code == 200:
            user_data = response.json()
            logger.info(f"Account {account.index} | Logged in as: {user_data.get('username', 'Unknown')}")
            return True
        return False
    except Exception as e:
        logger.error(f"Account {account.index} | Token check failed: {e}")
        return False

async def process_account(account: Account, configs: list[CheckInConfig]):
    """Process all configurations for a single account"""
    async with AsyncSession() as session:
        if account.proxy:
            session.proxies = {
                "http": account.proxy,
                "https": account.proxy
            }

        if await check_token(account, session):
            # 随机打乱配置顺序，避免固定模式
            random.shuffle(configs)

            for config in configs:
                # 发送消息
                await send_checkin_message(account, config, session)
        else:
            logger.warning(f"Account {account.index} | Invalid token")

def detect_file_encoding(file_path: str) -> str:
    """Detect the encoding of a file"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']

    for encoding in encodings:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as f:
                f.read()
                return encoding
        except UnicodeDecodeError:
            continue

    return 'utf-8'  # default to UTF-8 if no encoding works

def load_csv_file(file_path: str) -> list[dict]:
    """Load CSV file with automatic encoding detection"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []

    encoding = detect_file_encoding(file_path)
    logger.info(f"Detected encoding for {file_path}: {encoding}")

    try:
        with codecs.open(file_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {e}")
        return []

def load_accounts(csv_path: str) -> list[Account]:
    accounts = []
    rows = load_csv_file(csv_path)

    # 随机打乱账号顺序
    random.shuffle(rows)

    for idx, row in enumerate(rows, 1):
        try:
            accounts.append(Account(
                token=row['DISCORD_TOKEN'].strip(),
                proxy=row['PROXY'].strip() if row['PROXY'] else '',
                index=idx
            ))
        except Exception as e:
            logger.error(f"Error processing account row {idx}: {e}")
            continue

    return accounts

def load_configs(csv_path: str) -> list[CheckInConfig]:
    """Load configurations from CSV file"""
    configs = []
    rows = load_csv_file(csv_path)

    for row in rows:
        try:
            configs.append(CheckInConfig(
                index=int(row['INDEX']),
                project=row['PROJECT'].strip(),
                guild_id=row['GUILD_ID'].strip(),
                channel_id=row['CHANNEL_ID'].strip(),
                message=row['MESSAGE'].strip()
            ))
        except Exception as e:
            logger.error(f"Error processing config row: {e}")
            continue

    return configs

async def process_all_accounts(accounts: list[Account], configs: list[CheckInConfig]):
    """Process accounts one by one with delays"""
    for account in accounts:
        try:
            # 每个账号之间增加 15-45 秒的随机延迟
            if account.index > 1:  # 跳过第一个账号的延迟
                delay = random.uniform(15, 45)
                logger.info(f"Waiting {delay:.2f} seconds before processing next account...")
                await asyncio.sleep(delay)

            await process_account(account, configs)

        except Exception as e:
            logger.error(f"Error processing account {account.index}: {e}")
            continue

async def main():
    # Configure logging
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/checkin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger.add(log_file, rotation="1 day", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

    try:
        # Load accounts from CSV
        accounts_path = "config/accounts.csv"
        accounts = load_accounts(accounts_path)
        logger.info(f"Loaded {len(accounts)} accounts from CSV")

        if not accounts:
            logger.error("No valid accounts found in CSV file")
            return

        # Load configurations from config.csv
        config_path = "config/config.csv"
        configs = load_configs(config_path)
        logger.info(f"Loaded {len(configs)} configurations from CSV")

        if not configs:
            logger.error("No valid configurations found in CSV file")
            return

        # Log loaded configurations
        logger.info("Loaded projects:")
        for config in sorted(configs, key=lambda x: x.index):
            logger.info(f"[{config.index}] {config.project} - {config.message}")

        # 开始处理所有账号
        start_time = time.time()
        logger.info("Starting check-in process...")

        await process_all_accounts(accounts, configs)

        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"Check-in process completed in {total_time:.2f} seconds")

    except Exception as e:
        logger.error(f"Main process error: {e}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
