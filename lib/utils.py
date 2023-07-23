import datetime, requests, logging, json
from pytz import timezone


def createTimeArray(initDate: datetime.datetime, minimumHour: int, maximumHour: int):
    initDate = initDate.replace(hour=minimumHour, minute=0, second=0, microsecond=0)
    timeIterative = initDate

    times = []
    for i in range(7):  # For each day in the week
        timeIterative = initDate + datetime.timedelta(days=i)
        for i in range(maximumHour - minimumHour):  # For each hour in the day
            logging.debug(f"TimeIterative: " + str(timeIterative))
            times.append(
                timeIterative.astimezone(datetime.timezone.utc).strftime("%H00-%d%m%Y")
            )
            timeIterative += datetime.timedelta(hours=1)
    return times


# Creates the Crab.Fit and Returns the API Response
async def createCrabFit(
    title: str = "",
    minimumHour: int = 9,
    maximumHour: int = 22,
    localTz: str = "America/Los_Angeles",
    initDate: datetime = (datetime.datetime.today() + datetime.timedelta(days=1)),
) -> requests.Response:
    logging.info("Beginning Crab.fit request build with title: '" + title + "'")
    logging.debug("Initial date parameter: " + str(initDate))

    # Build Crab.fit Information
    initDate = initDate.astimezone(
        timezone(localTz)
    )  # Failsafe if datetime is not passed in correct TZ
    logging.debug("Building time array with init datetime " + str(initDate))

    # API Call for Crab.fit
    payload = json.dumps(
        {
            "name": f"{title} {initDate.strftime('%m/%d')}-{(initDate + datetime.timedelta(days=6)).strftime('%m/%d')}",
            "times": createTimeArray(
                initDate=initDate, minimumHour=minimumHour, maximumHour=maximumHour
            ),
            "timezone": localTz,
        }
    )
    logging.debug(
        "Sending Crab.fit API request with the following data: " + str(payload)
    )
    response = requests.request(
        "POST",
        "https://api.crab.fit/event",
        headers={"Content-Type": "application/json"},
        data=payload,
    )

    return response
