from __future__ import print_function

import pyodbc
import pandas as pd
import sched
import time
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds, static_discovery=False)
schedulerTest = sched.scheduler(time.time, time.sleep)
current_day = datetime.datetime.now()


def database_update():
    """
    Connects to the SQL database .
    :return: connection to database
    """

    server = 'servername'
    database = 'database'
    username = 'user'
    password = 'password#'
    # connects to the SQL server using the above variables
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};'
                          'SERVER='+server+
                          ';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    return cnxn


def sql_Queries():
    """
    connects to the DB using the connection from database_update() and sends a SQL query
    :return: results from SQL Query as dataframe
    """
    cnxn = database_update()

    # returning a dataframe saves times since you only request from db once

    query = 'SELECT TOP (15) [AppointmentID],[StartDate],[EndDate],[AppointmentName],[AssignedTo],[Description],' \
            '[CreatedDate],[CreatedBy]' \
            'FROM [SQL2012_1010845_agenciahisp].[dbo].[Appointments]' \
            'ORDER BY AppointmentID DESC'
    sql_table = pd.read_sql(query, cnxn)
    df_appointments = pd.DataFrame(sql_table)
    print(df_appointments)
    return df_appointments


def appntmnts_info():
    """
    using the returned dataframe form SQl_query function it gathers the information of the appointment that will be used
    to create the google event.
    :return:
    """
    df_appointments = sql_Queries()
    num_of_rows = df_appointments.shape[0]-1
    row = 0


    while row<=num_of_rows:

        name =  df_appointments.at[row,'AppointmentName']
        appointment_id = df_appointments.at[row,'AppointmentID' ]
        start_date = str(df_appointments.at[row,'StartDate'])
        end_date = str(df_appointments.at[row,'EndDate'])
        start_convert = sql_time_to(start_date)
        end_convert = sql_time_to(end_date)
        begining = start_convert.datedateframe()
        ending = end_convert.datedateframe()

        description = df_appointments.at[row,'Description']
        reminder = reminders(begining)
        email = email_address(description)

        associatedID = str(df_appointments.at[row, 'AssignedTo'])
        color = colorID(associatedID)


        # 'now' was made for the chkr() it is the date when it was created which is then used to check every event
        # afterwards to see if the event already exist
        created_date = str(df_appointments.at[row,'CreatedDate'])
        created_convert = sql_time_to(created_date)
        now = created_convert.createdDataFrame()


        print('event '+str(appointment_id)+' is printing')
        print(name)
        print(begining)
        print(ending)

        print(now)

        event_creator(name, begining, ending, description, color, email, reminder, now, appointment_id)


        row += 1


def event_creator(*info):
    """
    Creates the event using the google calendar API
    :param info: uses the appointment info to be used as the values for the Google Calendar event
    :return: a created event in google or simply returns to appntmnts_info() if event exist
    """
    name = info[0]
    begining = info[1]
    ending = info[2]
    description = info[3]
    color = info[4]
    email = info[5]
    reminder = info[6]
    now = info[7]
    appointment_id = info[8]
    print(appointment_id)
    results = chkr(name,now)

    # nested If statements are used to differentiate the difference between and event that has an email of an event
    # attendee. Often times end users dont place attendee emails so nested if statement might be useless.

    if results != None:
        print('while statement continuing\n')
        return
    else:
        print('event being created\n')
        if email == None:
            eventwemail = {
                'summary': name,
                'location': '',
                'description': description,
                'start': {
                    'dateTime': begining,
                    'timeZone': 'America/Chicago',
                },
                'colorID': color,
                'end': {
                    'dateTime': ending,
                    'timeZone': 'America/Chicago',
                },
                'colorId': color,
                'attendees': [
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': reminder},
                        {'method': 'popup', 'minutes': 60},
                        {'method': 'popup', 'minutes': 24 * 10},
                    ],
                },
            }
            event = service.events().insert(calendarId='primary', body=eventwemail).execute()
            'Event created: % s' % (event.get('htmlLink'))
            event_id = event.get('id', [])
            event_writer(name, event_id, appointment_id)
        else:
            event = {
                'summary': name,
                'location': '',
                'description': description,
                'start': {
                    'dateTime': begining,
                    'timeZone': 'America/Chicago',
                },
                'colorID': color,
                'end': {
                    'dateTime': ending,
                    'timeZone': 'America/Chicago',
                },
                'colorId': color,
                'attendees': [
                    {'email': email}
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': reminder},
                        {'method': 'popup', 'minutes': 60},
                        {'method': 'popup', 'minutes': 24 * 10},
                    ],
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            'Event created: % s' % (event.get('htmlLink'))
            event_id = event.get('id',[])
            event_writer(name, event_id, appointment_id)


# funstion below will be used to update events that are already existing in google. The way the program is written
# program skips events that are similar in name on google calendar.

def event_writer(*event_info):
    """
    Writes certain event details like the title event ID (googles event ID) and the appointment ID (gathered from the
    DB) to be able to update the event in the future
    :param event_info: name, event_id appointment_id
    :return:
    """
    name = event_info[0]
    event_id = event_info[1]
    appointment_id = str(event_info[2])
    data = {
        'Appointment ID': [appointment_id],
        'title': [name],
        'Event ID': [event_id]
    }
    df = pd.DataFrame(data)
    df.to_csv('EventInformation.csv', mode='a', index=False, header=False)


def chkr(x, y):
    """
    the function check all events after the y parameter which is the date the event was created and then checks those
    events for similar titles (x parameter is title of event) if no event is named the same
    :return: if no events have a similar name to the event in question the results is returned
    """
    now = y
    print('looking from ' + now)
    # making event_result a list of all the events in the main calendar organized by time with a maz amount of rows
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          singleEvents=True,
                                          orderBy='startTime'
                                          ).execute()
    events = events_result.get('items', [])

    # is getting the objects 'items' from event_results

    # print('Events')
    if not events:
        print('No upcoming events found.')
        # Prints the start and name of the next 10 events
    for event in events:
        title = event['summary']
        if title != x:
            # print('event doesnt not exist')
            result_f = 0

        else:
            # print('event already exist')
            result_t = 1
            return result_t


