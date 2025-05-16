from dotenv import load_dotenv
load_dotenv()

from app import app
import config

if __name__ == "__main__":
    debug_mode = config.DEBUG if hasattr(config, 'DEBUG') else False
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)