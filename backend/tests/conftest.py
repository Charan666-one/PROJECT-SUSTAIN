import os
import tempfile

# Isolate the local vector store and disable external calls for the test run.
os.environ.setdefault("VECTOR_STORE_DIR", tempfile.mkdtemp(prefix="vecstore_test_"))
os.environ["ANTHROPIC_API_KEY"] = ""
