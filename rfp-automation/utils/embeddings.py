"""
Embeddings Utility for RFP Automation System

This module handles:
- Loading SKU catalog from CSV
- Creating embeddings using sentence-transformers
- Setting up ChromaDB for semantic search
- Performing similarity search for SKU matching

Author: FMCG RFP Automation Team
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SKUEmbeddings:
    """Embeddings manager for SKU catalog semantic search."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", persist_directory: str = "./chroma_db"):
        self.model_name = model_name
        self.persist_directory = persist_directory
        self.model = None
        self.collection = None
        self.client = None
        self.sku_data = {}
        self._initialize_model()
        self._initialize_chromadb()

    def _initialize_model(self):
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def _initialize_chromadb(self):
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            collection_name = "sku_catalog"
            try:
                self.collection = self.client.get_collection(name=collection_name)
                logger.info(f"Connected to existing collection: {collection_name}")
            except Exception:
                self.collection = self.client.create_collection(name=collection_name)
                logger.info(f"Created new collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise

    def load_sku_catalog(self, csv_path: str, clear_existing: bool = False) -> bool:
        try:
            logger.info(f"Loading SKU catalog from: {csv_path}")
            df = pd.read_csv(csv_path)
            required_columns = ['sku_id', 'name', 'category', 'specs', 'base_cost', 'unit']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Missing required columns in {csv_path}")
                return False

            if clear_existing:
                self.collection.delete(where={})
                logger.info("Cleared existing embeddings")

            documents, metadatas, ids = [], [], []
            for _, row in df.iterrows():
                searchable_text = self._create_searchable_text(row)
                documents.append(searchable_text)
                metadata = {
                    'sku_id': str(row['sku_id']),
                    'name': str(row['name']),
                    'category': str(row['category']),
                    'specs': str(row['specs']),
                    'base_cost': float(row['base_cost']),
                    'unit': str(row['unit'])
                }
                metadatas.append(metadata)
                ids.append(str(row['sku_id']))
                self.sku_data[str(row['sku_id'])] = metadata

            logger.info("Creating embeddings for SKU catalog...")
            embeddings = self.model.encode(documents, show_progress_bar=True)
            embedding_list = embeddings.tolist()

            batch_size = 100
            for i in range(0, len(documents), batch_size):
                self.collection.add(
                    documents=documents[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size],
                    embeddings=embedding_list[i:i+batch_size]
                )
            logger.info(f"Successfully loaded {len(documents)} SKUs with embeddings")
            return True
        except Exception as e:
            logger.error(f"Error loading SKU catalog: {e}")
            return False

    def _create_searchable_text(self, row: pd.Series) -> str:
        """Create more descriptive text from SKU data for better semantic search."""
        parts = [
            f"Product Name: {row['name']}",
            f"Category: {row['category']}",
        ]
        specs_str = str(row['specs'])
        try:
            specs = dict(s.split(':') for s in specs_str.split(',') if ':' in s)
            for key, value in specs.items():
                parts.append(f"{key.strip().capitalize()}: {value.strip()}")
        except (ValueError, TypeError):
            parts.append(f"Specifications: {specs_str}")

        parts.append(f"Packaging Unit: {row['unit']}")
        return ', '.join(parts)

    def search_similar_skus(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Searching for SKUs similar to: '{query}'")
            query_embedding = self.model.encode([query])
            where_clause = {"category": category_filter} if category_filter else {}
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=top_k,
                where=where_clause if where_clause else None,
                include=['metadatas', 'distances', 'documents']
            )

            similar_skus = []
            if results and results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    sku_result = {
                        'sku_id': metadata['sku_id'],
                        'name': metadata['name'],
                        'category': metadata['category'],
                        'specs': metadata['specs'],
                        'base_cost': metadata['base_cost'],
                        'unit': metadata['unit'],
                        'similarity_score': similarity,
                        'searchable_text': results['documents'][0][i]
                    }
                    similar_skus.append(sku_result)
            logger.info(f"Found {len(similar_skus)} similar SKUs")
            return similar_skus
        except Exception as e:
            logger.error(f"Error searching SKUs: {e}")
            return []

    def get_sku_by_id(self, sku_id: str) -> Optional[Dict[str, Any]]:
        try:
            results = self.collection.get(ids=[sku_id], include=['metadatas'])
            return results['metadatas'][0] if results and results['metadatas'] else None
        except Exception as e:
            logger.error(f"Error getting SKU by ID: {e}")
            return None

    def get_all_categories(self) -> List[str]:
        try:
            results = self.collection.get(include=['metadatas'])
            if not results or not results['metadatas']:
                return []
            categories = {metadata['category'] for metadata in results['metadatas'] if 'category' in metadata}
            return sorted(list(categories))
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        try:
            return {
                'total_skus': self.collection.count(),
                'categories': self.get_all_categories(),
                'model_name': self.model_name,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    def clear_collection(self) -> bool:
        try:
            self.collection.delete(where={})
            self.sku_data.clear()
            logger.info("Collection cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False


def create_embeddings_manager(csv_path: str, model_name: str = "all-MiniLM-L6-v2") -> Optional[SKUEmbeddings]:
    try:
        embeddings = SKUEmbeddings(model_name=model_name)
        if embeddings.load_sku_catalog(csv_path):
            logger.info("Embeddings manager created and loaded successfully")
            return embeddings
        logger.error("Failed to load SKU catalog")
        return None
    except Exception as e:
        logger.error(f"Error creating embeddings manager: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python embeddings.py <path_to_sku_catalog.csv>")
        sys.exit(1)

    manager = create_embeddings_manager(sys.argv[1])
    if manager:
        print("\nCollection Stats:", json.dumps(manager.get_collection_stats(), indent=2))
        for query in ["chocolate biscuits", "cooking oil", "tea bags"]:
            print(f"\nSearching for: '{query}'")
            results = manager.search_similar_skus(query, top_k=3)
            print(json.dumps(results, indent=2))
