import time
import asyncio
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from models.medalist import MedalistModel
import motor.motor_asyncio
import pandas as pd
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path="../.env")

class EventHandler(FileSystemEventHandler):
    def __init__(self, workers: int):
        client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URL"))
        db = client.examdb
        self.medalists_collection = db.get_collection("medalists_collection")

        self.executor = ThreadPoolExecutor(max_workers=workers)
        self.medal_type = {1: "G", 2: "S", 3: "C"}

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.event_type == "created" and "archive" not in event.src_path:
            logger.info(f"File created: {event.src_path}")
            self.executor.submit(self.runAsyncTask, event.src_path)

    def waitFile(self, file_path: str, max_attempts: int = 10, delay: int = 1) -> bool:
        attempts = 0
        while attempts < max_attempts:
            try:
                with open(file_path, "r"):
                    return True
            except IOError:
                attempts += 1
                time.sleep(delay)
        logger.warning(f"File not accessible after {max_attempts} attempts")
        return False

    def runAsyncTask(self, file_path: str) -> None:
        asyncio.run(self.processFile(file_path))

    async def processFile(self, file_path: str) -> None:
        if not self.waitFile(file_path=file_path):
            logger.error("File not accessible")
            return
        try:
            logger.info("Reading CSV and saving to MongoDB")
            df = pd.read_csv(file_path)

            medalists = []
            for _, row in df.iterrows():
                try:
                    medalist = MedalistModel(
                        discipline=row["discipline"],
                        event=row["event"],
                        event_date=row["medal_date"],
                        name=row["name"],
                        medal_type=row["medal_type"],
                        gender=row["gender"],
                        country=row["country"],
                        country_code=row["country_code"],
                        nationality=row["nationality"],
                        medal_code=self.medal_type.get(row["medal_code"], "Unknown"),
                        medal_date=row["medal_date"],
                    ).model_dump(by_alias=True)

                    existing = await self.medalists_collection.find_one(medalist)
                    if existing:
                        logger.info("Medalist already saved")
                        continue

                    medalists.append(medalist)
                except Exception as e:
                    logger.error(f"Error processing row: {e}")

            if medalists:
                await self.medalists_collection.insert_many(medalists)
                logger.info(f"Inserted {len(medalists)} records into MongoDB")
            else:
                logger.info("No valid records to insert")

            archive_path = os.path.join(os.path.dirname(file_path), "archive")
            if not os.path.exists(archive_path):
                os.makedirs(archive_path)
            os.rename(file_path, os.path.join(archive_path, os.path.basename(file_path)))
            logger.info(f"Moved file to archive: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")


async def startObserver(workers: int):
    event_handler = EventHandler(workers)
    observer = Observer()
    observer.schedule(event_handler, "../storage/app/medalists", recursive=True)
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=5, help="Number of workers")
    args = parser.parse_args()
    try:
        logger.info(f"Oberserver starting...")
        asyncio.run(startObserver(args.workers))
    except KeyboardInterrupt:
        logger.info(f"Exiting...")
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
