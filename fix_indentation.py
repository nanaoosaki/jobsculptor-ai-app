#!/usr/bin/env python
# Fix specific indentation issue at line 213 of claude_integration.py

import os
import shutil
import re

def fix_indentation_issues():
    # Make a backup
    shutil.copy('claude_integration.py', 'claude_integration.py.bak_indent')
    print("Created backup: claude_integration.py.bak_indent")
    
    # Read the file
    with open('claude_integration.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix indentation issues
    
    # Fix line 197 - statement separation
    content = re.sub(
        r'logger\.info\(f"Tailoring resume with {provider} LLM"\)\s+# Extract resume sections',
        'logger.info(f"Tailoring resume with {provider} LLM")\n    \n    # Extract resume sections',
        content
    )
    
    # Fix lines 475, 477, 482 - indentation blocks
    content = re.sub(
        r'if provider\.lower\(\) == "claude":\s+llm_client = ClaudeClient\(api_key, api_url\)',
        'if provider.lower() == "claude":\n        llm_client = ClaudeClient(api_key, api_url)',
        content
    )
    
    content = re.sub(
        r'elif provider\.lower\(\) == "openai":\s+llm_client = OpenAIClient\(api_key\)',
        'elif provider.lower() == "openai":\n        llm_client = OpenAIClient(api_key)',
        content
    )
    
    content = re.sub(
        r'else:\s+raise ValueError\(f"Unsupported LLM provider: {provider}"\)',
        'else:\n        raise ValueError(f"Unsupported LLM provider: {provider}")',
        content
    )
    
    # Fix line 680 - statement separation
    content = re.sub(
        r'except \(ImportError, Exception\) as e:\s+logger\.warning',
        'except (ImportError, Exception) as e:\n            logger.warning',
        content
    )
    
    # Fix line 1363 - indentation issue
    content = re.sub(
        r'validation_success = validate_bullet_point_cleaning\(sections: Dict\[str, str\]\) -> bool:',
        'validation_success = validate_bullet_point_cleaning(cleaned_sections)\n        if not validation_success:',
        content
    )
    
    # Fix line 1704 - unexpected indentation
    content = re.sub(
        r'# Return info without generating YC-style PDF\s+return output_filename',
        '# Return info without generating YC-style PDF\n    return output_filename',
        content
    )
    
    # Write back the fixed content
    with open('claude_integration.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed indentation issues in claude_integration.py")

if __name__ == "__main__":
    fix_indentation_issues()

# Backup the original file
shutil.copy('claude_integration.py', 'claude_integration.py.bak5')

# Read the file line by line
with open('claude_integration.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 213 (0-indexed is 212)
if len(lines) > 212 and '     analysis = job_data[\'analysis\']' in lines[212]:
    lines[212] = '                analysis = job_data[\'analysis\']\n'
    print("Fixed indentation at line 213")
else:
    print("Line 213 not found or doesn't match expected pattern")

# Write the file back
with open('claude_integration.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Script completed")

# Read the file
with open('claude_integration.py', 'r', encoding='utf-8') as file:
    content = file.read()

# Create backup
with open('claude_integration.py.bak_fix3', 'w', encoding='utf-8') as file:
    file.write(content)

# Fix syntax error on line 1002
content = re.sub(
    r'# No JSON found, return the original content\s+logger\.error\(\s*\n\s+f"No JSON found in OpenAI response for {section_name}"\)',
    r'# No JSON found, return the original content\n                    logger.error(f"No JSON found in OpenAI response for {section_name}")',
    content
)

# Fix misaligned logger warnings
content = re.sub(
    r'else:\s+logger\.warning\(\s*\n\s+f',
    r'else:\n                logger.warning(\n                    f',
    content
)

# Fix indentation in _format_experience_json method
content = re.sub(
    r'if not experience_data:\s*\n\s+return ""',
    r'if not experience_data:\n            return ""',
    content
)

# Fix string formatting for company names
content = re.sub(
    r'formatted_text \+= f"<p class=\'job-header\'><span class=\'company\'>{(?:\s*\n\s+)company\.upper\(\)}</span>',
    r'formatted_text += f"<p class=\'job-header\'><span class=\'company\'>{company.upper()}</span>',
    content
)

# Fix string formatting for institution names
content = re.sub(
    r'formatted_text \+= f"<p class=\'education-header\'><span class=\'institution\'>{(?:\s*\n\s+)institution\.upper\(\)}</span>',
    r'formatted_text += f"<p class=\'education-header\'><span class=\'institution\'>{institution.upper()}</span>',
    content
)

# Fix string formatting for projects
content = re.sub(
    r'formatted_text \+= f"<p class=\'project-header\'><span class=\'project-title\'>{(?:\s*\n\s+)title\.upper\(\)}</span>"',
    r'formatted_text += f"<p class=\'project-header\'><span class=\'project-title\'>{title.upper()}</span>"',
    content
)

# Fix string formatting for skills lists
content = re.sub(
    r'technical_skills = \[\s*\n\s+s for s in',
    r'technical_skills = [s for s in',
    content
)

# Fix string formatting for current_app
content = re.sub(
    r'api_responses_dir = os\.path\.join\(\s*\n\s+current_app\.config',
    r'api_responses_dir = os.path.join(current_app.config',
    content
)

# Write the fixed content
with open('claude_integration.py', 'w', encoding='utf-8') as file:
    file.write(content)

print("Fixed syntax errors in claude_integration.py") 