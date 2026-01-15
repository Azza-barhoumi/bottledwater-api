#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BottledWater API - Backend Server
Flask development server entry point
"""

import os
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(app_dir.parent))

try:
    from app import create_app
    
    if __name__ == '__main__':
        app = create_app()
        # If the database is empty (no brands), seed it automatically for developer convenience
        try:
            from app.models import Brand
            from app.seed import seed as seed_fn
            with app.app_context():
                if Brand.query.count() == 0:
                    print('[→] No brands found in database, running seed()')
                    seed_fn()
        except Exception:
            # non-fatal: continue starting server even if seeding fails
            pass
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        print(f'[✓] Flask app created successfully')
        print(f'[→] Starting server on 0.0.0.0:{port}')
        print(f'[→] Debug mode: {debug}')
        app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
except Exception as e:
    print(f'[✗] Failed to start server: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