def reminders(x):
    """
    returns an int to be used as the reminder in the appointment info
    :param x: the bigining of the apoinment
    :return:
    """
    hora = int(x[11:13])
    minuto = int(x[14:16])
    morning = 480
    to = timeconvert(hora, minuto)
    hour = to.hour_to_min()

    time_in_mins = hour + minuto
    reminder = time_in_mins - morning

    return reminder


# datetime should be input as string
class sql_time_to:
    def __init__(self,datetime,):
        self.startdate = datetime

    # original solution to issue regarding variable current day/the parameters needed for sql_Queries which is resolved
    # but is being kept incase of future use
    def date_to_string(self):
        date = self.startdate
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        result = year+'-'+month+'-'+day
        return result


    def datedateframe(self):
        complete_date = self.startdate
        time = complete_date[11:19]
        date = complete_date[:10]
        result = date + 'T' + time
        return result

    def createdDataFrame(self):
        creatn_date = self.startdate
        cyear = int(creatn_date[:4])
        cmnth = int(creatn_date[5:7])
        cdy = int(creatn_date[8:10])
        result = datetime.datetime(year=cyear, month=cmnth, day=cdy, hour=1, minute=0, second=0,
                                 microsecond=0).isoformat() + 'Z'
        return result


class timeconvert:
    # made because google api uses minutes for the reminder option
    def __init__(self,hour,minute):
        self.hh_to_mm = hour
        self.mm_to_hh = minute

    # minutes to hours is not used but still made, in case it is needed in the future

    def hour_to_min(self):
        result = self.hh_to_mm * 60
        return result
    def min_to_hour(self):
        result = self.mm_to_hh / 60
        return result


def colorID(x):
    """
    returns the color ID for the event according to the AssociateID from the DB
    for more information regarding Googles ColorID's for Google Calendar go to
    https://lukeboyle.com/blog/posts/google-calendar-api-color-id
    :return:
    """

    data = {'Name': ['Carlos', 'Jackie', 'Laura', 'Mayra ', 'Monica', 'Seyry', 'Silvia', 'OPEN', 'Diego', 'Elvin'],
            'GcolorID': ['9', '4', '10', '2', '7', '3', '11', '5', '8', '1']}
    df = pd.DataFrame(data, index=['35', '29', '34', '32', '31', '50', '30', '48', '39', '53'])

    GcolorID = df.at[x, 'GcolorID']
    return GcolorID



def email_address(x):
    """
    returns an email adress or value to be used in the event info
    :param x: is the
    :return:
    """
    description = x
    at = '@'
    enter = '\n'

    arrova = description.find(at)
    if arrova == -1:
        print('no email address found')
    else:
        ingreso = description.rfind(enter)+1
        adress = description[ingreso:arrova]
        domain = description[arrova:]
        email = adress + domain
        return email

