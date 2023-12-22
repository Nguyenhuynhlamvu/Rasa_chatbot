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

# class ActionTellTime(Action):
#     def name(self) -> Text:
#         return "action_tell_time"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         current_place = next(tracker.get_latest_entity_values("place"), None)
#         utc = arrow.utcnow()
        
#         msg = f"It's {utc.format('HH:mm')} in {current_place} now. "
#         dispatcher.utter_message(text=msg)

#         return []
    
class ActionRunGoalBroadcaster(Action):
    def name(self) -> Text:
        return "action_run_goal_broadcaster"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if tracker.get_intent_of_latest_message() == "affirm":
            msg = "Được rồi, theo tôi."
            dispatcher.utter_message(text=msg)
            
            # Get cooordinate from database following specific student ID
            # x, y, z = 5.5, -2.0, 1.0
            x, y, z = 1.0, -1.0, 1.0
            coor = f'{x},{y},{z}'
            HTTP_methods.post_message('run_barcode', coor)
            
            # Path to your Python node inside the Catkin workspace
            python_node_path = '/home/xuanai/catkin_ws/src/library_robot/scripts/goal_broadcaster.py'

            # Run the ROS Python node from the Catkin workspace
            process = subprocess.Popen(['/usr/bin/python3', python_node_path])
        else:
            dispatcher.utter_message(text="Oke, vậy chào bạn.")

        return []
    

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
    

class ActionAskforInstruction(Action):

    def name(self) -> Text:
        return "action_ask_for_instruction"
    

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Bạn có cần mình dẫn đường hay không?")
        return []
    
class ActionRequestPlaceBook(Action):
    def name(self) -> Text:
        return "action_request_place_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ID = 0
        HTTP_methods.post_message(run_barcode, 'book')
        HTTP_methods.post_message(book_ID, '0')
        while(1):
            if HTTP_methods.get_request(book_ID).text != "0":
                ID = HTTP_methods.get_request(book_ID).text
                break
            time.sleep(0.05)
        dispatcher.utter_message(text=f"Bạn muốn trả cuốn sách với ID là {ID} này đúng không.")

        return []
    
class ActionProcessReturnForm(Action):
    def name(self) -> Text:
        return "action_process_return_form"

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
        if ID_student != 0:
            # result = book_search.search_studentinfo_by_id(ID_student)
            # print(result)
            dispatcher.utter_message(text=f"Mã số sinh viên của bạn là {ID_student}.")
            dispatcher.utter_message(text="Đã xử lí xong trả sách")
        else:
            print(ID_student)
            dispatcher.utter_message(text="Mình không đọc được thẻ sinh viên của bạn.")
#         return []