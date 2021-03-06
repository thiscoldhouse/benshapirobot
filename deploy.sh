set -e

echo "Cloning fresh repo, this may require your git password\n"
cd /tmp
git clone https://github.com/thiscoldhouse/benshapirobot.git
cd -
cp secrets.py /tmp/benshapirobot/

# send the new artifact to the servers
echo "Sending deploy to $hostname"
rm -rf /tmp/benshapirobot/.git
scp -r /tmp/benshapirobot/ tad@tucker.ai:/tmp
rm -rf /tmp/benshapirobot/
ssh -t tad@tucker.ai "
                   mv /usr/src/benshapirobot/reddit_config.json /tmp/ &&
                   rm -rf /usr/src/benshapirobot/* &&
                   mv /tmp/benshapirobot/* /usr/src/benshapirobot/ &&
                   rm -rf /tmp/benshapirobot/ &&
                   /usr/src/venv/benshapirobot/bin/pip install -r /usr/src/benshapirobot/requirements.txt    &&
                   mv /tmp/reddit_config.json /usr/src/benshapirobot/  &&
                   sudo /bin/systemctl daemon-reload &&
                   sudo /bin/systemctl restart benshapirobot &&
                   sudo /bin/systemctl status benshapirobot"
echo "Done"
