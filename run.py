import os
import sys

print("=" * 50, flush=True)
print("Starting Voice Bot Application...", flush=True)
print("=" * 50, flush=True)

try:
    from app import create_app
    app = create_app()
    print("✅ App created successfully!", flush=True)
    
    # Get port from environment
    port = int(os.environ.get('PORT', 10000))
    print(f"✅ Port set to: {port}", flush=True)
    
except Exception as e:
    print(f"❌ Error during startup: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    print("Running with Flask dev server", flush=True)
    app.run(debug=False, host='0.0.0.0', port=port)