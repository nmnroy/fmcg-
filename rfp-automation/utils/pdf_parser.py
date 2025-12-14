"""
PDF Parser Utility for RFP Automation System

This module handles parsing of PDF and text files to extract:
- Raw text content
- Client information (name, organization)
- Deadlines and due dates
- Line items with quantities and specifications
- Other relevant metadata

Author: FMCG RFP Automation Team
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    """Parser for RFP documents (PDF and text files)."""

    def __init__(self):
        """Initialize the PDF parser with more robust regex patterns."""
        self.client_patterns = [
            r"(?:Company|Client|Organization|Issued by|From|For|To)[:\-]?\s*([^\n\r]+)",
            r"^([A-Z][a-zA-Z\s&,]+(?:Inc|Corp|LLC|Ltd|Company|Corporation))\s*$",
        ]

        self.deadline_patterns = [
            r"(?:Deadline|Due Date|Submission Date|Closing Date)[:\-]?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
            r"(?:Deadline|Due Date|Closing Date)[:\-]?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            r"(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s*(?:by|at|on)",
        ]

        self.line_item_patterns = [
            r"(?:Item|ID|No\.)?\s*(\d+)[\.\s]\s*([^\n\r]+?)\s+(?:Qty|Quantity)[:\-]?\s*(\d+)",
            r"(\d+)\s+x\s+([^\n\r]+)",
            r"^\s*(\d+)\.\s+([^\n\r]+?)(?:\s*[-:]\s*(\d+))?",
        ]

        self.value_patterns = [
            r"(?:Estimated|Total|Approximate) Value[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)",
            r"Budget[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)",
            r"Total Contract Value[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)",
        ]
    
    def parse_rfp_text(self, text: str) -> Dict[str, Any]:
        """
        Parse RFP text content and extract structured information
        
        Args:
            text: Raw text content from PDF or text file
            
        Returns:
            Dictionary with parsed RFP data
        """
        try:
            logger.info("Starting RFP text parsing...")
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Extract metadata
            metadata = self._extract_metadata(cleaned_text)
            
            # Extract line items
            line_items = self._extract_line_items(cleaned_text)
            
            # Generate unique RFP ID
            rfp_id = self._generate_rfp_id(metadata)
            
            result = {
                "rfp_id": rfp_id,
                "raw_text": cleaned_text,
                "metadata": metadata,
                "line_items": line_items,
                "parsing_timestamp": datetime.now().isoformat(),
                "text_length": len(cleaned_text),
                "line_item_count": len(line_items)
            }
            
            logger.info(f"Successfully parsed RFP: {rfp_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing RFP text: {str(e)}")
            return self._create_error_result(str(e), text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\$\/\@\#\%\&\+\=\*\!]', ' ', text)
        # Normalize line breaks
        text = re.sub(r'\r\n|\r', '\n', text)
        return text.strip()
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from text"""
        metadata = {
            "client_name": "",
            "rfp_title": "",
            "deadline": "",
            "estimated_value": "",
            "mandatory_requirements": [],
            "industry": "FMCG"
        }
        
        # Extract client name
        for pattern in self.client_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["client_name"] = match.group(1).strip()
                break
        
        # Extract deadline
        for pattern in self.deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline_str = match.group(1)
                metadata["deadline"] = self._normalize_date(deadline_str)
                break
        
        # Extract estimated value
        for pattern in self.value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                    metadata["estimated_value"] = f"${value:,.2f}"
                except ValueError:
                    metadata["estimated_value"] = value_str
                break
        
        # Extract RFP title (first line or first significant line)
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 10 and not line.lower().startswith(('to:', 'from:', 'date:', 'subject:')):
                metadata["rfp_title"] = line[:100]  # Limit title length
                break
        
        # Extract mandatory requirements
        requirements_patterns = [
            r"(?:Mandatory|Required|Must have|Essential)\s*(?:requirements?|criteria?)[\:\-]\s*([^\n\r]+)",
            r"(?:Requirements?|Criteria?)[\:\-]\s*([^\n\r]+)",
        ]
        
        for pattern in requirements_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split by common delimiters and clean
                reqs = re.split(r'[,;•\-\*]', match)
                cleaned_reqs = [req.strip() for req in reqs if len(req.strip()) > 5]
                metadata["mandatory_requirements"].extend(cleaned_reqs[:5])  # Limit to 5 requirements
        
        return metadata
    
    def _extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from text"""
        line_items = []
        
        for pattern in self.line_item_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    item_id = match[0].strip()
                    description = match[1].strip()
                    quantity = match[2].strip()
                    
                    # Try to extract specs from description
                    specs = self._extract_specs_from_description(description)
                    
                    line_item = {
                        "item_id": item_id,
                        "description": description,
                        "quantity": self._clean_quantity(quantity),
                        "specs": specs,
                        "unit": self._infer_unit(description)
                    }
                    
                    line_items.append(line_item)
        
        # If no structured items found, try to extract from numbered lists
        if not line_items:
            line_items = self._extract_numbered_items(text)
        
        return line_items[:50]  # Limit to 50 items
    
    def _extract_specs_from_description(self, description: str) -> Dict[str, str]:
        """Extract specifications from item description"""
        specs = {}
        
        # Common spec patterns
        spec_patterns = {
            "weight": r"(\d+(?:\.\d+)?)\s*(?:g|kg|gram|kilogram)s?",
            "volume": r"(\d+(?:\.\d+)?)\s*(?:ml|l|liter|milliliter)s?",
            "count": r"(\d+)\s*(?:pcs?|pieces?|units?|items?|count)",
            "packaging": r"(?:packaging|pack)?\s*[:\-]?\s*(box|packet|bottle|jar|can|bag|carton)",
            "flavor": r"(?:flavor|variant)?\s*[:\-]?\s*([a-zA-Z]+)",
            "size": r"(?:size)?\s*[:\-]?\s*(small|medium|large|xlarge|xl|s|m|l)",
        }
        
        for spec_type, pattern in spec_patterns.items():
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                specs[spec_type] = match.group(1).strip()
        
        return specs
    
    def _clean_quantity(self, quantity: str) -> str:
        """Clean and normalize quantity string"""
        # Remove non-numeric characters except for decimal points
        cleaned = re.sub(r'[^\d\.]', '', quantity)
        try:
            # Convert to int if it's a whole number
            if '.' not in cleaned:
                return str(int(float(cleaned)))
            else:
                return str(float(cleaned))
        except (ValueError, TypeError):
            return quantity  # Return original if conversion fails
    
    def _infer_unit(self, description: str) -> str:
        """Infer unit from description"""
        unit_indicators = {
            "box": "box",
            "boxes": "box", 
            "packet": "packet",
            "packets": "packet",
            "bottle": "bottle",
            "bottles": "bottle",
            "jar": "jar",
            "jars": "jar",
            "can": "can",
            "cans": "can",
            "bag": "bag",
            "bags": "bag",
            "carton": "carton",
            "cartons": "carton",
        }
        
        description_lower = description.lower()
        for indicator, unit in unit_indicators.items():
            if indicator in description_lower:
                return unit
        
        return "units"  # Default unit
    
    def _extract_numbered_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract items from numbered lists when structured patterns fail"""
        items = []
        
        # Pattern for numbered list items
        numbered_pattern = r"(\d+)\.\s*([^\n\r]+?)(?:\s*[-:]?\s*(\d+))?"
        matches = re.findall(numbered_pattern, text)
        
        for match in matches:
            item_id = match[0].strip()
            description = match[1].strip()
            quantity = match[2] if match[2] else "1"  # Default to 1 if no quantity
            
            item = {
                "item_id": item_id,
                "description": description,
                "quantity": quantity,
                "specs": self._extract_specs_from_description(description),
                "unit": self._infer_unit(description)
            }
            items.append(item)
        
        return items
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to standard format"""
        try:
            # Try different date formats
            formats = [
                "%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y",
                "%B %d, %Y", "%b %d, %Y",
                "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"
            ]
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            return date_str  # Return original if parsing fails
        except Exception:
            return date_str
    
    def _generate_rfp_id(self, metadata: Dict[str, Any]) -> str:
        """Generate unique RFP ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = metadata.get("client_name", "Unknown").replace(" ", "_")[:10]
        return f"RFP_{client_name}_{timestamp}"
    
    def _create_error_result(self, error_msg: str, original_text: str) -> Dict[str, Any]:
        """Create error result when parsing fails"""
        return {
            "rfp_id": f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "raw_text": original_text,
            "metadata": {"client_name": "", "rfp_title": "", "deadline": "", "estimated_value": "", "mandatory_requirements": []},
            "line_items": [],
            "parsing_timestamp": datetime.now().isoformat(),
            "error": error_msg,
            "text_length": len(original_text),
            "line_item_count": 0
        }


