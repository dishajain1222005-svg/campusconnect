"""
network/routes.py – Network status page.

What it shows (and what it does NOT show):
- Server's LAN IP, port, uptime, request count since start.
- Number of authenticated CampusConnect sessions active in the last 5 minutes.
- Recent activity log entries.
- The current client's IP address.

What it does NOT do:
- It does NOT scan the network.
- It does NOT list all Wi-Fi devices.
- It shows CampusConnect session activity only.

Networking concept: We detect the server's LAN IP using a UDP socket trick
(no packets sent).  The 'uptime' is computed from a module-level start_time
variable set when the app starts.
"""
import time
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, ActivityLog
from app.utils import get_lan_ip, get_all_lan_ips

network_bp = Blueprint("network", __name__, url_prefix="/network")

# Module-level start time and request counter
_start_time = time.time()
_request_count = 0


def increment_request_count():
    global _request_count
    _request_count += 1


@network_bp.route("/")
@login_required
def status():
    increment_request_count()

    lan_ip = get_lan_ip()
    all_ips = get_all_lan_ips()
    port = current_app.config.get("PORT", 5000)
    uptime_seconds = int(time.time() - _start_time)
    uptime_str = _format_uptime(uptime_seconds)

    # Active users: last_seen within the last 5 minutes
    five_min_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=5)
    active_users = User.query.filter(User.last_seen >= five_min_ago).count()

    # Recent activity log
    recent_logs = (ActivityLog.query
                   .order_by(ActivityLog.created_at.desc())
                   .limit(20).all())

    # For students: limited view
    is_teacher = current_user.is_teacher

    return render_template("network/status.html",
                           lan_ip=lan_ip,
                           all_ips=all_ips,
                           port=port,
                           uptime=uptime_str,
                           request_count=_request_count,
                           active_users=active_users,
                           recent_logs=recent_logs,
                           client_ip=request.remote_addr,
                           is_teacher=is_teacher)


def _format_uptime(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s"
