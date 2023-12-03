# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import FormValidationAction, Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
import arrow
import subprocess



ALLOWED_BOOK_DATES = ["một", "hai", "ba"]
ALLOWED_BOOK_TYPE = ["toán học", "văn học", "vật lý"]

class ActionTellTime(Action):

    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_place = next(tracker.get_latest_entity_values("place"), None)
        utc = arrow.utcnow()
        
        msg = f"It's {utc.format('HH:mm')} in {current_place} now. "
        dispatcher.utter_message(text=msg)

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
        dispatcher.utter_message(text=f"OK! Bạn muốn mượn sách {slot_value}.")
        return {"book_type": slot_value}
        

        return []

    def validate_borrow_dates(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                                ) -> Dict[Text, Any]:
        
        if slot_value.lower() not in ALLOWED_BOOK_DATES:
            dispatcher.utter_message(text=f"Chúng tôi không cho phép mượn sách quá ba ngày.")
            return {"borrow_dates": None}
        # Path to your Python node inside the Catkin workspace
        python_node_path = '/home/xuanai/catkin_ws/src/library_robot/scripts/goal_broadcaster.py'

        # Run the ROS Python node from the Catkin workspace
        process = subprocess.Popen(['/usr/bin/python3', python_node_path])

        dispatcher.utter_message(text=f"OK! Bạn muốn mượn sách trong {slot_value} ngày.")
        return {"borrow_dates": slot_value}
        

        return []


class ActionValidateLendForm(FormValidationAction):

    def name(self) -> Text:
        return "utter_submit"
    

    def submit_borrow_session(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # current_place = next(tracker.get_latest_entity_values("place"), None)
        # utc = arrow.utcnow()
        
        # msg = f" Borrow session submited "
        # dispatcher.utter_message(text=msg)

        

        return []
        

        return []