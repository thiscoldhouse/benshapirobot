mkdir -p /usr/src/venv
virtualenv --python $(which python3) /usr/src/venv/benshapirobot

cat > /etc/systemd/system/benshapirobot.service <<EOM
[Unit]
Description=Ben's Happy Bot
After=network.target

[Service]
Type=simple
User=tad
WorkingDirectory=/usr/src/benshapirobot
ExecStart=/usr/src/venv/benshapirobot/bin/python /usr/src/benshapirobot/main.py
StandardOutput=syslog
StandardError=syslog
Restart=always

[Install]
WantedBy=multi-user.target
EOM

systemctl enable /etc/systemd/system/benshapirobot.service
