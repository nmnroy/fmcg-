"""
Initialize ChromaDB with SKU Catalog

This script loads the SKU catalog from CSV and creates embeddings
in ChromaDB for semantic search.

Author: FMCG RFP Automation Team
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the embeddings database with SKU catalog."""
    try:
        from utils.embeddings import create_embeddings_manager
        
        sku_catalog_path = os.getenv("SKU_CATALOG_PATH", "data/sku_catalog.csv")
        
        print("🔄 Initializing embeddings database...")
        print(f"📂 Loading SKU catalog from: {sku_catalog_path}")
        
        # Create embeddings manager and load catalog
        manager = create_embeddings_manager(sku_catalog_path)
        
        if manager:
            stats = manager.get_collection_stats()
            print(f"✅ Database initialized successfully!")
            print(f"📊 Collection Stats: {stats}")
            return True
        else:
            print("❌ Failed to create embeddings manager")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
