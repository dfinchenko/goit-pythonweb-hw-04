import asyncio
import aiofiles
import shutil
import os
import logging
from pathlib import Path
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("file_sorter.log"), logging.StreamHandler()]
)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Asynchronous file sorter by extension")
    parser.add_argument("source", type=str, help="Path to the source folder")
    parser.add_argument("output", type=str, help="Path to the output folder")
    return parser.parse_args()

async def copy_file(file_path: Path, output_folder: Path):
    try:
        extension = file_path.suffix[1:] if file_path.suffix else "no_extension"
        target_folder = output_folder / extension
        target_folder.mkdir(parents=True, exist_ok=True)

        target_file = target_folder / file_path.name
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.copy, file_path, target_file)
        logging.info(f"File {file_path} copied to {target_file}")
    except Exception as e:
        logging.error(f"Error copying file {file_path}: {e}")

async def read_folder(source_folder: Path, output_folder: Path):
    tasks = []
    files = await asyncio.to_thread(list, source_folder.rglob("*"))
    for file_path in files:
        if file_path.is_file():
            tasks.append(copy_file(file_path, output_folder))
    await asyncio.gather(*tasks)

async def main():
    args = parse_arguments()
    source_folder = Path(args.source)
    output_folder = Path(args.output)

    if not source_folder.is_dir():
        logging.error("The source folder does not exist or is not a directory.")
        return
    output_folder.mkdir(parents=True, exist_ok=True)

    logging.info(f"Starting to sort files from {source_folder} to {output_folder}")
    await read_folder(source_folder, output_folder)
    logging.info("File sorting completed.")

if __name__ == "__main__":
    asyncio.run(main())
