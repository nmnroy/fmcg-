.PHONY: all test test-cli test-sdk audit run-backend run-streamlit run-frontend benchmark clean

# Default target
all: test audit

# Run all test suites
test:
	python3 -m unittest discover -s tests -p "test_*.py"

# Run CLI tests specifically
test-cli:
	python3 -m unittest tests/test_cli.py

# Run Python SDK client tests
test-sdk:
	python3 -m unittest tests/test_sdk.py

# Run complete system integration audit runner
audit:
	python3 verify_system.py

# Run benchmark pipeline with 20 iterations
benchmark:
	python3 scripts/benchmark_pipeline.py 20

# Run FastAPI backend locally
run-backend:
	uvicorn backend.server:app --reload --port 8000

# Run Streamlit UI locally
run-streamlit:
	streamlit run streamlit_app.py

# Run React frontend
run-frontend:
	cd frontend && npm run dev

# Clean python bytecode and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f data/test_llm_cache.json
