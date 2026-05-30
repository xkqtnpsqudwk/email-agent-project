import threading

# Shared lock for thread-safe file I/O across all tools
file_lock = threading.Lock()
