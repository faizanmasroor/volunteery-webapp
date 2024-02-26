# Volunteery Webapp

This is a long-term project that aims to create a web app that allows people to search for volunteering opportunities with filters like location, age restrictions, and date.

The flow of data involves a web scraper (in Python) being built for each website to parse through the pages and return all the data about volunteering events.
Then, it is stored in a MySQL DB which is later queried by the frontend once a user starts searching for volunteering events and choosing search filters.