def parse_rfp_pdf(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse RFP from PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Parsed RFP data dictionary
    """
    try:
        import PyPDF2
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        parser = PDFParser()
        return parser.parse_rfp_text(text)
        
    except ImportError:
        logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
        return {"error": "PyPDF2 not installed"}
    except Exception as e:
        logger.error(f"Error reading PDF file: {str(e)}")
        return {"error": f"Error reading PDF file: {str(e)}"}


def parse_rfp_text_file(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse RFP from text file
    
    Args:
        file_path: Path to text file
        
    Returns:
        Parsed RFP data dictionary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        parser = PDFParser()
        return parser.parse_rfp_text(text)
        
    except Exception as e:
        logger.error(f"Error reading text file: {str(e)}")
        return {"error": f"Error reading text file: {str(e)}"}


if __name__ == "__main__":
    # Test the parser with sample text
    sample_text = """
    Company Name: Global Foods Inc.
    RFP Title: Q4 2024 Beverage Supply Contract
    Deadline: 12/15/2024
    Estimated Value: $50,000
    
    Requirements:
    1. Premium Tea Bags 100ct - 500 boxes
    2. Instant Coffee 200g - 300 jars  
    3. Cooking Oil 1L - 1000 bottles
    """
    
    parser = PDFParser()
    result = parser.parse_rfp_text(sample_text)
    print(json.dumps(result, indent=2))
