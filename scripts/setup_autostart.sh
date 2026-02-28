#!/bin/bash
# scripts/setup_autostart.sh
# Run this once on the Pi to configure SentinelPi to launch on boot.
# When you close the app, the normal desktop (LXDE/Openbox) starts.
#
# Usage: bash scripts/setup_autostart.sh

set -e

APP_DIR="/home/rpi/SentinelPi"
VENV_PYTHON="$APP_DIR/venv/bin/python3"
USER="rpi"

echo "=== SentinelPi Autostart Setup ==="

# ── Step 1: Enable console autologin (no desktop on boot) ────────────────────
# This makes the Pi boot to a terminal logged in as 'rpi', not the desktop.
sudo raspi-config nonint do_boot_behaviour B1   # Boot to CLI, autologin

# ── Step 2: Install onscreen keyboard ────────────────────────────────────────
echo "[*] Installing matchbox-keyboard..."
sudo apt install -y matchbox-keyboard

# ── Step 3: Create the launcher script ───────────────────────────────────────
# This script is what .bashrc will call on login.
# It starts the GUI. When the GUI closes, it launches the desktop.

cat > "$APP_DIR/scripts/launch.sh" << 'LAUNCH'
#!/bin/bash
# Launched automatically on login.
# Starts SentinelPi fullscreen. When closed, opens the desktop.

export DISPLAY=:0
export XAUTHORITY=/home/rpi/.Xauthority

# Start a minimal X session in the background so Qt has a display
if ! pgrep -x Xorg > /dev/null; then
    startx &
    sleep 3   # wait for X to be ready
fi

cd /home/rpi/SentinelPi
source venv/bin/activate

echo "Starting SentinelPi..."
python3 main.py

# ── App was closed — now launch the normal desktop ────────────────────
echo "SentinelPi closed. Starting desktop..."
# Kill the bare X session and start the full desktop
pkill Xorg 2>/dev/null || true
sleep 1
startx /usr/bin/openbox-session   # change to 'lxsession' if you use LXDE
LAUNCH

chmod +x "$APP_DIR/scripts/launch.sh"

# ── Step 4: Add launcher call to .bashrc ─────────────────────────────────────
# Only runs when logging in on tty1 (the physical screen), not SSH.
BASHRC="/home/$USER/.bashrc"
MARKER="# SentinelPi autostart"

if ! grep -q "$MARKER" "$BASHRC"; then
    cat >> "$BASHRC" << 'BASHEOF'

# SentinelPi autostart
# Only runs on the physical display (tty1), not over SSH
if [ "$(tty)" = "/dev/tty1" ]; then
    bash /home/rpi/SentinelPi/scripts/launch.sh
fi
BASHEOF
    echo "[*] Added autostart to .bashrc"
else
    echo "[*] Autostart already in .bashrc, skipping."
fi

echo ""
echo "=== Done ==="
echo "Reboot to test: sudo reboot"
echo ""
echo "To undo autostart, remove the SentinelPi block from ~/.bashrc"
echo "and run: sudo raspi-config nonint do_boot_behaviour B4  (boot to desktop)"
