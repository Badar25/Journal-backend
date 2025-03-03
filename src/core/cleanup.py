import asyncio
from datetime import datetime, timedelta
from ..services.qdrant_service import qdrant_service
from .logger import logger

async def cleanup_old_journals():
    while True:
        try:
            logger.info("Starting scheduled cleanup of old journal entries")
            
            # Calculate the timestamp for 8 days ago
            cutoff_date = datetime.now() - timedelta(days=8)
            cutoff_timestamp = cutoff_date.timestamp()
            
            # Delete journals older than 8 days
            filter = Filter(must=[
                FieldCondition(
                    key="createdAt",
                    range=Range(lt=cutoff_timestamp)
                )
            ])
            
            qdrant_service.client.delete(
                collection_name=qdrant_service.collection_name,
                points_selector=filter
            )
            
            logger.info("Completed cleanup of old journal entries")
            
            # Wait for 24 hours before next cleanup
            await asyncio.sleep(24 * 60 * 60)  # 24 hours in seconds
            
        except Exception as e:
            logger.error(f"Error during journal cleanup: {str(e)}")
            # Wait for 1 hour before retrying in case of error
            await asyncio.sleep(60 * 60)