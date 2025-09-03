#!/usr/bin/env python3
"""
MCP Server for Gemini CLI Integration with Claude Code
Provides tools for consulting Gemini and managing the integration
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

# Import our Gemini integration
from gemini_integration import gemini

class GeminiMCPServer:
    def __init__(self, project_root: str = "."):
        self.server = Server("gemini-collaboration")
        self.project_root = Path(project_root).resolve()
        self.setup_tools()
        self.setup_resources()
    
    def setup_tools(self):
        """Register MCP tools for Gemini integration"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="consult_gemini",
                    description="Consult Gemini for a second opinion or additional perspective",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The question or topic to ask Gemini about"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context to provide to Gemini (optional)",
                                "default": ""
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="gemini_status",
                    description="Get current status and statistics of Gemini integration",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="toggle_gemini_auto_consult",
                    description="Toggle automatic Gemini consultation when uncertainty is detected",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "enabled": {
                                "type": "boolean",
                                "description": "Whether to enable or disable auto-consultation"
                            }
                        },
                        "required": ["enabled"]
                    }
                ),
                Tool(
                    name="update_gemini_config",
                    description="Update Gemini configuration parameters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "Gemini model to use (e.g., gemini-2.5-flash, gemini-2.5-pro)",
                                "enum": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
                            },
                            "rate_limit_delay": {
                                "type": "number",
                                "description": "Delay between calls in seconds",
                                "minimum": 0.5,
                                "maximum": 10.0
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout for Gemini calls in seconds",
                                "minimum": 10,
                                "maximum": 300
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            if name == "consult_gemini":
                return await self.handle_consult_gemini(arguments)
            elif name == "gemini_status":
                return await self.handle_gemini_status(arguments)
            elif name == "toggle_gemini_auto_consult":
                return await self.handle_toggle_auto_consult(arguments)
            elif name == "update_gemini_config":
                return await self.handle_update_config(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    def setup_resources(self):
        """Register MCP resources"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            return [
                Resource(
                    uri="file://gemini-config.json",
                    name="Gemini Configuration",
                    description="Current Gemini integration configuration",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            if uri == "file://gemini-config.json":
                config_path = self.project_root / "gemini-config.json"
                if config_path.exists():
                    return config_path.read_text(encoding='utf-8')
                else:
                    return json.dumps({
                        "model": "gemini-2.5-flash",
                        "timeout": 60,
                        "rate_limit_delay": 2.0,
                        "auto_consult": True,
                        "uncertainty_thresholds": {
                            "not_sure": True,
                            "uncertain": True,
                            "might_be": True,
                            "possibly": True,
                            "unclear": True
                        }
                    }, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def handle_consult_gemini(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle Gemini consultation request"""
        query = arguments.get("query", "")
        context = arguments.get("context", "")
        
        if not query.strip():
            return [TextContent(
                type="text",
                text="❌ Error: Query cannot be empty"
            )]
        
        try:
            result = await gemini.call_gemini(query, context)
            
            if result["success"]:
                response_text = f"""🤖 **Gemini {result['model']} Response** ({result['timestamp']})

{result['response']}

---
*This consultation was provided by Gemini to supplement Claude's analysis.*"""
                
                return [TextContent(type="text", text=response_text)]
            else:
                error_text = f"""❌ **Gemini Consultation Failed**

Error: {result['error']}
Model: {result['model']}
Time: {result['timestamp']}

Please check your Gemini CLI setup and API key configuration."""
                
                return [TextContent(type="text", text=error_text)]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Unexpected error during Gemini consultation: {str(e)}"
            )]
    
    async def handle_gemini_status(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle status request"""
        try:
            status = gemini.get_status()
            
            status_text = f"""📊 **Gemini Integration Status**

**Configuration:**
- Model: {status['model']}
- Auto-consult: {'✅ Enabled' if status['auto_consult'] else '❌ Disabled'}
- Rate limit delay: {status['rate_limit_delay']}s
- Config file: {status['config_file']}

**Session Statistics:**
- Total calls: {status['session_stats']['total_calls']}
- Successful: {status['session_stats']['successful_calls']}
- Failed: {status['session_stats']['failed_calls']}
- Last consult: {status['session_stats']['last_consult_time'] or 'Never'}

**Available Commands:**
- `/consult_gemini` - Get Gemini's perspective
- `/toggle_gemini_auto_consult` - Toggle auto-consultation
- `/update_gemini_config` - Update configuration"""
            
            return [TextContent(type="text", text=status_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error getting status: {str(e)}"
            )]
    
    async def handle_toggle_auto_consult(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle auto-consult toggle"""
        try:
            enabled = arguments.get("enabled", True)
            gemini.update_config(auto_consult=enabled)
            
            status = "enabled" if enabled else "disabled"
            return [TextContent(
                type="text",
                text=f"✅ Auto-consultation {status}. Gemini will {'now' if enabled else 'no longer'} be automatically consulted when uncertainty patterns are detected."
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error toggling auto-consult: {str(e)}"
            )]
    
    async def handle_update_config(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle configuration update"""
        try:
            # Filter out None values and invalid keys
            updates = {k: v for k, v in arguments.items() if v is not None}
            
            if not updates:
                return [TextContent(
                    type="text",
                    text="❌ No valid configuration parameters provided"
                )]
            
            gemini.update_config(**updates)
            
            updated_items = []
            for key, value in updates.items():
                updated_items.append(f"- {key}: {value}")
            
            update_text = f"""✅ **Configuration Updated**

Updated parameters:
{chr(10).join(updated_items)}

Use `/gemini_status` to see the current configuration."""
            
            return [TextContent(type="text", text=update_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error updating configuration: {str(e)}"
            )]

async def main():
    parser = argparse.ArgumentParser(description="Gemini MCP Server")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Create and start the server
    server_instance = GeminiMCPServer(project_root=args.project_root)
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Gemini MCP Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1) 