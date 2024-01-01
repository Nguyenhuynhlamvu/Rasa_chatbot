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

# This is a simple example for a custom action which utters "Hello World!"
from typing import Any, Text, Dict, List

from rasa_sdk import FormValidationAction, Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
import arrow
import subprocess
import time
import datetime






ALLOWED_BOOK_DATES = ["một", "hai", "ba"]
ALLOWED_BOOK_TYPE = ["toán học", "văn học", "vật lý"]
MAX_BORROW_BOOKS = 2
BORROW_BOOK_LIST = []
ID_STUDENT = 0


    
#validate lend form
class ActionValidateLendForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_lend_form"
    

    def validate_book_type(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                                ) -> Dict[Text, Any]:
    
        if slot_value.lower() not in ALLOWED_BOOK_TYPE:
            dispatcher.utter_message(text=f"Chúng tôi không có loại sách {slot_value}.")
            return {"book_type": None}
        # dispatcher.utter_message(text=f"OK! Bạn muốn mượn sách {slot_value}.")
        return {"book_type": slot_value}


    def validate_borrow_dates(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                                ) -> Dict[Text, Any]:
        
        if slot_value.lower() not in ALLOWED_BOOK_DATES:
            dispatcher.utter_message(text=f"Chúng tôi không cho phép mượn sách quá ba ngày.")
            return {"borrow_dates": None}
        
        # dispatcher.utter_message(text=f"OK! Bạn muốn mượn sách trong {slot_value} ngày.")
        return {"borrow_dates": slot_value}


class ActionSubmit(Action):

    def name(self) -> Text:
        return "action_submit"
    

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text=f"Oke bạn muốn mượn cuốn sách {tracker.get_slot('book_type')} trong {tracker.get_slot('borrow_dates')} ngày phải không?")
        # dispatcher.utter_message(text="Oke bạn muốn mượn cuốn sách ngày phải không?")
        return []  
    
class ActionRequestPlaceStudentCard(Action):
    def name(self) -> Text:
        return "action_request_place_student_card"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global ID_STUDENT
        ID_STUDENT = 0
        HTTP_methods.post_message(run_barcode, 'card')
        HTTP_methods.post_message(card_ID, '0')
        while(1):
            if HTTP_methods.get_request(card_ID).text != "0":
                ID_STUDENT = HTTP_methods.get_request(card_ID).text
                break
            time.sleep(0.05)
        # process database
        if ID_STUDENT != 'None':
            result = book_search.search_studentinfo_by_id(ID_STUDENT)
            if result is not None:
                HTTP_methods.post_message(info_database, str(result))
                dispatcher.utter_message(text=f"Mã số sinh viên của bạn là {ID_STUDENT} phải không.")
                dispatcher.utter_message(text=f"Làm ơn đưa sách vào khe bên dưới để mình kiểm tra.")
            else:
                dispatcher.utter_message(text=f"Xin lỗi, mình không tìm thấy trong dữ liệu bất kì sinh viên nào có mã số sinh viên là {ID_STUDENT}.")
        else:
            print(ID_STUDENT)
            dispatcher.utter_message(text="Mình không đọc được thẻ sinh viên của bạn.")
#         return []  
    
class ActionRequestPlaceBorrowBook(Action):
    def name(self) -> Text:
        return "action_request_place_borrow_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        global BORROW_BOOK_LIST  
        ID = None
        HTTP_methods.post_message(run_barcode, 'borrow_book')
        HTTP_methods.post_message(book_ID, '0')
        while(1):
            if HTTP_methods.get_request(book_ID).text != "0":
                ID = HTTP_methods.get_request(book_ID).text
                break
            time.sleep(0.05)
        BORROW_BOOK_LIST.append(ID)
        if ID != 'None':
            name_book = book_search.search_name_by_id_in_bookitem(ID)
            # print(result)
            if name_book is not None:
                result = book_search.search_all_by_name_in_books(name_book)
                # print('....................................')
                HTTP_methods.post_message(info_database, str(result))
                dispatcher.utter_message(text=f"Cuốn sách bạn muốn mượn là {name_book}.")
                # dispatcher.utter_message(text=f"Bạn có muốn mượn thêm cuốn sách nào nữa không.")
            else:
                dispatcher.utter_message(text=f"Xin lỗi, tôi không tìm thấy cuốn sách với ID là {ID} trong dữ liệu.")
        else:
            dispatcher.utter_message(text=f"Xin lỗi, tôi chưa quét được mã vạch.")

        return []

class ActionProcessLendForm(Action):
    def name(self) -> Text:
        return "action_process_lend_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global BORROW_BOOK_LIST, ID_STUDENT
        # print('confirm_enough_books: ', tracker.get_slot('confirm_enough_books'))
        for id_book in BORROW_BOOK_LIST:
            book_search.update_isavailable_state('false', id_book)
            borrow_day = datetime.datetime.now()
            book_search.create_bill(ID_STUDENT, id_book, borrow_day)
        BORROW_BOOK_LIST = []
        dispatcher.utter_message(text="Đã xử lí xong mượn sách")
        return []

        