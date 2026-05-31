VENV = .venv/bin

.PHONY: api mock-api

api:
	$(VENV)/uvicorn eval_pipeline.app:app --reload

mock-api:
	$(VENV)/uvicorn eval_pipeline.routers.mock_file_processing:app --reload --port 8001
