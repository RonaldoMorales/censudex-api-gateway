import uvicorn
import os
import sys
from dotenv import load_dotenv

if len(sys.argv) > 1:
    env_file = sys.argv[1]
    load_dotenv(env_file)
else:
    load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)