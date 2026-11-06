# Yard song picker

The touchscreen runs Chromium in kiosk mode at http://127.0.0.1:8795/.
The server reads the configured FPP playlist and live status. It only offers
songs also marked requestable by the public show catalog. Confirmed requests
use the same queue API as the show website.

On the console, edit `~/yard-song-picker/config.json` to set `master` to the
FPP base URL and `playlist` to its exact show playlist name. Restart the
picker with `systemctl --user restart yard-song-picker.service`. Keep the
website catalog in sync when changing seasons.

The service starts with the desktop user's session. The desktop autostart
entry opens Chromium. The browser and server communicate over loopback.

## Install on another Pi

Use Raspberry Pi OS 64-bit with Desktop and a Wayland desktop session. Enable
desktop auto-login for the kiosk account. Run these commands from this folder
as that account. The service and browser start under the same user.

```sh
sudo apt install chromium python3 curl ffmpeg
mkdir -p ~/yard-song-picker ~/.config/systemd/user ~/.config/autostart
install -m 644 server.py index.html pip.js start-kiosk.sh ~/yard-song-picker/
test -e ~/yard-song-picker/config.json || install -m 644 config.json ~/yard-song-picker/
install -m 644 yard-song-picker.service ~/.config/systemd/user/
install -m 644 yard-song-picker.desktop ~/.config/autostart/
systemctl --user daemon-reload
systemctl --user enable --now yard-song-picker.service
```

Set the Master address and playlist as described above. Log out and back in
to start the kiosk, or run `sh ~/yard-song-picker/start-kiosk.sh` from a
terminal on the desktop. Select HDMI as the default audio output and the
webcam as the default microphone. Chromium may ask for microphone permission
on the first chat.

Pip needs a SpaceXSI API key. Save it as `XAI_API_KEY=...` in
`~/.config/yard-song-picker/voice.env`, restrict the file to mode 600,
then restart the service. Keep this file outside the repository. The camera
preview currently matches the j5create 360 camera by its Linux device name.
