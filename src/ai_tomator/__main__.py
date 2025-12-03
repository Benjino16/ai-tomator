import os
import threading
import time
import webbrowser

import uvicorn
from ai_tomator.app import app


def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000/ui")


def main():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
