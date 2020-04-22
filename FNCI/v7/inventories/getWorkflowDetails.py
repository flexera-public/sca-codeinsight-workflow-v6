'''
Copyright 2020 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Tue Apr 14 2020
File : getWorkflowDetails.py
'''
import logging
import requests
import sys
import config

logger = logging.getLogger(__name__)

#######################################################################
# If the calling app is a flask app then we can use
# the flask abort function to catch exceptions
# so see if its defined in a common config file
try: 
    FLASKAPP = config.FLASKAPP
except:
    FLASKAPP = False

if FLASKAPP:
    from flask import abort
#######################################################################

FNCI_API = "FNCI Get Workflow Details API"
ENDPOINT_URL = config.BASEURL + "inventories/"

#------------------------------------------------------------------------------------------#
def get_inventory_workflow_details(inventoryId, authToken):
    logger.info("Entering update_inventory_workflow_details")
    
    RESTAPI_URL = ENDPOINT_URL + str(inventoryId) + "/workflows" 
    logger.debug("    RESTAPI_URL: %s" %RESTAPI_URL)
    
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + authToken} 

       
    # Make the REST API call to get the data           
    try:
        response = requests.get(RESTAPI_URL, headers=headers)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        # Connection Error - Is the server up and running?
        abort_message = FNCI_API + " - Error Connecting to FNCI Server - " +  (ENDPOINT_URL).split("codeinsight")[0] # Get rid of everything after codeinsight in url
        logger.error("    %s" %(abort_message))

        if FLASKAPP:         
            # Using error code 500 (Internal Server Error) to cover connection errors
            # in the flask apps
            abort(500, FNCI_API + " - %s" %abort_message) 
        else:
            print(abort_message)
            print("Is the FNCI server running?")
            print("Exiting script")
            sys.exit() 
    except requests.exceptions.RequestException as e: # Catch the exception for the logs but process below
        logger.error(e)
    

    # We at least received a response from FNCI so check the status to see
    # what happened if there was an error or the expected data
    if response.status_code == 200:
        logger.debug("    Call to %s was successful." %FNCI_API)
        logger.info("Inventory Workflow Details Retreived")
        return(response.json()["Workflow Request Details"])
    
    elif response.status_code == 400:
        # Bad Request
        logger.error("    %s - Error: %s -  Bad Request." %(FNCI_API, response.status_code ))
        if FLASKAPP:         
            abort(400, FNCI_API + " - Bad Request - Look at debug log for more details") 
        else:
            print("%s - Error: %s -  Bad Request." %(FNCI_API, response.status_code ))
            print("    Exiting script")
            sys.exit()   

    elif response.status_code == 401:
        # Unauthorized Access
        logger.error("    %s - Error: %s -  Authentication Failed: JWT token is not valid or user does not have correct permissions." %(FNCI_API, response.status_code ))
        if FLASKAPP:         
            abort(401, FNCI_API + " - Authentication Failed: JWT token is not valid or user does not have correct permissions.")
        else:
            print("%s - Error: %s -  Authentication Failed: JWT token is not valid or user does not have correct permissions." %(FNCI_API, response.status_code ))
            print("    Exiting script")
            sys.exit()   

    elif response.status_code == 404:
        # Not Found
        logger.error("    %s - Error: %s -  URL endpoint not found:  %s" %(FNCI_API, response.status_code,  RESTAPI_URL ))
        if FLASKAPP:         
            abort(400, FNCI_API + " - Bad Request - URL endpoint not found") 
        else:
            logger.debug("    %s - Error: %s -  URL endpoint not found:  %s" %(FNCI_API, response.status_code,  RESTAPI_URL ))
            # Assume this request is for details which don't exist yet to just return
            return "Does Not Exist"
               

    elif response.status_code == 405:
        # Method Not Allowed
        logger.error("    %s - Error: %s -  Method (GET/POST/PUT//DELETE/ETC) Not Allowed." %(FNCI_API, response.status_code ))
        if FLASKAPP:         
            abort(405, FNCI_API + " - Method Not Allowed.")
        else:
            print("    %s - Error: %s -  Method (GET/POST/PUT//DELETE/ETC) Not Allowed." %(FNCI_API, response.status_code ))
            print("    Exiting script")
            sys.exit()  
        
    elif response.status_code == 500:
        # Internal Server Error
        logger.error("    %s - Error: %s -  Internal Server Error." %(FNCI_API, response.status_code ))
        if FLASKAPP:         
            abort(500, FNCI_API + " - Internal Server Error.")
        else:
            print("    %s - Error: %s -  Internal Server Error." %(FNCI_API, response.status_code ))
            print("    Exiting script")
            sys.exit()  