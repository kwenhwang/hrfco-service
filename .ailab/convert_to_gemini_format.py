#!/usr/bin/env python3
"""
SuperClaude to Gemini CLI Format Converter
Converts SuperClaude .md command files to Gemini .tol format
"""

import os
import re
from pathlib import Path

def convert_md_to_tol(md_content, command_name):
    """Convert SuperClaude markdown content to Gemini .tol format"""
    
    # Extract description from the markdown
    description_match = re.search(r'description:\s*"([^"]*)"', md_content)
    description = description_match.group(1) if description_match else f"SuperClaude {command_name} command"
    
    # Extract usage pattern
    usage_match = re.search(r'```\n(/sc:[^\s]*.*?)\n```', md_content, re.DOTALL)
    usage = usage_match.group(1) if usage_match else f"/sc:{command_name}"
    
    # Extract main content (remove frontmatter and convert to plain text)
    content = re.sub(r'^---.*?---\n', '', md_content, flags=re.DOTALL)
    content = re.sub(r'```.*?\n', '', content)
    content = re.sub(r'```', '', content)
    content = content.strip()
    
    # Create .tol format content
    tol_content = f"""# {command_name.title()} - SuperClaude Command

**Description:** {description}

**Usage:** {usage}

{content}

This command is part of the SuperClaude framework integrated into Gemini CLI.
Use it to enhance your development workflow with AI-powered assistance.
"""
    
    return tol_content

def main():
    """Main conversion function"""
    gemini_commands_dir = Path.home() / ".gemini" / "commands" / "sc"
    
    if not gemini_commands_dir.exists():
        print(f"❌ SuperClaude commands directory not found: {gemini_commands_dir}")
        return
    
    print("🔄 Converting SuperClaude commands to Gemini format...")
    
    converted_count = 0
    
    for md_file in gemini_commands_dir.glob("*.md"):
        command_name = md_file.stem
        
        # Skip index.md for now
        if command_name == "index":
            continue
            
        print(f"   Converting {command_name}...")
        
        try:
            # Read original .md content
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert to .tol format
            tol_content = convert_md_to_tol(md_content, command_name)
            
            # Write .tol file
            tol_file = md_file.with_suffix('.tol')
            with open(tol_file, 'w', encoding='utf-8') as f:
                f.write(tol_content)
            
            # Remove original .md file
            md_file.unlink()
            
            converted_count += 1
            print(f"   ✅ {command_name}.md → {command_name}.tol")
            
        except Exception as e:
            print(f"   ❌ Error converting {command_name}: {e}")
    
    print(f"\n🎉 Conversion complete! Converted {converted_count} commands.")
    print(f"📁 Commands are now available in: {gemini_commands_dir}")
    print("\n🚀 Next steps:")
    print("   1. Run 'gemini' to start Gemini CLI")
    print("   2. Try '/sc' to see available SuperClaude commands")
    print("   3. Use commands like '/sc analyze', '/sc implement', etc.")

if __name__ == "__main__":
    main() 