#!/usr/bin/env python3
"""
Gemini CLI + Claude Integration Wrapper
This script extends Gemini CLI with Claude consultation capabilities
"""

import sys
import os
import subprocess
import asyncio
import argparse
import json
import re
from pathlib import Path
from typing import List, Optional

# Import Claude integration
from claude_integration import claude

class GeminiClaudeWrapper:
    def __init__(self):
        self.claude_enabled = True
        self.auto_consult = True
        self.verbose = False
    
    async def run_gemini_with_claude(self, args: List[str]) -> int:
        """Run Gemini CLI and optionally consult Claude"""
        
        # Check if this is a prompt request
        prompt_mode = False
        prompt_text = ""
        
        if "-p" in args or "--prompt" in args:
            prompt_mode = True
            try:
                prompt_idx = args.index("-p") if "-p" in args else args.index("--prompt")
                if prompt_idx + 1 < len(args):
                    prompt_text = args[prompt_idx + 1]
            except (ValueError, IndexError):
                pass
        
        # Run original Gemini CLI
        # On Windows, use PowerShell to call gemini with proper argument handling
        if os.name == 'nt':  # Windows
            # Build the full command as a string for PowerShell
            args_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in args)
            gemini_cmd = ["powershell", "-Command", f"gemini {args_str}"]
        else:
            gemini_cmd = ["gemini"] + args
        
        if self.verbose:
            print(f"🚀 Running: {' '.join(gemini_cmd)}")
        
        try:
            # Ensure PATH includes npm global directory
            env = os.environ.copy()
            npm_path = os.path.expanduser("~\\AppData\\Roaming\\npm")
            if npm_path not in env.get("PATH", ""):
                env["PATH"] = env.get("PATH", "") + ";" + npm_path
            
            result = subprocess.run(
                gemini_cmd,
                capture_output=prompt_mode and self.claude_enabled,
                text=True,
                encoding='utf-8',
                env=env
            )
            
            # If not in prompt mode or Claude disabled, just return the result
            if not prompt_mode or not self.claude_enabled:
                return result.returncode
            
            gemini_response = result.stdout.strip() if result.stdout else ""
            
            # Print Gemini's response
            print(gemini_response)
            
            # Check if we should consult Claude
            should_consult = False
            
            if self.auto_consult and claude.detect_uncertainty_patterns(gemini_response):
                should_consult = True
                if self.verbose:
                    print("\n🤔 Uncertainty detected in Gemini's response. Consulting Claude...")
            
            # Always offer manual Claude consultation
            if not should_consult:
                print("\n" + "="*60)
                print("💡 Would you like Claude's perspective on this? (y/N): ", end="", flush=True)
                try:
                    response = input().strip().lower()
                    should_consult = response in ['y', 'yes']
                except (EOFError, KeyboardInterrupt):
                    print()
                    return result.returncode
            
            if should_consult:
                await self.consult_claude(prompt_text, gemini_response)
            
            return result.returncode
            
        except FileNotFoundError:
            print("❌ Error: Gemini CLI not found. Please install it first:")
            print("   npm install -g @google/gemini-cli")
            return 1
        except Exception as e:
            print(f"❌ Error running Gemini CLI: {e}")
            return 1
    
    async def consult_claude(self, original_prompt: str, gemini_response: str):
        """Consult Claude for additional perspective"""
        print("\n" + "🤖 Consulting Claude..." + "\n" + "="*60)
        
        # Prepare Claude's prompt
        claude_prompt = f"""The user asked: "{original_prompt}"

Gemini responded with: "{gemini_response}"

Please provide your perspective on this question. Focus on:
1. Any additional insights or alternative viewpoints
2. Areas where you might disagree or have different emphasis
3. Practical considerations or nuances that might be helpful
4. Any corrections or clarifications if needed

Keep your response concise and complementary to Gemini's answer."""
        
        try:
            result = await claude.call_claude(claude_prompt)
            
            if result["success"]:
                print(f"🧠 **Claude {result['model']} adds:**")
                print(f"{result['response']}")
                print(f"\n⏱️  *Response time: {result['timestamp']}*")
                
                if 'usage' in result and result['usage']:
                    usage = result['usage']
                    if 'input_tokens' in usage and 'output_tokens' in usage:
                        print(f"📊 *Tokens: {usage['input_tokens']} in, {usage['output_tokens']} out*")
            else:
                print(f"❌ **Claude consultation failed:**")
                print(f"Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error consulting Claude: {e}")
        
        print("="*60)
    
    def run_interactive_mode(self):
        """Run interactive mode with Claude integration"""
        print("🤖 Gemini CLI + Claude Integration")
        print("Type 'exit' to quit, 'claude' to toggle Claude, 'status' for info")
        print("="*60)
        
        while True:
            try:
                user_input = input("\ngemini> ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'claude':
                    self.claude_enabled = not self.claude_enabled
                    status = "enabled" if self.claude_enabled else "disabled"
                    print(f"🔄 Claude consultation {status}")
                    continue
                elif user_input.lower() == 'status':
                    self.print_status()
                    continue
                elif user_input.lower().startswith('claude '):
                    # Direct Claude query
                    claude_query = user_input[7:]  # Remove 'claude ' prefix
                    asyncio.run(self.direct_claude_query(claude_query))
                    continue
                elif not user_input:
                    continue
                
                # Run Gemini with the input
                args = ["-p", user_input]
                asyncio.run(self.run_gemini_with_claude(args))
                
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def direct_claude_query(self, query: str):
        """Direct query to Claude"""
        print("🧠 Asking Claude directly...")
        try:
            result = await claude.call_claude(query)
            
            if result["success"]:
                print(f"\n**Claude {result['model']}:**")
                print(result['response'])
            else:
                print(f"❌ Claude error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def print_status(self):
        """Print current status"""
        claude_status = claude.get_status()
        
        print("\n📊 **Integration Status:**")
        print(f"• Claude enabled: {'✅' if self.claude_enabled else '❌'}")
        print(f"• Auto-consult: {'✅' if self.auto_consult else '❌'}")
        print(f"• Claude model: {claude_status['model']}")
        print(f"• API key set: {'✅' if claude_status['api_key_set'] else '❌'}")
        print(f"• Total Claude calls: {claude_status['session_stats']['total_calls']}")
        print(f"• Successful: {claude_status['session_stats']['successful_calls']}")
        print(f"• Failed: {claude_status['session_stats']['failed_calls']}")

def main():
    parser = argparse.ArgumentParser(
        description="Gemini CLI + Claude Integration",
        add_help=False  # We'll handle help manually to pass through to Gemini
    )
    
    parser.add_argument('--no-claude', action='store_true', 
                       help='Disable Claude integration')
    parser.add_argument('--no-auto-consult', action='store_true',
                       help='Disable automatic Claude consultation')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--claude-only', action='store_true',
                       help='Use only Claude (skip Gemini)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive mode')
    
    # Parse known args to separate our args from Gemini args
    known_args, gemini_args = parser.parse_known_args()
    
    # Create wrapper instance
    wrapper = GeminiClaudeWrapper()
    wrapper.claude_enabled = not known_args.no_claude
    wrapper.auto_consult = not known_args.no_auto_consult
    wrapper.verbose = known_args.verbose
    
    # Handle special modes
    if known_args.interactive:
        wrapper.run_interactive_mode()
        return 0
    
    if known_args.claude_only:
        if gemini_args and gemini_args[0] == '-p' and len(gemini_args) > 1:
            prompt = gemini_args[1]
            asyncio.run(wrapper.direct_claude_query(prompt))
            return 0
        else:
            print("❌ --claude-only requires -p <prompt>")
            return 1
    
    # If no Gemini args provided, show help
    if not gemini_args:
        print("🤖 Gemini CLI + Claude Integration")
        print("\nUsage:")
        print("  python gemini_claude_wrapper.py [wrapper-options] [gemini-options]")
        print("\nWrapper options:")
        print("  --no-claude           Disable Claude integration")
        print("  --no-auto-consult     Disable automatic Claude consultation")
        print("  --verbose, -v         Verbose output")
        print("  --claude-only         Use only Claude (skip Gemini)")
        print("  --interactive, -i     Start interactive mode")
        print("\nExamples:")
        print("  python gemini_claude_wrapper.py -p 'What is quantum computing?'")
        print("  python gemini_claude_wrapper.py --claude-only -p 'Explain AI ethics'")
        print("  python gemini_claude_wrapper.py --interactive")
        print("\nAll other arguments are passed to Gemini CLI.")
        return 0
    
    # Run Gemini with Claude integration
    return asyncio.run(wrapper.run_gemini_with_claude(gemini_args))

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1) 