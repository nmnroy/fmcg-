import os
from dotenv import load_dotenv
from utils.embeddings import SKUEmbeddings

load_dotenv()

def initialize_database():
    print("Initializing Database...")
    
    catalog_path = "data/sku_catalog.csv"
    if not os.path.exists(catalog_path):
        print("ERROR: sku_catalog.csv not found!")
        return False
    
    try:
        embeddings = SKUEmbeddings()
        embeddings.load_sku_catalog(catalog_path)
        print("SUCCESS: Database initialized!")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    initialize_database()