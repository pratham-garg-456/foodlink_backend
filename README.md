# Installation guide and Setup for Backend

## Pre-requisite 
- Install python: https://www.python.org/downloads/
  (command to check if you have python already installed: `which python3`)

Usually, pip is automatically installed if you are:
  
  - Working in a virtual environment
  - Using Python downloaded from python.org
  - Using Python that has not been modified by a redistributor to remove ensurepip

 if not, then
- Install pip: https://pip.pypa.io/en/stable/installation/
  


## Setup up project locally:
- Clone the repository 
- Set up a virtual environment, so that we keep abstraction between the application and our local machine (whatever we install will not affect our local machine)
  
  ```bash
  # Create Virtual Environment 
  python3 -m venv venv

  # Platform-Specific Commands for activation
    
    ## Window
    venv\Scripts\Activate.ps1 (powershell)
  
    ## mac/linux
    source venv/bin/activate

  #install the dependencies in your virtual environment 
  python3 -m pip install -r requirements.txt

  #deactive the virtual environment
  deactivate
  ```

## Run the Project in Development mode 
```sh
fastapi dev
```



  
