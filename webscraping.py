"""
Specific package installation commands:
playwright.sync_api --> "conda config --add channels conda-forge",
                        "conda config --add channels microsoft",
                        "conda install playwright",
                        "playwright install"
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime


class StewpotScraper:
    """
    A class can scrape The Stewpot's website to find the names, dates, addresses, and age restrictions of all available
    volunteering events. The scrape_website() method returns all this information as a single list of dictionaries,
    with each dictionary corresponding to one event, and each dictionary containing key-value pairs of the four
    aforementioned attributes and the collected data.

    ...

    Attributes
    ----------
    url : str
        the URL address of The Stewpot
    webdriver : PlaywrightContextManager
        object that remotely opens and interacts with a web browser
    page : playwright.sync_api.Page
        an object representing the current webpage the browser is viewing
    events_data : list[dict]
        a list that stores the dictionaries with data of all available volunteering events
    event_attrs : list[str]
        a list of the four details to be scraped from the website's volunteering events
    curr_event_dict : dict
        a dictionary that stores volunteer event data of the current webpage being viewed
    events_panel_html : str
        a string that stores the HTML content of the webpage that displays all volunteering events
     events_panel_soup : BeautifulSoup
        the BeautifulSoup parser for the webpage that displays all volunteering events
    curr_event_html : str
        a string that stores the HTML content for the webpage of the current volunteering event being viewed
    curr_event_soup : BeautifulSoup
        the BeautifulSoup parser for the webpage of the current volunteering event being viewed

    Methods
    -------
    launch_browser(wd):
        Launches a Chromium browser and goes to The Stewpot's website.

    go_to_events_page():
        Redirects to the webpage that displays all available volunteering events.

    get_event_title():
        Returns the title of the volunteering event on the current page.

    get_event_dates():
        Returns a list of datetime objects with all available shifts for the volunteering event on the current page.
        Returns "Ongoing" if there are no defined shifts.

    get_event_address():
        Goes to the information page, returns the volunteer event's address, returns back to original event page.

    get_age_restriction():
        Returns a phrasal string describing the age restriction of the volunteering opportunity on the current webpage.
        Returns None if an age restriction does not exist.

    scrape_event(event):
        Goes to the event URL (given by parameter), creates empties the curr_event_dict, stores current event data in
        the curr_event_dict, appends it to events_data, then returns to the events panel page.

    scrape_events_panel():
        Iterates through all events on the events panel page and calls the scrape_event() method.

    next_page_exists():
        Checks if there is an arrow to go to the next page, as the events panel may be split into 2 or more sections.

    scrape_website():
        Launches the webdriver, goes to the events panel page, scrapes the events panel page(s) (involves scraping each
        event page), checks to see if there are any more pages to see on the events panel page, then returns all the
        data stored in events_data.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes to scrape The Stewpot's website and store the data retrieved.

        Parameters
        ----------

        """
        self.url = 'https://www.thestewpot.org/'
        self.webdriver = sync_playwright()
        self.page = None

        self.events_data = []
        self.event_attrs = ['Title', 'Date', 'Address', 'Age Restriction']
        self.curr_event_dict = {'Title': str,
                                'Date': list[datetime],
                                'Address': str,
                                'Age Restriction': str | None}

        self.events_panel_html = None
        self.events_panel_soup = None
        self.curr_event_html = None
        self.curr_event_soup = None

    def launch_browser(self, wd) -> None:
        """
        Launches a Chromium browser with the Playwright webdriver, opens a webpage, and goes to The Stewpot's website.

        Parameters
        ----------
        wd : PlaywrightContextManager
            An instance of sync_playwright(), which is opened by the "with" statement.

        Returns
        -------
        None
        """

        browser = wd.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(self.url)
        self.page = page

    def go_to_events_page(self) -> None:
        """
        Redirects to the volunteer events panel page by clicking buttons that lead to the webpage.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.page.click('.button[href="/i-want-to-help"]')
        self.page.click('.button[href="/volunteer"]')
        self.page.click('.button[href="https://thestewpot.galaxydigital.com"]')
        self.page.click('.btn[href="/need/"]')

    def get_event_title(self) -> str:
        """
        Finds the title of the event on the current webpage and returns it.

        Parameters
        ----------
        None

        Returns
        -------
        str
        """

        return self.curr_event_soup.find(class_='panel-title').text.strip()

    def get_event_dates(self) -> list[datetime] | str:
        """
        Parses through a table element on the current webpage to find all available shifts and their dates, stores the
        shift dates in a list of formatted datetime objects, then returns the list if the table element exists.
        Otherwise, catch an AttributeError when attempting to find the element and return "Ongoing" to signify that the
        volunteer event has no definite shifts.

        Parameters
        ----------
        None

        Returns
        -------
        list[datetime]
        """

        # TODO: Figure out some other format when importing all the dates for volunteering events, because MySQL does not support lists as input datatypes for data tables.

        try:
            table = self.curr_event_soup.find('table', id='shifts-table')
            rows = table.find_all('tr', tabindex='0')
            shifts = []
            for row in rows:
                target_string = row.find('td').text
                target_words = target_string.split()[:4]
                unformatted_date = ' '.join(target_words)
                formatted_date_obj = datetime.strptime(unformatted_date, "%a %b %d, %Y")
                shifts.append(formatted_date_obj)
            return shifts
        except AttributeError:
            return 'Ongoing'

    def get_event_address(self) -> str:
        """
        Redirects to the volunteer event's program information webpage to reliably find the event's address. Proceeds
        to return the event's address.

        Parameters
        ----------
        None

        Returns
        -------
        str
        """

        self.page.click('.more-info')
        program_page_html = self.page.inner_html('.location')
        program_soup = BeautifulSoup(program_page_html, 'html.parser')
        address_string = program_soup.find('td', class_='text').text.strip()
        formatted_address = ' '.join(address_string.split())
        self.page.go_back()
        return formatted_address

    def get_age_restriction(self) -> str | None:
        """
        Finds the age restriction of the event on the current webpage and returns a string of the form "# and older".
        Returns None if no age restriction is found.

        Parameters
        ----------
        None

        Returns
        -------
        str | None
        """

        additional_details = self.curr_event_soup.find('section', class_='requirements')
        text_body = additional_details.find('tbody').text.strip()
        if "and older" in text_body:
            return text_body.split('\n')[1]
        else:
            return None

    def scrape_event(self, event: BeautifulSoup) -> None:
        """
        Finds the title, date, address, and age restriction of the event on the current webpage and stores it in
        curr_event_dict, which then is copied and stored as an element in events_data. The function goes to the webpage
        of the current event (entered as a parameter), saves the HTMl contents in curr_event_html, then creates a
        BeautifulSoup object with it. After the data has been appended to events_data, the webdriver returns to the
        events panel webpage.

        Parameters
        ----------
        event : BeautifulSoup
            An HTML segment of the event to be parsed, which includes its redirect hyperlink

        Returns
        -------
        None
        """

        event_url = event.find('a')['href']
        self.page.click(f'.card-body[href="{event_url}"]')

        self.curr_event_html = self.page.inner_html('.panel')
        self.curr_event_soup = BeautifulSoup(self.curr_event_html, 'html.parser')

        self.curr_event_dict = {'Title': self.get_event_title(),
                                'Date': self.get_event_dates(),
                                'Address': self.get_event_address(),
                                'Age Restriction': self.get_age_restriction()}

        self.page.go_back()
        self.events_data.append(self.curr_event_dict)

    def scrape_events_panel(self) -> None:
        """
        Stores the HTML contents of the current event panels page, creates a BeautifulSoup object to parse through it,
        identifies all the events found, and then iterates through each event and calls scrape_event() on it.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.events_panel_html = self.page.inner_html('.panel-content')
        self.events_panel_soup = BeautifulSoup(self.events_panel_html, 'html.parser')

        events = self.events_panel_soup.find_all('div', class_='need')
        for event in events:
            self.scrape_event(event)

    def next_page_exists(self) -> bool:
        """
        Checks to see if the webdriver can cycle through anymore webpages in the events panel page and returns a
        boolean value evaluating this condition.

        Parameters
        ----------
        None

        Returns
        -------
        bool
        """

        return self.events_panel_soup.find('a', href='/need/index/12')

    def scrape_website(self) -> list[dict]:
        """
        Creates a web driver, launches a Chromium browser, redirects to the events panel webpage, iterates through all
        events on the events panel webpage by calling scrape_event for each, checking to see if there are anymore
        events panel webpages to view before breaking from the loop, and finally returning events_data.

        Parameters
        ----------
        None

        Returns
        -------
        events_data : list[dict]
            A list of dictionaries, with each dictionary containing data for an event
        """

        with self.webdriver as wd:
            self.launch_browser(wd)
            self.go_to_events_page()

            while True:
                self.scrape_events_panel()

                if self.next_page_exists():
                    self.page.click('a[href="/need/index/12"]')
                else:
                    break

        return self.events_data
