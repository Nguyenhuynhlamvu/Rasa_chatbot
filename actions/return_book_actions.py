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




    
class ActionRequestPlaceReturnBook(Action):
    def name(self) -> Text:
        return "action_request_place_return_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ID = None
        HTTP_methods.post_message(run_barcode, 'book')
        HTTP_methods.post_message(book_ID, '0')
        while(1):
            if HTTP_methods.get_request(book_ID).text != "0":
                ID = HTTP_methods.get_request(book_ID).text
                break
            time.sleep(0.05)
        if ID != 'None':
            result = book_search.search_book_by_id(ID)
            # print(result)
            if result is not None:
                HTTP_methods.post_message(info_database, str(result))
                dispatcher.utter_message(text=f"Bạn muốn trả cuốn sách {result[2]} này đúng không.")
            else:
                dispatcher.utter_message(text=f"Xin lỗi, tôi không tìm thấy cuốn sách với ID là {ID} trong dữ liệu.")
        else:
            dispatcher.utter_message(text=f"Xin lỗi, tôi chưa quét được mã vạch.")

        return []
    
class ActionProcessReturnForm(Action):
    def name(self) -> Text:
        return "action_process_return_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # result = book_search.search_studentinfo_by_id(ID_student)
        # send data to GUI
        dispatcher.utter_message(text="Đã xử lí xong trả sách")
        
        return [] 