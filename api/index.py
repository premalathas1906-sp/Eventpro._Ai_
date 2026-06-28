import os
import sys

# Add root folder to sys.path to resolve imports cleanly on Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()
