# CampusConnect – Viva Question Bank

---

## Networking Concepts

**Q: What is an IP address?**
A: A unique numerical label assigned to every device on a network, used to route
packets to the correct destination. Example: `192.168.1.42`. In our project the
server's LAN IP is printed on startup and shared with students.

**Q: What is the difference between 127.0.0.1, 0.0.0.0, and the LAN IP?**
A: `127.0.0.1` (localhost) is the loopback address — only the same machine can
reach it. `0.0.0.0` is a special bind address meaning "listen on ALL interfaces",
so other devices on the LAN can connect. The LAN IP (e.g. `192.168.1.42`) is
what we print in the startup banner and share with students.
In `run.py` we bind to `0.0.0.0:5000`, which is why the app is reachable from
other devices.

**Q: What is a port number?**
A: A 16-bit number (0–65535) that identifies which application on a device a
connection is meant for. HTTP normally uses port 80. We use port 5000. When a
student types `http://192.168.1.42:5000`, the `:5000` tells their browser to
connect to that port.

**Q: What is TCP?**
A: Transmission Control Protocol. It guarantees that data arrives in order,
without errors or missing pieces, by using acknowledgements and retransmission.
HTTP (which carries our web pages) runs on top of TCP.

**Q: What is a socket?**
A: A socket is one endpoint of a two-way communication link (TCP connection).
Flask calls `socket.bind(('0.0.0.0', 5000))` to create a listening socket.
When a student's browser connects, the OS creates a new socket for that
conversation.

**Q: What is HTTP?**
A: Hypertext Transfer Protocol. The application-layer protocol browsers use to
request and receive web pages. A request looks like:
```
GET /login HTTP/1.1
Host: 192.168.1.42:5000
```
The server responds with:
```
HTTP/1.1 200 OK
Content-Type: text/html
...page HTML...
```

**Q: What is the request-response cycle?**
A: 1. Browser opens a TCP connection to the server. 2. Browser sends an HTTP
request (method, path, headers, optional body). 3. Flask receives it, runs the
view function, renders a template. 4. Flask sends an HTTP response (status code,
headers, body). 5. Browser renders the HTML.

**Q: What is a subnet? What does the subnet mask mean?**
A: A subnet is a logical subdivision of an IP network. The subnet mask
(e.g. `255.255.255.0` or `/24`) tells devices which part of an IP address is the
network and which is the host. Devices on the same subnet can communicate
directly without a router.

**Q: What is the default gateway?**
A: The router's IP address. Traffic destined for another subnet is sent to the
gateway. For our LAN demo, all traffic stays within the subnet — no gateway needed.

---

## Project-specific

**Q: Why does the server bind to 0.0.0.0?**
A: Binding to `0.0.0.0` tells the OS to accept connections on every network
interface — Wi-Fi, Ethernet, hotspot. If we bound to `127.0.0.1`, only the
server laptop itself could access the app.

**Q: How do you find the server's LAN IP?**
A: `ipconfig` on Windows shows all adapters. We also detect it programmatically
with a UDP socket trick in `utils.py:get_lan_ip()` — we "connect" a UDP socket
to `10.254.254.254:1`, which makes the OS choose the outgoing interface without
sending any packet, then we read the local address from the socket.

**Q: What is a firewall? Why do we need to add a rule?**
A: A firewall filters incoming and outgoing network traffic. Windows Firewall
blocks port 5000 by default. We add a rule that allows TCP port 5000 inbound on
the Private profile, restricted to LocalSubnet — meaning only devices on the same
LAN can connect. We never disable the firewall entirely.

**Q: What is Wi-Fi client isolation (AP isolation)?**
A: A setting on some wireless routers/hotspots that prevents devices connected
to the same Wi-Fi from communicating with each other — they can only reach the
internet. This breaks our LAN demo. The fix is to use Windows Mobile Hotspot,
which does not have this restriction.

**Q: Why are passwords hashed?**
A: If the SQLite database file is ever accessed by someone, plain-text passwords
would be exposed. Hashing (we use pbkdf2:sha256 via Werkzeug) is a one-way
transformation — you can verify a password but cannot reverse the hash to get the
original. Even the server never knows the plain-text password after it's stored.

**Q: How is the quiz timer enforced securely?**
A: The browser shows a countdown using JavaScript. But a student could disable JS
or fake the submit time. Our defence: when the attempt is created, `started_at` is
recorded in the database by the server. On submission, the server checks:
`submitted_at ≤ started_at + duration + 10s grace`. If the student is too late,
the submission is accepted but the server records it. The score is always computed
server-side from the DB data — the browser never receives `correct_option`.

**Q: What is CSRF and how do you prevent it?**
A: Cross-Site Request Forgery tricks a logged-in user's browser into submitting
a form to your site from another site. We prevent it with Flask-WTF: every POST
form includes a hidden `csrf_token` field generated by the server. The server
validates this token before processing the request.

**Q: What is the difference between role-based access and authentication?**
A: Authentication answers "who are you?" (login). Authorisation answers "what
are you allowed to do?" (role check). Our `@teacher_required` and
`@student_required` decorators enforce authorisation after Flask-Login handles
authentication.

**Q: Why is the Flask development server not suitable for production?**
A: It is single-threaded (unless `threaded=True`), not hardened against malformed
requests, and not optimised for concurrent connections. We use Waitress for more
stability. For a real production deployment, Nginx + Gunicorn would be typical.
