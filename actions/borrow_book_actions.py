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






ALLOWED_BOOK_DATES = ["một", "hai", "ba"]
ALLOWED_BOOK_TYPE = ["toán học", "văn học", "vật lý"]
MAX_BORROW_BOOKS = 2


    
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
        ID_student = 0
        HTTP_methods.post_message(run_barcode, 'card')
        HTTP_methods.post_message(card_ID, '0')
        while(1):
            if HTTP_methods.get_request(card_ID).text != "0":
                ID_student = HTTP_methods.get_request(card_ID).text
                break
            time.sleep(0.05)
        # process database
        if ID_student != None:
            result = book_search.search_studentinfo_by_id(ID_student)
            if result is not None:
                HTTP_methods.post_message(info_database, str(result))
                dispatcher.utter_message(text=f"Mã số sinh viên của bạn là {ID_student}.")
                dispatcher.utter_message(text=f"Làm ơn đưa sách vào khe bên dưới để mình kiểm tra.")
            else:
                dispatcher.utter_message(text=f"Xin lỗi, mình không tìm thấy trong dữ liệu bất kì sinh viên nào có mã số sinh viên là {ID_student}.")
        else:
            print(ID_student)
            dispatcher.utter_message(text="Mình không đọc được thẻ sinh viên của bạn.")
#         return []  
    
class ActionRequestPlaceBorrowBook(Action):
    def name(self) -> Text:
        return "action_request_place_borrow_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # events = tracker.events
        # for event in reversed(events):
        #     if event['event'] == 'action':
        #         if event['name'] == 'action_request_place_student_card':
        #             print('................', event)
                    
        ID = None
        HTTP_methods.post_message(run_barcode, 'book')
        HTTP_methods.post_message(book_ID, '0')
        while(1):
            if HTTP_methods.get_request(book_ID).text != "0":
                print('ID_student: ', ID)
                ID = HTTP_methods.get_request(book_ID).text
                break
            time.sleep(0.05)
        if ID != None:
            result = book_search.search_book_by_id(ID)
            # print(result)
            if result is not None:
                print('....................................')
                HTTP_methods.post_message(info_database, str(result))
                dispatcher.utter_message(text=f"Cuốn sách bạn tìm là {result[2]}.")
                dispatcher.utter_message(text=f"Bạn có muốn mượn thêm cuốn sách nào nữa không.")
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
        
        print('confirm_enough_books: ', tracker.get_slot('confirm_enough_books'))
        dispatcher.utter_message(text="Đã xử lí xong mượn sách")
        return []

class ActionValidatePlaceBorrowBookForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_place_borrow_book_form"

    def validate_confirm_enough_books(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                                ) -> Dict[Text, Any]:
        
        latest_intent = tracker.get_intent_of_latest_message()
        print('latest_intent: ', latest_intent)
        if latest_intent == 'affirm':
            print('AFFIRM')
            ID = None
            HTTP_methods.post_message(run_barcode, 'book')
            HTTP_methods.post_message(book_ID, '0')
            while(1):
                if HTTP_methods.get_request(book_ID).text != "0":
                    print('ID_student: ', ID)
                    ID = HTTP_methods.get_request(book_ID).text
                    break
                time.sleep(0.05)
            if ID != None:
                result = book_search.search_book_by_id(ID)
                # print(result)
                if result is not None:
                    print('....................................')
                    HTTP_methods.post_message(info_database, str(result))
                    dispatcher.utter_message(text=f"Cuốn sách bạn tìm là {result[2]}.")
                    dispatcher.utter_message(text=f"Bạn có muốn mượn thêm cuốn sách nào nữa không.")
                    return {"confirm_enough_books": None}
                else:
                    dispatcher.utter_message(text=f"Xin lỗi, tôi không tìm thấy cuốn sách với ID là {ID} trong dữ liệu.")
                    dispatcher.utter_message(text=f"Bạn có muốn quét lại không.")
                    return {"confirm_enough_books": None}
            else:
                dispatcher.utter_message(text=f"Xin lỗi, tôi chưa quét được mã vạch.")
                dispatcher.utter_message(text=f"Bạn có muốn quét lại không.")
                print('return {"confirm_enough_books": None}')
                return {"confirm_enough_books": None}
        elif latest_intent == 'deny':
            print('DENY')
            return {"confirm_enough_books": "Done"} 
        