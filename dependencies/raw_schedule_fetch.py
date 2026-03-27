import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup

from usarby.settings import MAIN_URL


# TODO properly implement try/except block in future updates
# Initialize the session
try:
    session = requests.Session()
except ConnectionError:
    session = None
    print("Sorry, but the service isn't available at the moment.")

# Get the home page (for cookies + csrf)
r = session.get(MAIN_URL)


def get_csrf():
    """Get CSRF token from the main url"""
    soup: BeautifulSoup = BeautifulSoup(r.text, "html.parser")
    csrf: str = soup.find("meta", {"name": "csrf-token"})["content"]
    return csrf


def get_raw_schedule_data(your_group_name: str, semester: int = 1, university_week: int = 1, debug: bool = False):
    """
    Fetches raw lesson data for a specific group and time period.

    Args:
        your_group_name (str): The name of the student group.
        semester (int, optional): The academic semester. Defaults to 1.
        university_week (int, optional): The specific week number. Defaults to 1.
        debug (bool, optional): If True, enables debug logging. Defaults to False.

    Raises:
        ValueError: If the response cannot be decoded as JSON.

    Returns:
        dict: A JSON-decoded dictionary containing lesson information.
    """
    # Get CSRF token
    csrf = get_csrf()

    # Get the group ID by name
    group_id = _get_group_id_by_group_name(your_group_name, csrf)
    
    # Prepare POST data
    schedule_payload = {
        "_csrf": csrf,
        "gr": group_id,
        "sem": semester,
        "day": 7, # Only the frontend needs that.
        "week": university_week,
        "grName": f"{your_group_name}"
    }
    
    # Get lessons data
    try:
        r_lessons = _get_lessons_data(schedule_payload, debug=debug)
        return r_lessons
    except Exception as e:
        # Raise error
        raise ValueError("Couldn't decode the JSON or find any data, check the input data.") from e
    
    
def _get_group_id_by_group_name(group_name: str, csrf: str, debug: bool = False) -> str | None:
    r"""Get group ID by User's group name

    Args:
        group_name (str): Group name (e.g. IT11Z)
        csrf (str): CSRF Token
        debug (bool, optional): Toggle debug. Defaults to False.

    Returns:
        str or None: Group (str) or None
    """

    # Get URL
    url_groups = f"{MAIN_URL}/api/getGroups"
    
    # Prepare POST data
    payload = {
        "_csrf": csrf,
    }
    
    # POST to get groups
    r_groups = session.post(url_groups, data=payload)

    # Debugging
    if debug:
        print("Status groups:", r_groups.status_code)
        print("Response groups:", r_groups.json())
    
    # Get the group ID from the response
    for group in r_groups.json():
        if group["Denumire"] == group_name:
            return group["Id"]

    # If the group is not found, return None
    return None


# Get the user's lessons
def _get_lessons_data(payload: dict, debug: bool = False):
    """Get lessons data (payload) in json

    Args:
        payload (dict): Schedule payload
        debug (bool, optional): Toggle debug. Defaults to False.

    Returns:
        r_lessons: lessons in json
    """
    # Get URL
    url_lessons = f"{MAIN_URL}/api/getlessons"

    # POST to get lessons
    r_lessons = session.post(url_lessons, data=payload)

    # Debugging
    if debug:
        print("Status lessons:", r_lessons.status_code)
        print("Response lessons:", r_lessons.json())
    
    # Return the lessons
    return r_lessons.json()


# Local test
if __name__ == "__main__":
    get_raw_schedule_data("IT11Z", university_week=11, debug=True)