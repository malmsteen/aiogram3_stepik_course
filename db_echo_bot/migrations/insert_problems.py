import json
import asyncio
import logging
import os
import sys

from app.infrastructure.database.connection import get_pg_connection
from config.config import Config, load_config
from psycopg import AsyncConnection, Error

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format,
)

logger = logging.getLogger(__name__)

if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    connection: AsyncConnection | None = None

    try:
        connection = await get_pg_connection(
            db_name=config.db.name,
            host=config.db.host,
            port=config.db.port,
            user=config.db.user,
            password=config.db.password,
        )
        async with connection:
            async with connection.transaction():
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS problems(
                                id SERIAL PRIMARY KEY,
                                topics TEXT[],
                                type VARCHAR(20),
                                source_id VARCHAR(10),
                                source VARCHAR(20) DEFAULT 'fipi',
                                img TEXT,
                                url TEXT,
                                text TEXT NOT NULL,
                                position INTEGER
                            ); 
                        """
                    )
                logger.info("Table `problems` was successfully created")
    except Error as db_error:
        logger.exception("Database-specific error: %s", db_error)
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        if connection:
            await connection.close()
            logger.info("Connection to Postgres closed")




    with open('fipi_probs_last_w_pos.json', 'r') as fr:
        problems = json.load(fr)

    try:
        connection = await get_pg_connection(
            db_name=config.db.name,
            host=config.db.host,
            port=config.db.port,
            user=config.db.user,
            password=config.db.password,
        )
        async with connection:
            async with connection.transaction():
                async with connection.cursor() as cursor:
                    for problem in problems:
                        topics = problem['topics']
                        prob_type = problem['type']
                        source_id = problem['id']    
                        img = problem['img']    
                        url = problem['url']
                        text = problem['text']
                        position = problem['position']
                        # print(problem)
                        query = f"""
                        INSERT INTO problems (topics, type, img, url, text, position, source_id, source) 
                        VALUES (
                            ARRAY[{','.join(f"'{topic.replace("'", "''")}'" for topic in topics)}],
                            '{prob_type}',                                      
                            {f"'{img}'" if img else 'NULL'}, 
                            {f"'{url}'"}, 
                            '{text.replace("'", "''")}', 
                            {position},
                            '{source_id}',   
                            'fp' 
                        );
                        """
                        
                        await cursor.execute(query=query)
                        logger.info(f"Problem {source_id} inserted")
    except Error as db_error:
        logger.exception("Database-specific error: %s", db_error)
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        if connection:
            await connection.close()
            logger.info("Connection to Postgres closed")


asyncio.run(main())