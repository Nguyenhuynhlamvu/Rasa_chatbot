import typing
from typing import Any, Optional, Text, Dict, List, Type
import fasttext
import numpy as np
import os

# from rasa.nlu.components import Component
from rasa.nlu.featurizers.featurizer import DenseFeaturizer
# from rasa.nlu.config import RasaNLUModelConfig
# from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.tokenizers.tokenizer import Tokenizer
from rasa_nlu.components import Component
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.training_data import Message, TrainingData

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata
from rasa.nlu.constants import DENSE_FEATURE_NAMES, DENSE_FEATURIZABLE_ATTRIBUTES, TEXT


class FastTextFeaturizer(DenseFeaturizer):
    """A new component"""

    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""
        return [Tokenizer]

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["fasttext"]

    defaults = {"file": None, "cache_dir": None}
    language_list = []

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
        path = os.path.join(component_config["cache_dir"], component_config["file"])
        self.model = fasttext.load_model(path)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        for example in training_data.intent_examples:
            for attribute in DENSE_FEATURIZABLE_ATTRIBUTES:
                self.set_fasttext_features(example, attribute)

    def set_fasttext_features(self, message: Message, attribute: Text = TEXT):
        text_vector = self.model.get_word_vector(message.text)
        word_vectors = [
            self.model.get_word_vector(t.text)
            for t in message.data["tokens"]
            if t.text != "__CLS__"
        ]
        X = np.array(word_vectors + [text_vector])  # remember, we need one for __CLS__

        features = self._combine_with_existing_dense_features(
            message, additional_features=X, feature_name=DENSE_FEATURE_NAMES[attribute]
        )
        message.set(DENSE_FEATURE_NAMES[attribute], features)

    def process(self, message: Message, **kwargs: Any) -> None:
        self.set_fasttext_features(message)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any,
    ) -> "Component":
        """Load this component from file."""

        if cached_component:
            return cached_component
        else:
            return cls(meta)