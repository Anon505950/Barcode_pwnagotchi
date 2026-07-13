#!/bin/bash

# This is a daemon script for PiSugarS To use the side BUTTON (not scwitch) as a power on/off

# During runtime it treats it as a GPIO which we can use to execute system commands

# When off this button restores the pi battery acting as a hardware switch, not software

#save to /usr/local/bin/PiSugarS_Custom.sh
#make exec: sudo chmod +x /usr/local/bin/PiSugarS_Custom.sh
#create service file: sudo nano /etc/systemd/system/PiSugarS_Custom.service
#Service file:

#[Unit]
#Description=PiSugar-S Shutdown Button
#After=multi-user.target

#[Service]
#ExecStart=/usr/local/bin/PiSugarS_Custom.sh
#Restart=always
#User=root

#[Install]
#WantedBy=multi-user.target


#enable the service: sudo systemctl enable PiSugarS_Custom.service && sudo systemctl start PiSugarS_Custom.service

#(optional) verify it's running: systemctl status PiSugarS_Custom.service




# Disable I2C (PiSugar-S requires GPIO3 free)
sudo raspi-config nonint do_i2c 0

# Export GPIO3
echo 3 | sudo tee /sys/class/gpio/export

# Set direction
echo in | sudo tee /sys/class/gpio/gpio3/direction

# Monitor button
while true; do
    sleep 0.1
    ButtonValue=$(cat /sys/class/gpio/gpio3/value)

    if [ "$ButtonValue" == "0" ]; then
        count=0

        while [ "$ButtonValue" == "0" ]; do
            ((count++))
            ButtonValue=$(cat /sys/class/gpio/gpio3/value)
            sleep 0.001
        done

        # Long press → shutdown
        if [ $count -gt 50 ]; then
            sudo shutdown -h now
        fi
    fi
done

