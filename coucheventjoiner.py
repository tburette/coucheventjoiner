from enum import Enum
import sys
import os
import re
import time
import argparse
import urlparse
import getpass
import requests
from requests.exceptions import RequestException
import lxml.html

COUCHSURFING_NETLOC = 'www.couchsurfing.org'
COUCHSURFING_EVENT_BASE_PATH = '/n/events/'
COUCHSURFING_AUTH_BASE_PATH = '/n/auth'
DEFAULT_RETRY_DELAY = 30
MIN_RETRY_DELAY = 10

def write_error_and_exit(message):
    sys.stderr.write("{0}: error: {1}\n".format(
            os.path.basename(sys.argv[0]), 
            message)
                     )
    sys.exit(2)    

def validate_event_url(url):
    """
    sys.exit if wrong.
    Return a cleaned up version of the url 
    """

    (_, netloc, path, _, _) = urlparse.urlsplit(url)
    #regexp incorrect (but good enough). Accepts characters incorrect in a URL
    if(netloc != COUCHSURFING_NETLOC or 
       not re.match(COUCHSURFING_EVENT_BASE_PATH + "[^/]+$", path)):
        write_error_and_exit(
            "URL invalid. Expecting {0}, got {1}".format(
                COUCHSURFING_NETLOC + COUCHSURFING_EVENT_BASE_PATH + "...", 
                netloc + path)
            )
    return urlparse.urlunsplit(('https', 
                               COUCHSURFING_NETLOC, 
                               path, 
                               '', #query
                               '') #fragment
                               ) 

def parse_args():
    """sys.exit if wrong arguments"""
    parser = argparse.ArgumentParser(
        description="Tries to join couchsurfing event even if full")
    parser.add_argument('-d', 
                        '--delay', 
                        type=int, 
                        default=DEFAULT_RETRY_DELAY,
                        help='Delay before retrying (in seconds)')
    parser.add_argument('event', 
                        type=str, 
                        help='Event URL')
    parser.add_argument('username',
                        type=str,
                        help='Couchsurfing username')
    #password = None if no password supplied
    #password = "" if user wrote "" for the command line
    parser.add_argument('password',
                        type=str,
                        nargs='?',
                        help='Couchsurfing password. If password missing the '
                             'application will ask for it.')
    return vars(parser.parse_args())

def get_user_values():
    args = parse_args()
    if(args['delay'] < MIN_RETRY_DELAY):
        write_error_and_exit(" Minimum allowed delay is {0}".format(MIN_RETRY_DELAY))
    args['event'] = validate_event_url(args['event'])
    #None instead of 'not x' because allow empty passwords
    if args['password'] is None: 
        args['password'] = getpass.getpass()
    
    return args
    
class LoginException(Exception):
    """
    Error during login attempt
    """
    pass

class ParsingError(Exception):
    """
    Can't retrieve information from page. (Page format changed?)
    """
    pass

def login(username, password, session=None):
    """
    Attempts to login to Couchsurfing.

    Returns:
    requests.Session: session object, logged in Couchsurfing

    Raises:
    requests.exceptions.RequestException: network error
    LoginException: login failed
    """
    if not session:
        session = requests.Session()
    #authenticity_token missing but it still works
    r = session.post('https://' + 
                     COUCHSURFING_NETLOC + 
                     COUCHSURFING_AUTH_BASE_PATH, 
                     data={'return_to':'', 
                           'username':username, 
                           'password':password}
                     )
    if r.status_code == 200:
        return session
    else:
        raise LoginException("Login failed. HTTP code : {0} {1}".format( 
                r.status_code, r.reason))

def is_logged_in(tree):
    """
    Determine if logged in.
    
    Args:
    tree (lxml.html.HtmlElement) : content of a couchsurfing page
    """
    return bool(tree.xpath('//*[@id="main-menu"]/*[@id="logged_in_menu"]'))

def is_event_over(tree):
    """
    Determine if the event is over

    Args:
    tree (lxml.html.HtmlElement) : content of a couchsurfing page representing 
        an event
    """
    #Technically wrong. The searched class could be a substring of another one
    #class="foobar"-> searching for 'bar' would match even tough it's not in it
    return bool(tree.xpath('//*[@id="sidebar"]'
                          '/div[contains(@class, "event_status")]'
                          '/*[text()="This event is over."]')
                )

def is_attending(tree):
    return bool(tree.xpath('//div[contains(@class, "event_join_and_attendees")]'
                           '//a[contains(@class, "leave_event_button") '
                           'and not(contains(@class, "hide"))]')
                )

