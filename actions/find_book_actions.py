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



BOOK_NAME = ''


class ActionValidateFindBookForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_find_book_form"

    def validate_book_name(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                                ) -> Dict[Text, Any]:
        global BOOK_NAME
        print('..........................')
        name = HTTP_methods.get_request(choose_book).text.encode('latin1').decode('utf8')
        print('...................name: ', name)
        if name != '0':
            result = book_search.search_all_by_name_in_books(name)
            print('name: ', name)
            HTTP_methods.post_message(choose_book, '0')
        else:
            result = book_search.search_all_by_name_in_books(slot_value)
            name = slot_value
            print('slot_value: ', name)
        if result is not None:
            HTTP_methods.post_message(info_book, str(result))
            HTTP_methods.post_message(run_barcode, 'find_book_list')
            BOOK_NAME = result[1]
            # print('result: ', result[1])
            dispatcher.utter_message(text=f"Bạn muốn tìm cuốn sách {name}, nó nằm ở kệ sách {result[9]}")
            if book_search.search_bookid_by_name_in_bookitem(name, 'true') == None:
                dispatcher.utter_message(text=f"Xin lỗi bạn nhưng thư viện hiện không còn cuốn sách {name} nào.")
                return {"book_name": None}
            return {"book_name": name}
        else:
            dispatcher.utter_message(text=f"Xin lỗi, mình không tìm thấy bất kì cuốn sách nào tên là {slot_value} trong dữ liệu cả.")
            books = book_search.find_book_by_similarity_name(slot_value)
            # print('book_names: ', book_names)
            if len(books) > 0:
                for book in books:
                    print(book[1])
                HTTP_methods.post_message(info_book, str(books))
                dispatcher.utter_message(text="Có phải bạn cần một trong những cuốn sách này không?")
                HTTP_methods.post_message(run_barcode, 'find_book_list')
                return {"book_name": None}
            else:
                dispatcher.utter_message(text="Xin bạn hãy nói hoặc nhập lại cuốn sách mình muốn tìm!")
                return {"book_name": None}

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
        global BOOK_NAME
        
        if tracker.get_intent_of_latest_message() == "affirm":
            # Get cooordinate from database following specific student ID
            x, y, w = book_search.search_location_by_namebook_in_bookitem(BOOK_NAME)
            # x, y, z = 1.0, -1.0, 1.0
            coor = f'{x},{y},{w}'
            HTTP_methods.post_message(coordinate, coor)
            msg = "Được rồi, theo tôi."
            dispatcher.utter_message(text=msg)
            
            # Run the ROS Python node from the Catkin workspace
            process = subprocess.Popen([which_python3, python_node_path])
        else:
            dispatcher.utter_message(text="Oke, vậy chào bạn.")

        return []