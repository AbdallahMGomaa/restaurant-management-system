from django.test import TestCase
import requests
import random
import json
import datetime


path = "http://127.0.0.1:8000/reservations/"
# Create your tests here.
class AvailableTimeSlots(TestCase):
    def test_minimumNumberOfSeats(self):
        header = json.loads(
            requests.post(
                url='http://127.0.0.1:8000/users/login/',
                json={'number':'1234','password':'123456'}
            ).content.decode()
        )
        requiredSeats = random.randint(1,12)
        response = requests.get(
            url=path+'checkAvailableSlots/',
            headers=header,
            json = {'seats':str(requiredSeats)}
        )
        minTableBody = json.loads(response.content.decode())
        response = requests.get(
            url="http://127.0.0.1:8000/tables/get/",
            headers=header
        )
        tables = json.loads(json.loads(response.content.decode())['tables'])
        minTable = tables[0]
        for table in tables:
            if table['seats']>=requiredSeats:
                if minTable['seats']<requiredSeats or table['seats']<minTable['seats']: 
                    minTable = table
        self.assertEqual(minTableBody['seats'],minTable['seats'])
    
    def test_reservation(self):
        header = json.loads(
            requests.post(
                url='http://127.0.0.1:8000/users/login/',
                json={'number':'1234','password':'123456'}
            ).content.decode()
        )
        timeNow = datetime.datetime.now()
        end_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(23,59,59,999999))
        reservations = [
            (
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+1,
                            timeNow.minute,
                            timeNow.second,
                            timeNow.microsecond
                ), 
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+2,
                            timeNow.minute,
                            timeNow.second,
                            timeNow.microsecond
                ),
                'table reserved successfully'
            ),
            (
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+2,
                            timeNow.minute,
                            timeNow.second+1,
                            timeNow.microsecond
                ), 
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+3,
                            timeNow.minute,
                            timeNow.second,
                            timeNow.microsecond
                ),
                'table reserved successfully'
            ),
            (
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour,
                            timeNow.minute,
                            timeNow.second-1,
                            timeNow.microsecond
                ), 
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+1,
                            timeNow.minute,
                            timeNow.second-1,
                            timeNow.microsecond
                ),
                'invalid time range'
            ),
            (
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+2,
                            timeNow.minute+1,
                            timeNow.second,
                            timeNow.microsecond
                ),
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+2,
                            timeNow.minute,
                            timeNow.second,
                            timeNow.microsecond
                )
                ,
                'invalid time range',
            ),
            (
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour,
                            timeNow.minute,
                            timeNow.second+1,
                            timeNow.microsecond
                ),
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+1,
                            timeNow.minute,
                            timeNow.second+1,
                            timeNow.microsecond
                ),
                'table already reserved'
            ),
            (
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+1,
                            timeNow.minute,
                            timeNow.second,
                            timeNow.microsecond
                ),
                datetime.datetime(
                            timeNow.year,
                            timeNow.month,
                            timeNow.day,
                            timeNow.hour+2,
                            timeNow.minute,
                            timeNow.second,
                            timeNow.microsecond
                ),
                'table already reserved'
            )
        ]
        for reservation in reservations:
            response = requests.post(
                url=path+'reserve/',
                headers=header,
                json={
                    'table':'1',
                    'start':str(
                        reservation[0]
                    ),
                    'end':str(
                        reservation[1]
                    )
                }
            ).content.decode()
            # body = json.loads(response)
            self.assertEqual(response,reservation[2])
