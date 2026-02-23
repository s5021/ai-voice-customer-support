import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("Voice Bot Server Starting...")
    print("=" * 50)
    print(f"Port: {port}")
    print("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=port)