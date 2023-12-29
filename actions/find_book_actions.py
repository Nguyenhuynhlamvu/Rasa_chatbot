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

# class ActionTellTime(Action):
#     def name(self) -> Text:
#         return "ac
#validate find book form
class ActionValidateFindBookForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_find_book_form"
    

    def validate_book_type(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                                ) -> Dict[Text, Any]:
        return {"book_name": slot_value}

class ActionFindBook(Action):

    def name(self) -> Text:
        return "action_find_book"
    

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text=f"Tra database và hiện cuốn sách tên {tracker.get_slot('book_name')} lên GUI")
        dispatcher.utter_message(text="Đây có đúng là cuốn sách bạn tìm không")
        return []

class ActionClearFindBookSlots(Action):

    def name(self) -> Text:
        return "action_clear_book_form_slot"
    

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("book_name", None)]
        # dispatcher.utter_message(text=f"{tracker.get_slot('book_name')}")
        # return []
   
class ActionAskforInstruction(Action):
    def name(self) -> Text:
        return "action_ask_for_instruction"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Bạn có cần mình dẫn đường hay không?")
        return []


#run ros
class ActionRunGoalBroadcaster(Action):
    def name(self) -> Text:
        return "action_run_goal_broadcaster"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if tracker.get_intent_of_latest_message() == "affirm":
            # Get cooordinate from database following specific student ID
            x, y, z = 5.5, -2.0, 1.0
            # x, y, z = 1.0, -1.0, 1.0
            coor = f'{x},{y},{z}'
            HTTP_methods.post_message('run_barcode', coor)
            
            msg = "Được rồi, theo tôi."
            dispatcher.utter_message(text=msg)
            
            # Path to your Python node inside the Catkin workspace
            python_node_path = '/home/xuanai/catkin_ws/src/library_robot/scripts/goal_broadcaster.py'

            # Run the ROS Python node from the Catkin workspace
            process = subprocess.Popen(['/usr/bin/python3', python_node_path])
        else:
            dispatcher.utter_message(text="Oke, vậy chào bạn.")

        return []