"""
run.py – Start CampusConnect.

Usage:
    python run.py              # Flask dev server (demo only)
    python run.py --waitress   # Waitress WSGI server (more stable for demos)

Networking concept:
- HOST = 0.0.0.0 means "bind to ALL network interfaces".
  This makes the app reachable from any device on the same Wi-Fi.
- PORT = 5000 is the TCP port number other devices use in the URL.
- The startup banner prints the LAN URL so you can tell students
  which address to type.
"""
import argparse
import sys
from app import create_app
from app.utils import get_lan_ip, get_all_lan_ips
from config import Config

app = create_app()


def print_banner(host: str, port: int):
    lan_ip = get_lan_ip()
    all_ips = get_all_lan_ips()

    print("=" * 60)
    print("  CampusConnect – Offline LAN Academic Platform")
    print("=" * 60)
    print(f"  Local URL   : http://127.0.0.1:{port}")
    print(f"  LAN URL     : http://{lan_ip}:{port}")
    if len(all_ips) > 1:
        print("  Other IPs   :", ", ".join(f"http://{ip}:{port}" for ip in all_ips))
    print()
    print("  Open on other devices:")
    print(f"  → http://{lan_ip}:{port}")
    print()
    print("  Press CTRL+C to stop.")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CampusConnect")
    parser.add_argument("--waitress", action="store_true",
                        help="Use Waitress WSGI server instead of Flask dev server")
    args = parser.parse_args()

    host = Config.HOST
    port = Config.PORT

    print_banner(host, port)

    if args.waitress:
        try:
            from waitress import serve
            print("  Using Waitress WSGI server.")
            serve(app, host=host, port=port, threads=8)
        except ImportError:
            print("Waitress not installed. Run: pip install waitress")
            sys.exit(1)
    else:
        print("  Using Flask development server (demo/classroom use only).")
        # debug=False always; threaded=True for concurrent students
        app.run(host=host, port=port, debug=False, threaded=True)
