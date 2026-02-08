#!/usr/bin/env python3
"""
Main entry point for Curio Decision Record MCP Server.

Run this script to start the MCP server using stdio transport.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for local imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import server (from same directory)
from server import app
from mcp.server.stdio import stdio_server


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
