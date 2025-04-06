"""LLM processor module using Google's Gemini API.

This module handles the processing of trading messages through Gemini to standardize their format.
"""

import os
import re
from typing import Optional, Tuple
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def sort_price_range(price_range_str: str) -> str:
    """Takes a price range string and ensures lower value comes first.
    
    Args:
        price_range_str: String containing two numbers separated by a hyphen.
        
    Returns:
        Formatted string with lower number first.
        
    Example:
        "2343 - 1234" becomes "1234 - 2343"
    """
    try:
        numbers = re.findall(r'[\d.]+', price_range_str)
        if len(numbers) == 2:
            num1, num2 = float(numbers[0]), float(numbers[1])
            return f"{min(num1, num2)} - {max(num1, num2)}"
    except:
        pass
    return price_range_str

def format_final_response(response_text: str) -> str:
    """Post-process the LLM response to ensure price ranges are properly formatted.
    
    Args:
        response_text: The raw response from the LLM.
        
    Returns:
        Formatted response with sorted price ranges.
    """
    lines = response_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.startswith('Entry:') and ' - ' in line:
            prefix = line.split(':')[0] + ': '
            price_range = line[len(prefix):].strip()
            sorted_range = sort_price_range(price_range)
            formatted_lines.append(f"{prefix}{sorted_range}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def process_with_llm(message_text: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Process the trading message through Gemini to validate and format in one call.
    
    Args:
        message_text: The original trading message to process.
        
    Returns:
        Tuple containing:
        - bool: True if message is valid
        - Optional[str]: Reason if invalid, None if valid
        - Optional[str]: Formatted message if valid, None if invalid
    """
    prompt = f"""You are a trading signal validator and formatter. First validate if this is a valid trading signal, then if valid, format it according to the rules.

Original message:
{message_text}

Step 1 - Validation:
A valid trading signal usually has:
- Entry price or range
- Stop loss
- Direction (buy/sell)
- Take profit (optional)

Step 2 - If valid, format using these rules:
1. Keep exactly these fields in this order:
   - Asset
   - Type (BUY/SELL)
   - Entry (single price or range)
   - Stop Loss
   - Take Profit (multiple targets if present)
2. For ranges, always put lower value first
3. Keep exact numbers, don't modify values
4. Remove any extra text or commentary
5. If the message has Buy now or Sell now. Add a property to the final response called "At: NOW"
6. Use exactly this format:
Asset: [Symbol]
Type: [BUY/SELL]
Entry: [Price] or [Low - High]
Stop Loss: [Price]
Take Profit: [TP1] [TP2] [TP3]

Respond in this exact format:
VALID: [true/false]
REASON: [If invalid, explain why. If valid, write "Valid trading signal"]
FORMAT:
[If valid, include the formatted message here using the format above]

Example Response for Valid Message:
VALID: true
REASON: Valid trading signal
FORMAT:
Asset: GOLD
Type: BUY
Entry: 2930.88 - 2934.88
Stop Loss: 2926.88
Take Profit: 2936.68

Example Response for Invalid Message:
VALID: false
REASON: Missing stop loss level
FORMAT: None"""
    
    try:
        response = model.generate_content(prompt)
        
        if not response.text:
            return False, "Empty response from LLM", None
            
        # Parse response
        sections = response.text.strip().split('\n')
        
        # Extract validity
        valid_line = next((line for line in sections if line.startswith('VALID:')), '')
        is_valid = 'true' in valid_line.lower()
        
        # Extract reason
        reason_line = next((line for line in sections if line.startswith('REASON:')), '')
        reason = reason_line.split(':', 1)[1].strip() if reason_line else None
        
        if not is_valid:
            return False, reason, None
            
        # Extract and format the trading signal
        format_section = '\n'.join(sections[sections.index('FORMAT:') + 1:]).strip()
        if not format_section or format_section == 'None':
            return False, "Failed to format message", None
            
        # Post-process to ensure price ranges are properly sorted
        final_response = format_final_response(format_section)
        return True, None, final_response
            
    except Exception as e:
        return False, f"Error processing message: {str(e)}", None 