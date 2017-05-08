import subprocess
from time import sleep
from threading import Thread
import json
import io

with open('config.json') as data_file:
    config = json.load(data_file)

# Sleep once right when this script is called to give the Pi enough time
# to connect to the network
sleep(5)

# Some arrays to help minimize streaming and account for devices
# disappearing from the network when asleep
firstRun = [1] * len(config['users'])
presentSent = [0] * len(config['users'])
notPresentSent = [0] * len(config['users'])
counter = [0] * len(config['users'])

# Function that checks for device presence
def whosHere(i):

    # 30 second pause to allow main thread to finish arp-scan and populate output
    sleep(5)

    # Loop through checking for devices and counting if they're not present
    while True:

        # Exits thread if Keyboard Interrupt occurs
        if stop == True:
            print "Exiting Thread"
            exit()
        else:
            pass

        # If a listed device address is present print and stream
        if config['users'][i]["mac"] in output:
            print( config['users'][i]["name"] + "'s device is connected to your network" )

            if config['users'][i]["present"] == "false":
                # Stream that device is present
                config['users'][i]["present"] = "true"

                with open('config.json', 'w') as data_file:
                    json.dump( config, data_file )
                
                print( config['users'][i]["name"] + " present streamed" )
                # Reset counters so another stream isn't sent if the device
                # is still present
                counter[i] = 0
                sleep(900)
            else:
                # If a stream's already been sent, just wait for 15 minutes
                counter[i] = 0
                sleep(900)
        # If a listed device address is not present, print and stream
        else:
            print( config['users'][i]["name"] + "'s device is not present" )
            # Only consider a device offline if it's counter has reached 30
            # This is the same as 15 minutes passing
            if counter[i] == 30:
                if config['users'][i]["present"] == "true":
                    # Stream that device is not present
                    config['users'][i]["present"] = "false"
                    
                    with open('config.json', 'w') as data_file:
                        json.dump( config, data_file )

                    print( config['users'][i]["name"] + " not present streamed" )

                    # Reset counters so another stream isn't sent if the device
                    # is still present
                    counter[i] = 0
                else:
                    # If a stream's already been sent, wait 30 seconds
                    counter[i] = 0
                    sleep(30)
            # Count how many 30 second intervals have happened since the device 
            # disappeared from the network
            else:
                counter[i] = counter[i] + 1
                print( config['users'][i]["name"] + "'s counter at " + str(counter[i]) )
                sleep(30)


# Main thread

try:

    # Initialize a variable to trigger threads to exit when True
    global stop
    stop = False

    # Start the thread(s)
    # It will start as many threads as there are values in the users array
    for i in range(len(config['users'])):
        t = Thread(target=whosHere, args=(i,))
        t.start()

    while True:
        # Make output global so the threads can see it
        global output
        # Assign list of devices on the network to "output"
        output = subprocess.check_output("sudo arp-scan -l", shell=True)
        # Wait 30 seconds between scans
        sleep(30)

except KeyboardInterrupt:
    # On a keyboard interrupt signal threads to exit
    stop = True
    exit()
