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

    with open('oge_contexts.json', 'r') as fr:
        contexts = json.load(fr)  

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
                    for context in contexts:                   
                        source_id = context['fipi_id']
                        name = context['name'].replace("'", "''")
                        content = '\n'.join(context['content']).replace("'", "''")

                        query = f"""
                        INSERT INTO contexts (name, content, source_id)
                        VALUES (                            
                            '{name}',
                            '{content}',
                            '{source_id}'
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



    with open('fipi_probs_may_2026.json', 'r') as fr:
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
                        context_id = problem.get('context_id')
                        url = problem['url']
                        text = [problem['text']]                       
                        position = problem.get('position')
                        if type(position)==list:
                            position = 1
                        exam_type = problem.get('exam_type', 'ege')

                        await cursor.execute(
                            """
                            INSERT INTO problems 
                                (topics, type, url, text, position, source_id, context_id, exam_type, source)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (topics, prob_type, url, text, position, source_id, context_id, exam_type, 'fipi')
                        )                   
                        
                        logger.info(f"Problem {source_id} inserted")
    except Error as db_error:
        logger.exception("Database-specific error: %s", db_error)
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        if connection:
            await connection.close()
            logger.info("Connection to Postgres closed")


    with open('oge_onmay_2026.json', 'r') as fr:
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
                        context_id = problem.get('context_id')
                        url = problem['url']
                        text = problem['text']                        
                        position = problem.get('position')
                        if type(position)==list:
                            position = 1
                        exam_type = problem.get('exam_type', 'oge')

                        await cursor.execute(
                            """
                            INSERT INTO problems 
                                (topics, type, url, text, position, source_id, context_id, exam_type, source)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (topics, prob_type, url, text, position, source_id, context_id, exam_type, 'fipi')
                        )                       
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