"""Supabase client for Arrakis MVP."""

import asyncio
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from ..core.config import settings


class SupabaseClient:
    """Async wrapper for Supabase client."""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a raw SQL query."""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None, 
                lambda: self.client.rpc('exec_sql', {'query': query, 'params': params or {}})
            )
            return result.data if result.data else []
        except Exception as e:
            # Fallback to direct client call for simple queries
            try:
                result = await loop.run_in_executor(
                    None,
                    lambda: self.client.table('brands').select('*').execute()
                )
                return result.data if result.data else []
            except Exception as fallback_error:
                raise Exception(f"Database query failed: {e}, fallback failed: {fallback_error}")
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into a table."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.client.table(table).insert(data).execute()
        )
        return result.data[0] if result.data else {}
    
    async def select(self, table: str, **filters) -> List[Dict[str, Any]]:
        """Select data from a table with filters."""
        loop = asyncio.get_event_loop()
        query = self.client.table(table).select('*')
        
        # Apply filters
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)
        
        result = await loop.run_in_executor(None, lambda: query.execute())
        return result.data if result.data else []
    
    async def update(self, table: str, data: Dict[str, Any], **filters) -> List[Dict[str, Any]]:
        """Update data in a table."""
        loop = asyncio.get_event_loop()
        query = self.client.table(table).update(data)
        
        # Apply filters
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)
        
        result = await loop.run_in_executor(None, lambda: query.execute())
        return result.data if result.data else []
    
    async def delete(self, table: str, **filters) -> List[Dict[str, Any]]:
        """Delete data from a table."""
        loop = asyncio.get_event_loop()
        query = self.client.table(table).delete()
        
        # Apply filters
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)
        
        result = await loop.run_in_executor(None, lambda: query.execute())
        return result.data if result.data else []
    
    async def rpc(self, func: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Call a stored procedure."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.client.rpc(func, params or {})
        )
        return result.data if result.data else None


# Global client instance
db = SupabaseClient()