def is_event_full(tree):
    """
    Determine if event is full

    Args:
    tree (lxml.html.HtmlElement) : content of a couchurfing page 
        representing an event

    Raises:
    ParsingError: Couldn't retrieve data from page to determine if event is full
    """
    attendee_count_results = tree.xpath(
            '//div[contains(@class, "event_attendee_list_container")]'
            '/*[contains(@class, "event_user_list_title")]'
            '/span[1]/text()'
            )
    if not attendee_count_results:
        raise ParsingError("Can\t determine if event full. "
            "(Couldn't retrieve number of attendees)"
                           )
    try:
        attendee_count = int(attendee_count_results[0])
    except ValueError:
        raise ParsingError("Can't determine if event full. "
            "(Couldn't Parse number of attendees)"
                           )

    #if an event has a participant limit it will contain " Attending out of xx"
    #if an event has no participant limit it will contain " Attending"
    attending = tree.xpath(
            '//div[contains(@class, "event_attendee_list_container")]'
            '/*[contains(@class, "event_user_list_title")]'
            '/span[2]/text()'
            )
    if not attending:
        raise ParsingError('Can\'t determine if event full. '
                           'Couldn\'t retrieve number of spots available'
                           )
    if not 'out of' in attending[0]:
        #no participant limit
        return False
    
    try:
        total_spots = int(attending[0].split()[-1])
    except ValueError, IndexError:
        raise ParsingError('Can\'t determine if event full. '
                           'Couldn\'t parse number of spots available'
                           )

    return attendee_count == total_spots
        
def join_event(session, event):
    try:
        r = session.post(event + '/join', 
                         data={'source':'show_page'}
                         )
    except RequestException, e:
        print "Error retrieving page {0}".format(e)
        return false
    else:
        #if full response = 200 with content '{"error":"This event is full."}'
        try:
            is_full = 'This event is full' in r.json().get('error', '')
        except ValueError:
            is_full = False
        if r.status_code == 200 and not is_full:
            return True
        else:
            print "Joining failed.  HTTP code : {0} {1}".format( 
                r.status_code, r.reason)
            return False

class Result(Enum):
    ok = 1
    retry = 2
    abandon = 3

def get_event_page(session, event):
    try:
        r = session.get(event)
    except RequestException, e:
        return (None, (Result.retry, "Error retrieving page. {0}".format(e)))
    if r.status_code == 404:
        return (None, (Result.abandon, "Event doesn't exist ({0})".format(event)))
    if r.status_code != 200:
        return (None, (Result.retry, 
                       "Error retrieving page. HTTP code : {0} {1}".format( 
                    r.status_code, r.reason)
                       )
                )
    tree = lxml.html.fromstring(r.content)
    return (tree, (Result.ok, ''))        
    
def test_logged_in(tree, username, password, session):
    if not is_logged_in(tree):
        print "Logged out. Relogging"
        try:
            login(username, password, session)
        except RequestException, e:
            return (Result.retry, "Network error when attempting to relog in. {0}".format(e.message))
        except LoginException, e:
            return(Result.abandon, "Couldn't relog")
    return (Result.ok, '')
tests=[lambda tree: (Result.abandon, "Event is over") if is_event_over(tree) 
           else (Result.ok, ''),
       lambda tree: (Result.abandon, "Already attending event") 
           if is_attending(tree) 
           else (Result.ok, ''),
       lambda tree: (Result.retry, "Event full")
           if is_event_full(tree)
           else (Result.ok, '')
       ]

def loop_to_join_event(session, event, username, password, retry_delay):
    while True:
        (tree, page_retrieval_result) = get_event_page(session, event)
        #prepend test with result of retrieving the page and curried logged_in
        all_tests = [lambda _: page_retrieval_result] + \
                    [lambda tree: test_logged_in(tree, username, password, session)] + \
                    tests

        for test in all_tests:
            (result, msg) = test(tree)
            if result != Result.ok:
                print msg
                if result == Result.abandon:
                    return
                if result == Result.retry:
                    break
        else:#no break in loop
            if(join_event(session, event)):
                print "Joined event!"
                return
            else:
                print "Failed joining"
        print "Retrying in {0} seconds".format(retry_delay)
        time.sleep(retry_delay)            

def main():
    values = get_user_values()

    try:
        global session #testing
        if not 'session' in vars():
            session = login(values['username'], values['password'])        
    except RequestException, e:
        print "Network error when attempting to login. {0}".format(e.message)
    except LoginException, e:
        print "Couldn't login. {0}".format(e.message)
    else:
        loop_to_join_event(session,
                           values['event'],
                           values['username'],
                           values['password'],
                           values['delay'])

if __name__ == '__main__':
    main()
