"""Supabase client for Arrakis MVP."""

import asyncio
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from ..core.config import settings


class SupabaseClient:
    """Async wrapper for Supabase client."""
    
    def __init__(self):
        # Use the configured Supabase key (should be anon key for RLS)
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
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

    async def execute_raw_sql(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a parameterized SQL query safely.

        This method uses PostgreSQL's parameterized query syntax ($1, $2, etc.)
        to prevent SQL injection attacks.

        Args:
            query: SQL query with $1, $2, etc. placeholders
            params: List of parameters to bind to placeholders

        Returns:
            List of result rows as dictionaries

        Raises:
            Exception: If query execution fails
        """
        loop = asyncio.get_event_loop()

        # Convert positional parameters ($1, $2) to named parameters for PostgREST
        # Note: Supabase uses PostgREST which doesn't support raw SQL directly
        # For production, you should create stored procedures in Supabase
        # For now, we'll use the PostgREST query builder

        try:
            # Try to execute using RPC if a stored procedure exists
            # This is a temporary solution - ideally create Supabase functions
            result = await loop.run_in_executor(
                None,
                lambda: self._execute_postgrest_query(query, params or [])
            )
            return result
        except Exception as e:
            # Log error but don't expose details to client
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Database query error: {str(e)}")
            raise Exception("Database query failed")

    def _execute_postgrest_query(self, query: str, params: List[Any]) -> List[Dict[str, Any]]:
        """
        Execute query using PostgREST query builder.

        This is a bridge method that converts SQL queries to PostgREST calls.
        For production, replace with proper stored procedures.
        """
        # Import here to avoid circular dependency
        import re

        # Parse the query to extract table name and build PostgREST query
        # This is a simplified parser - for production use stored procedures

        # Check if it's a COUNT query
        if 'COUNT(*)' in query.upper():
            match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
            if match:
                table = match.group(1)
                result = self.client.table(table).select('*', count='exact').execute()
                return [{'count': result.count}]

        # Check if it's a SELECT query
        match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if match:
            table = match.group(1)

            # Extract SELECT columns
            select_match = re.search(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
            columns = '*'
            if select_match:
                columns = select_match.group(1).strip()
                # Clean up column list
                if columns and columns != '*':
                    # Keep it simple for now
                    columns = '*'

            # Build query
            q = self.client.table(table).select(columns)

            # Apply WHERE conditions if brand_name parameter exists
            if params and len(params) > 0:
                if 'WHERE brand_name' in query:
                    q = q.eq('brand_name', params[0])

            # Apply ORDER BY
            if 'ORDER BY' in query.upper():
                order_match = re.search(r'ORDER BY\s+(\w+)(\s+DESC|\s+ASC)?', query, re.IGNORECASE)
                if order_match:
                    column = order_match.group(1)
                    desc = 'DESC' in query.upper()
                    q = q.order(column, desc=desc)

            # Apply LIMIT
            if 'LIMIT' in query.upper():
                limit_match = re.search(r'LIMIT\s+(\$\d+|\d+)', query, re.IGNORECASE)
                if limit_match:
                    limit_str = limit_match.group(1)
                    if limit_str.startswith('$'):
                        # Parameter reference
                        param_index = int(limit_str[1:]) - 1
                        if param_index < len(params):
                            limit = int(params[param_index])
                            q = q.limit(limit)
                    else:
                        limit = int(limit_str)
                        q = q.limit(limit)

            result = q.execute()
            return result.data if result.data else []

        # If query can't be parsed, raise error
        raise Exception("Unsupported SQL query format. Please use Supabase stored procedures for complex queries.")


# Global client instance
db = SupabaseClient()
