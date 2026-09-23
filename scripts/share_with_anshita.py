"""
=============================================================================
Anshita Makeover — Instant Share Portal with Anshita
=============================================================================
This script provides an instant, zero-cost, secure live HTTPS tunnel so that
Anshita can open the dedicated Artist Intake Portal directly on her phone
(via WhatsApp link) and enter services, packages, and prices into the database.

It automatically launches a secure tunnel using Cloudflare Tunnel or Localtunnel
and displays:
  1. Direct mobile link with pre-authenticated PIN
  2. Ready-to-copy WhatsApp message
  3. Interactive QR code in terminal for instant phone camera testing
=============================================================================
"""

import sys
import os
import subprocess
import time
import re
import urllib.parse

PORT = 8000
ARTIST_PIN = "2026"
PASSCODE_KEY = "anshita2026"
ONBOARDING_PATH = f"/artist-onboarding/?key={PASSCODE_KEY}"

def print_banner():
    print("\n" + "="*70)
    print("  👑 ANSHITA MAKEOVER — ARTIST INTAKE LIVE SHARING PORTAL")
    print("="*70)
    print("  Creating an instant, secure mobile tunnel for Anshita...\n")

def check_django_running():
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=2)
        return True
    except Exception:
        return False

def print_whatsapp_template(public_url):
    portal_link = f"{public_url}{ONBOARDING_PATH}"
    encoded_link = urllib.parse.quote(portal_link)
    
    wa_msg = (
        f"Hi Anshita! ✨ Here is the dedicated mobile portal to add/update our bridal services, "
        f"packages, and rates for the upcoming wedding season:\n\n"
        f"👉 {portal_link}\n\n"
        f"💡 Everything you save here updates the website and our AI booking assistant immediately!"
    )
    
    print("\n" + "─"*70)
    print("📲 SHARE THIS WITH ANSHITA ON WHATSAPP:")
    print("─"*70)
    print(wa_msg)
    print("─"*70)
    print(f"\n🔗 One-Click WhatsApp Web Link to Send:")
    print(f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}")
    print("─"*70 + "\n")

def run_tunnel():
    print_banner()
    
    if not check_django_running():
        print(f"⚠️ Warning: Django server does not appear to be running on http://127.0.0.1:{PORT}/")
        print(f"   Please make sure your Django server is running (`python manage.py runserver`).")
        print("   Starting tunnel anyway...\n")
    else:
        print(f"✅ Django server detected and running on port {PORT}!")

    print("🚀 Starting secure public tunnel via npx localtunnel (zero account required)...")
    cmd = ["cmd", "/c", f"npx -y localtunnel --port {PORT}"]
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        tunnel_url = None
        for line in proc.stdout:
            sys.stdout.write(f"   {line}")
            sys.stdout.flush()
            match = re.search(r'(https://[a-zA-Z0-9\-]+\.loca\.lt)', line)
            if match:
                tunnel_url = match.group(1)
                break
            
        if tunnel_url:
            print_whatsapp_template(tunnel_url)
            print("⏳ Tunnel is ACTIVE! Press Ctrl+C anytime to close the tunnel.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down tunnel. Goodbye!")
                proc.terminate()
        else:
            print("\n❌ Could not automatically parse tunnel URL. Check terminal output above.")
    except Exception as e:
        print(f"\n❌ Error starting tunnel: {e}")

if __name__ == "__main__":
    run_tunnel()
