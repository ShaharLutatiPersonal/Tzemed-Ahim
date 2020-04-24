# Tzemed Ahim
## Shahar Lutati
# Introduction 
In this project our goal is to estimate the probability of exposure of one personal to another within 2 meter range within 10 minutes.
We decided to use BT bracelets as the transmitter and apply a statistical method (using quantile hypothesis) to determine whether the phone "sees" the bracelet.

The data using the echoless chamber was collected by using a special BT reciever written in c++ on ESP32 transciever.
Other data was collected using Samsung Galaxy S7.

## Apps in ./src
1. server.py - an HTTP server that collect and save beacons from mobile phones through the internet.
2. serial_EcholessChamber.py - a recording app specially written for the echoless chamber with 
serial interface to the BT reciever.
3. process_csv.py - post processing tool for analyzing the data from mobile phones collected by "server.py".
4. process_db.py - post processing tool for analyzing the DB collected during all measurements.