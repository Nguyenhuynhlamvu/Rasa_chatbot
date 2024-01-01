#!/home/xuanai/Python-env/rasa3/bin/python3
# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import sys
sys.path.append('/home/xuanai/Desktop/Library_robot/')
import Server.HTTP_methods as HTTP_methods
import Server.book_search as book_search
from Global_Variables import *

# This is a simple example for a custom action which utters "Hello Wor  ld!"
from typing import Any, Text, Dict, List

from rasa_sdk import FormValidationAction, Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
import arrow
import subprocess
import time
import datetime

RETURN_BOOK_LIST = []
STUDENT_ID_LIST = []



class ActionRequestPlaceReturnBook(Action):
    def name(self) -> Text:
        return "action_request_place_return_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        global RETURN_BOOK_LIST, STUDENT_ID_LIST
        ID = None
        HTTP_methods.post_message(run_barcode, 'return_book')
        HTTP_methods.post_message(book_ID, '0')
        while(1):
            if HTTP_methods.get_request(book_ID).text != "0":
                ID = HTTP_methods.get_request(book_ID).text
                break
            time.sleep(0.05)
        if ID != 'None':
            # result = book_search.search_book_by_id(ID)
            student_id = book_search.search_studentID_by_boookID_in_Bill(ID)
            name_book = book_search.search_name_by_bookID_in_bookitem(ID)
            # print(name_book)
            book_result = book_search.search_all_by_name_in_books(name_book)
            student_id = book_search.search_studentID_by_boookID_in_Bill(ID)
            if student_id is None:
                dispatcher.utter_message(text=f"Xin lỗi nhưng cuốn sách này chưa được mượn ở thư viện.")
                return []
            student_result = book_search.search_all_by_studentID_in_studentinfo(student_id)
            # print('student_result: ', student_result)
            if book_result is not None:
                if ID in RETURN_BOOK_LIST:
                    dispatcher.utter_message(text=f"Bạn vừa quét cuốn sách này rồi.")
                    return []
                RETURN_BOOK_LIST.append(ID)
                # STUDENT_ID_LIST.append(student_id)
                HTTP_methods.post_message(info_book, str(book_result))
                HTTP_methods.post_message(info_student, str(student_result))
                # HTTP_methods.post_message(info_database, str(result))
                dispatcher.utter_message(text=f"Bạn đang trả cuốn sách {name_book} do sinh viên {student_result[2]} mượn.")
                # dispatcher.utter_message(text=f"Bạn có muốn trả cuốn sách nào nữa không?")
            else:
                dispatcher.utter_message(text=f"Xin lỗi, tôi không tìm thấy cuốn sách với ID là {ID} trong dữ liệu.")
                # dispatcher.utter_message(text=f"Bạn có muốn quét lại không?")
        else:
            dispatcher.utter_message(text=f"Xin lỗi, tôi chưa quét được mã vạch.")
            # dispatcher.utter_message(text=f"Bạn có muốn quét lại không?")

        return []
    
class ActionProcessReturnForm(Action):
    def name(self) -> Text:
        return "action_process_return_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global RETURN_BOOK_LIST
        for ID in RETURN_BOOK_LIST:
            return_day = datetime.datetime.now()
            book_search.update_bill_return(ID, return_day)
            book_search.update_isavailable_state('true', ID)
        dispatcher.utter_message(text="Đã xử lí xong trả sách")
        RETURN_BOOK_LIST = []
        
        return [] 