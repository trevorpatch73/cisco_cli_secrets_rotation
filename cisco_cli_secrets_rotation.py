import csv
import random
import string
from getpass import getpass
from netmiko import ConnectHandler

# Global Variables
break_glass_account_name = 'admin'

# Prompt user for Netmiko credentials
username = input("Enter Netmiko username: ")
password = getpass("Enter Netmiko password: ")

# Prompt user for password requirements
length = int(input("Enter the desired length of the password: "))
special_chars = input("Enter the special characters to include (leave empty for no special characters): ")

# Generate a random password
characters = string.ascii_letters + string.digits + special_chars
new_password = ''.join(random.choice(characters) for _ in range(length))

# Define the CSV file path
csv_file = 'device_inventory.csv'

# Initialize a list to store the device names and corresponding password change status
password_changes = []

# Open the CSV file and iterate through each device
with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        device = {
            'device_type': row['DEVICE_OS'],
            'ip': row['DEVICE_IP_ADDRESS'],
            'username': username,
            'password': password,
            'secret': password,
        }

        # Connect to the device
        try:
            net_connect = ConnectHandler(**device)
            print(f"\nLogging into {row['DEVICE_NAME']} ({row['DEVICE_MODEL']}) device at {row['DEVICE_IP_ADDRESS']}")

            # Change the password based on device type
            if device['device_type'] == 'IOS':
                commands = [
                    'configure terminal',
                    'username {} secret 5 {}'.format(break_glass_account_name,new_password)
                ]

                # Send the configuration commands
                output = net_connect.send_config_set(commands)
                net_connect.disconnect()
                
                # Log the Results
                if 'Invalid command' in output:
                    password_changes.append((row['DEVICE_NAME'], False))
                    print(f"Password change failed for {row['DEVICE_NAME']}")
                else:
                    password_changes.append((row['DEVICE_NAME'], True))
                    print(f"Password change successful for {row['DEVICE_NAME']}")

            elif device['device_type'] == 'IOS-XE':
                commands = [
                    'configure terminal',
                    'username {} privilege 15 secret 5 {}'.format(break_glass_account_name,new_password)
                ]

                # Send the configuration commands
                output = net_connect.send_config_set(commands)
                net_connect.disconnect()

                # Log the Results
                if 'Invalid command' in output:
                    password_changes.append((row['DEVICE_NAME'], False))
                    print(f"Password change failed for {row['DEVICE_NAME']}")
                else:
                    password_changes.append((row['DEVICE_NAME'], True))
                    print(f"Password change successful for {row['DEVICE_NAME']}")

            elif device['device_type'] == 'NX-OS':
                commands = [
                    'configure terminal',
                    'username {} password 5 {}'.format(break_glass_account_name,new_password)
                ]
                
                # Send the configuration commands
                output = net_connect.send_config_set(commands)
                net_connect.disconnect()

                # Log the Results
                if 'ERROR:' in output:
                    password_changes.append((row['DEVICE_NAME'], False))
                    print(f"Password change failed for {row['DEVICE_NAME']}")
                else:
                    password_changes.append((row['DEVICE_NAME'], True))
                    print(f"Password change successful for {row['DEVICE_NAME']}")

            elif device['device_type'] == 'ASA':
                commands = [
                    'enable',
                    'config t',
                    'username {} password {}'.format(break_glass_account_name,new_password)
                ]

                # Send the configuration commands
                output = net_connect.send_config_set(commands)
                net_connect.disconnect()

                # Log the Results
                if 'ERROR:' in output:
                    password_changes.append((row['DEVICE_NAME'], False))
                    print(f"Password change failed for {row['DEVICE_NAME']}")
                else:
                    password_changes.append((row['DEVICE_NAME'], True))
                    print(f"Password change successful for {row['DEVICE_NAME']}")                

            elif device['device_type'] == 'FXOS':
                commands = [
                    'scope security',
                    'scope local-user',
                    'set-password {} {}'.format(break_glass_account_name,new_password)
                ]

                # Send the configuration commands
                output = net_connect.send_config_set(commands)
                net_connect.disconnect()

                # Log the Results
                if 'ERROR:' in output:
                    password_changes.append((row['DEVICE_NAME'], False))
                    print(f"Password change failed for {row['DEVICE_NAME']}")
                else:
                    password_changes.append((row['DEVICE_NAME'], True))
                    print(f"Password change successful for {row['DEVICE_NAME']}")

            else:
                print(f"Unsupported device type for Netmiko Actions: {device['device_type']}")
                continue            

        except Exception as e:
            password_changes.append((row['DEVICE_NAME'], False))
            print(f"Failed to connect to {row['DEVICE_NAME']} ({row['DEVICE_MODEL']}). Error: {str(e)}")

# Print the final password applied to all devices
print(f"\nFinal password applied to all Cisco devices: {new_password}")

# Print the password change status for each device
print("\nPassword change status:")
for device_name, status in password_changes:
    print(f"Device Name: {device_name}, Status: {'Success' if status else 'Failed'}")
