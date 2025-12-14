"""
Setup Verification Script for RFP Automation System

This script checks if all the core components of the system can be initialized correctly.
It verifies:
- Environment variables are loaded.
- PDFParser can be instantiated.
- SKUEmbeddings manager can be created (requires a dummy SKU file).
- RFPIntakeAgent can be initialized.

Author: FMCG RFP Automation Team
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_setup():
    """Runs a series of checks to verify the environment and components."""
    logger.info("--- Starting Environment & Setup Verification ---")
    
    # 1. Check for .env file and load it
    logger.info("1. Checking for .env file...")
    if not os.path.exists('.env'):
        logger.error("FATAL: .env file not found. Please copy .env.example to .env and fill in your API keys.")
        return False
    load_dotenv()
    logger.info("   .env file found and loaded.")

    # 2. Verify critical environment variables
    logger.info("2. Verifying critical environment variables...")
    required_vars = ['SKU_CATALOG_PATH', 'PRICING_RULES_PATH']
    if os.getenv('USE_LOCAL_MODEL', 'false').lower() != 'true':
        if os.getenv('OPENAI_API_KEY'):
            required_vars.append('OPENAI_API_KEY')
        elif os.getenv('GROQ_API_KEY'):
            required_vars.append('GROQ_API_KEY')
        else:
            logger.error("FATAL: No LLM API key found (OPENAI_API_KEY or GROQ_API_KEY). Please set one in .env.")
            return False

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"FATAL: Missing environment variables: {', '.join(missing_vars)}")
        return False
    logger.info("   All critical environment variables are set.")

    # 3. Check core component imports
    logger.info("3. Checking core component imports...")
    try:
        from utils.pdf_parser import PDFParser
        from utils.embeddings import SKUEmbeddings
        from agents.intake_agent import RFPIntakeAgent
        logger.info("   Successfully imported all core components.")
    except ImportError as e:
        logger.error(f"FATAL: Failed to import a core component: {e}")
        logger.error("   Please ensure all files are syntactically correct and in the right directories.")
        return False

    # 4. Check for necessary data files and directories
    logger.info("4. Verifying data files and directories...")
    sku_path = os.getenv('SKU_CATALOG_PATH')
    pricing_path = os.getenv('PRICING_RULES_PATH')
    
    # Create dummy files if they don't exist to allow initialization
    if not os.path.exists(sku_path):
        logger.warning(f"   SKU catalog not found at '{sku_path}'. Creating a dummy file for testing.")
        os.makedirs(os.path.dirname(sku_path), exist_ok=True)
        with open(sku_path, 'w') as f:
            f.write('SKU,Description,Category,BaseCost\n')
            f.write('DUMMY-001,Dummy Product,Dummy,10.0\n')

    if not os.path.exists(pricing_path):
        logger.warning(f"   Pricing rules not found at '{pricing_path}'. Creating a dummy file for testing.")
        os.makedirs(os.path.dirname(pricing_path), exist_ok=True)
        with open(pricing_path, 'w') as f:
            f.write('{}')

    logger.info("   Data files and directories verified.")

    # 5. Initialize components
    logger.info("5. Initializing core components...")
    try:
        parser = PDFParser()
        logger.info("   - PDFParser initialized successfully.")
        
        embeddings = SKUEmbeddings()
        embeddings.load_sku_catalog(sku_path)
        logger.info("   - SKUEmbeddings initialized and loaded dummy data successfully.")

        agent = RFPIntakeAgent()
        logger.info("   - RFPIntakeAgent initialized successfully.")

    except Exception as e:
        logger.error(f"FATAL: Failed to initialize a component: {e}", exc_info=True)
        return False

    logger.info("--- Verification Complete: Setup is successful! ---")
    return True

if __name__ == "__main__":
    if not check_setup():
        sys.exit(1)
