import os
import logging
import json
import getpass
import datetime
import requests
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
from garth.exc import GarthHTTPError
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError
)

# Configure debug logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

today = datetime.date.today()
startdate = today - datetime.timedelta(days=2)  # Select 2 days back
startdate = "2020-01-01"
# Load environment variables if defined
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
api = None

def get_credentials():
    """Get user credentials."""

    email = input("Login e-mail: ")
    password = getpass("Enter password: ")

    return email, password

def display_json(api_call, output):
    """Format API output for better readability."""

    dashed = "-" * 20
    header = f"{dashed} {api_call} {dashed}"
    footer = "-" * len(header)

    print(header)

    if isinstance(output, (int, str, dict, list)):
        print(json.dumps(output, indent=4))
    else:
        print(output)

    print(footer)

def init_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        print(
            f"Trying to login to Garmin Connect using token data from '{tokenstore}'...\n"
        )
        garmin = Garmin()
        garmin.login(tokenstore)
    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            # Ask for credentials if not set as environment variables
            if not email or not password:
                email, password = get_credentials()

            garmin = Garmin(email, password)
            garmin.login()
            # Save tokens for next login
            garmin.garth.dump(tokenstore)

        except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError, requests.exceptions.HTTPError) as err:
            logger.error(err)
            return None

    return garmin

def get_all_weights(api):
    # display_json(
    #     f"api.get_weigh_ins({startdate.isoformat()}, {today.isoformat()})",
    #     api.get_weigh_ins(startdate.isoformat(), today.isoformat())
    # )
    output = api.get_weigh_ins(startdate, today.isoformat())
    y = []
    x_ = 0
    x = []
    
    for day in output['dailyWeightSummaries'][::-1]:
        if day['latestWeight']:
            weight = day['latestWeight']['weight']
            y.append(weight/1000)
            x.append(x_)
        x_ = x_ + 1
    print("len(y) " + str(len(y)))
    print("len(x) " + str(len(x)))

    print("##############")
    print(y[-1])
    print(output['dailyWeightSummaries'][-1])
    # make data
    # x = np.linspace(0, 10, 100)
    # y = 4 + 2 * np.sin(2 * x)
    # print(y)

    # x = np.linspace(0, 10, 100)
    plt.style.use('_mpl-gallery')    
    # plot
    fig, ax = plt.subplots()    
    ax.plot(x, y, linewidth=2.0)

    # ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
    #     ylim=(0, 8), yticks=np.arange(1, 8))
    plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9)

    plt.show()



if __name__ == "__main__":
    api = init_api(email, password)
    get_all_weights(api)
    print("Hello, World!")