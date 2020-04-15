# Whatsapp RTU Result Server
This server delivers RTU result to whatsapp clients
```
Note that currently it only works in Whatsapp Business
```

## Prerequisite
#### For windows
Download this setup[https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_msvc2015-win64.exe] and install *wkhtmltox.exe* using default configurations.
Now add the the location "*C:\Program Files\wkhtmltopdf\bin*" to the *PATH* in Environmental Variables

#### For Linux users
Run the command in terminal
```
sudo apt-get install wkhtmltopdf
```

## Whatsapp Configurations
On your android or ios device on which whatsapp business is installed, *disable* the *permission* to whatsapp to *read the contacts*
```
This is done to get only mobile numbers in the chat as they are more formatted
```

## Starting the Server
On Windows, Execute the *whatsapp_result_server.exe* and give all the permissions required

On Linux, open terminal and navigate to the project directory and run the command:
```
chmod +x whatsapp_result_server
./whatsapp_result_server
```

## Next Step
Google chrome will start and you will see whatsapp login QR Code. Just scan the code and you are ready to serve

## Testing
Just message any RTU roll number to get his/her result of 'BTECH IV SEM MAIN 2019'

## Thank You
