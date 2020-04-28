from __future__ import annotations

import hashlib
import importlib
import os
import pickle
<<<<<<< HEAD
=======
import re
>>>>>>> origin/feature/versioning
from enum import Enum
from typing import Tuple, List, Optional, Union

import numpy as np
import tensorflow as tf
from scipy import spatial

from lr_face.data import FaceImage, FaceTriplet, to_array, FacePair
from lr_face.losses import TripletLoss
from lr_face.utils import cache
<<<<<<< HEAD
from lr_face.versioning import Version

EMBEDDINGS_DIR = 'embeddings'
MODELS_DIR = 'models'
=======
from lr_face.versioning import Tag

EMBEDDINGS_DIR = 'embeddings'
WEIGHTS_DIR = 'weights'
>>>>>>> origin/feature/versioning


class DummyScorerModel:
    """
    Dummy model that returns random scores.
    """

    def __init__(self, resolution=(100, 100)):
        self.resolution = resolution

    def fit(self, X, y):
        assert X.shape[1:3] == self.resolution
        pass

    def predict_proba(self, X: List[FacePair]):
        return np.random.random(size=(len(X), 2))

    def __str__(self):
        return 'Dummy'


class ScorerModel:
    """
    A wrapper around an `EmbeddingModel` that converts the embeddings of image
    pairs into (dis)similarity scores.
    """

    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model

    def predict_proba(self, X: List[FacePair]) -> np.ndarray:
        """
        Takes a list of face pairs as an argument and computes similarity
        scores between all pairs. To conform to the sklearn interface we
        return a 2D array of shape `(num_pairs, 2)`, where the first column
        is effectively ignored. The similarity scores are thus stored in the
        second column.

        :param X: List[FacePair]
        :return np.ndarray
        """
        scores = []
        cache_dir = EMBEDDINGS_DIR
        for pair in X:
            embedding1 = self.embedding_model.embed(pair.first, cache_dir)
            embedding2 = self.embedding_model.embed(pair.second, cache_dir)
            score = spatial.distance.cosine(embedding1, embedding2)
            scores.append([score, 1 - score])
        return np.asarray(scores)

    def __str__(self) -> str:
        return f'{self.embedding_model.name}Scorer'


class EmbeddingModel:
    def __init__(self,
<<<<<<< HEAD
                 base_model: tf.keras.Model,
                 version: Optional[Version],
                 resolution: Tuple[int, int],
                 model_dir: str,
                 name: str):
        self.base_model = base_model
        self.current_version = version
        self.resolution = resolution
        self.model_dir = model_dir
        self.name = name
        if version:
            self.load_weights(version)
=======
                 model: tf.keras.Model,
                 tag: Optional[Tag],
                 resolution: Tuple[int, int],
                 model_dir: str,
                 name: str):
        self.model = model
        self.tag = tag
        self.resolution = resolution
        self.model_dir = model_dir
        self.name = name
        if tag:
            self.load_weights(tag)
>>>>>>> origin/feature/versioning

    @cache
    def embed(self,
              image: FaceImage,
              cache_dir: Optional[str] = None) -> np.ndarray:
        """
        Computes an embedding of the `image`. Returns a 1D array of shape
        `(embedding_size)`.

        Optionally, a `cache_dir` may be specified where the embedding should
        be stored on disk. It can then be quickly loaded from disk later, which
        is typically faster than recomputing the embedding.

        :param image: FaceImage
        :param cache_dir: Optional[str]
        :return: np.ndarray
        """
        x = image.get_image(self.resolution, normalize=True)
        x = np.expand_dims(x, axis=0)
        if cache_dir:
            output_path = os.path.join(
                cache_dir,
<<<<<<< HEAD
                str(self),
=======
                str(self).replace(':', '-'),  # Windows compatibility
>>>>>>> origin/feature/versioning
                image.source or '_',
                f'{hashlib.md5(image.path.encode()).hexdigest()}.obj'
            )

            # If the embedding has been cached before, load and return it.
            if os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    return pickle.load(f)

            # If the embedding has not been cached to disk yet: compute the
            # embedding, cache it afterwards and then return the result.
<<<<<<< HEAD
            embedding = self.base_model.predict(x)[0]
=======
            embedding = self.model.predict(x)[0]
>>>>>>> origin/feature/versioning
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                pickle.dump(embedding, f)
            return embedding

        # If no `cache_dir` is specified, we simply compute the embedding.
<<<<<<< HEAD
        return self.base_model.predict(x)[0]

    def load_weights(self, version: Version):
        weights_path = self.get_weights_path(version)
        if not os.path.exists(weights_path):
            raise ValueError(f"Unable to load weights for version {version}: "
                             f"Could not find weights at {weights_path}")
        self.base_model.load_weights(weights_path)
        self.current_version = version

    def save_weights(self, version: Version):
        weights_path = self.get_weights_path(version)
        self.base_model.save_weights(weights_path, overwrite=False)
        self.current_version = version
        print(f"Saved weights for version {version} to {weights_path}")

    def get_weights_path(self, version: Version):
        filename = version.append_to_filename('weights.h5')
=======
        return self.model.predict(x)[0]

    def load_weights(self, tag: Tag):
        weights_path = self.get_weights_path(tag)
        if not os.path.exists(weights_path):
            raise ValueError(f"Unable to load weights for {tag}: "
                             f"Could not find weights at {weights_path}")
        self.model.load_weights(weights_path)
        self.tag = tag

    def save_weights(self, tag: Tag):
        weights_path = self.get_weights_path(tag)
        self.model.save_weights(weights_path, overwrite=False)
        self.tag = tag
        print(f"Saved weights for {tag} to {weights_path}")

    def get_weights_path(self, tag: Tag):
        filename = tag.append_to_filename('weights.h5')
>>>>>>> origin/feature/versioning
        return os.path.join(self.model_dir, filename)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.name == other.name \
<<<<<<< HEAD
               and self.current_version == other.current_version

    def __str__(self):
        if self.current_version:
            return f'{self.name}_{self.current_version}'
=======
               and self.tag == other.tag

    def __str__(self):
        if self.tag:
            return f'{self.name}_{self.tag}'
>>>>>>> origin/feature/versioning
        return self.name


class TripletEmbeddingModel(EmbeddingModel):
    """
    A subclass of EmbeddingModel that can be used to finetune an existing,
    pre-trained embedding model using a triplet loss.
    """

    def train(self,
              triplets: List[FaceTriplet],
              batch_size: int,
              num_epochs: int,
              optimizer: tf.keras.optimizers.Optimizer,
              loss: TripletLoss):
<<<<<<< HEAD
        trainable_model = self._build_trainable_model()
=======
        trainable_model = self.build_trainable_model()
>>>>>>> origin/feature/versioning
        trainable_model.compile(optimizer, loss)
        anchors, positives, negatives = to_array(
            triplets,
            resolution=self.resolution,
            normalize=True
        )

        # The triplet loss that is used to train the model actually does not
        # need any ground truth labels, since it simply aims to maximize the
        # difference in distances to the anchor embedding between positive and
        # negative query images. We create a dummy ground truth variable
        # because Keras loss functions still expect one.
        inputs = [anchors, positives, negatives]
        y = np.zeros(shape=(anchors.shape[0], 1))
        trainable_model.fit(
            x=inputs,
            y=y,
            batch_size=batch_size,
            epochs=num_epochs
        )

<<<<<<< HEAD
    def _build_trainable_model(self) -> tf.keras.Model:
=======
    def build_trainable_model(self) -> tf.keras.Model:
>>>>>>> origin/feature/versioning
        input_shape = (*self.resolution, 3)
        anchors = tf.keras.layers.Input(input_shape)
        positives = tf.keras.layers.Input(input_shape)
        negatives = tf.keras.layers.Input(input_shape)

<<<<<<< HEAD
        anchor_embeddings = self.base_model(anchors)
        positive_embeddings = self.base_model(positives)
        negative_embeddings = self.base_model(negatives)
=======
        anchor_embeddings = self.model(anchors)
        positive_embeddings = self.model(positives)
        negative_embeddings = self.model(negatives)
>>>>>>> origin/feature/versioning

        output = tf.stack([
            anchor_embeddings,
            positive_embeddings,
            negative_embeddings
        ], axis=1)

        return tf.keras.Model([anchors, positives, negatives], output)


class Architecture(Enum):
    """
    This Enum can be used to define all base model architectures that we
    currently support, and to build appropriate Python objects to apply those
    models. This abstracts away the individual implementations of various
    models so that there is one standard way of loading them.

    To load the embedding model for VGGFace for example, you would use:

    ```python
    embedding_model = Architecture.VGGFACE.get_embedding_model("0.0.1")`
    ```

    Similarly, to load a triplet embedder model, you would use:

    ```python
    triplet_embedding_model = \
        Architecture.VGGFACE.get_triplet_embedding_model("0.0.1")`
    ```

    Finally, to load a scorer model, you would use:

    ```python
    scorer_model = Architecture.VGGFACE.get_scorer_model("0.0.1")
    ```
    """
    VGGFACE = 'VGGFace'
    FACENET = 'Facenet'
    FBDEEPFACE = 'FbDeepFace'
    OPENFACE = 'OpenFace'

    @cache
<<<<<<< HEAD
    def get_base_model(self):
=======
    def get_model(self):
>>>>>>> origin/feature/versioning
        if self.source == 'deepface':
            module_name = f'deepface.basemodels.{self.value}'
            module = importlib.import_module(module_name)
            return module.loadModel()
        raise ValueError("Unable to load base model")

    def get_embedding_model(self,
<<<<<<< HEAD
                            version: Optional[Union[str, Version]] = None,
                            use_triplets: bool = False) -> EmbeddingModel:
        if isinstance(version, str):
            version = Version.from_string(version)
        base_model = self.get_base_model()
=======
                            tag: Optional[Union[str, Tag]] = None,
                            use_triplets: bool = False) -> EmbeddingModel:
        if isinstance(tag, str):
            tag = Tag(tag)
        base_model = self.get_model()
>>>>>>> origin/feature/versioning
        os.makedirs(self.model_dir, exist_ok=True)
        cls = TripletEmbeddingModel if use_triplets else EmbeddingModel
        return cls(
            base_model,
<<<<<<< HEAD
            version,
=======
            tag,
>>>>>>> origin/feature/versioning
            self.resolution,
            self.model_dir,
            name=self.value
        )

    def get_triplet_embedding_model(
            self,
<<<<<<< HEAD
            version: Optional[Union[str, Version]] = None
    ) -> TripletEmbeddingModel:
        embedding_model = self.get_embedding_model(version, use_triplets=True)
=======
            tag: Optional[Union[str, Tag]] = None
    ) -> TripletEmbeddingModel:
        embedding_model = self.get_embedding_model(tag, use_triplets=True)
>>>>>>> origin/feature/versioning
        if not isinstance(embedding_model, TripletEmbeddingModel):
            raise ValueError(f'Expected `TripletEmbeddingModel`, '
                             f'but got {type(embedding_model)}')
        return embedding_model

    def get_scorer_model(
            self,
<<<<<<< HEAD
            version: Optional[Union[str, Version]] = None
    ) -> ScorerModel:
        embedding_model = self.get_embedding_model(version, use_triplets=False)
        return ScorerModel(embedding_model)

    def get_latest_version(self) -> Version:
        try:
            model_files = os.listdir(self.model_dir)
        except FileNotFoundError:
            model_files = []
        if not model_files:
            raise ValueError(f'No {self.value} models have been saved yet')
        return max(map(Version.from_filename, model_files))
=======
            tag: Optional[Union[str, Tag]] = None
    ) -> ScorerModel:
        embedding_model = self.get_embedding_model(tag, use_triplets=False)
        return ScorerModel(embedding_model)

    def get_latest_version(self, tag: Union[str, Tag]) -> int:
        if isinstance(tag, str):
            tag = Tag(tag)
        try:
            def filter_func(filename):
                return bool(re.search(rf'{tag.name}-\d+\.\w+$', filename))

            model_files = list(filter(filter_func, os.listdir(self.model_dir)))
        except FileNotFoundError:
            model_files = []
        if not model_files:
            raise ValueError(f'No {self.value} weights have been saved yet')
        return max(map(Tag.get_version_from_filename, model_files))
>>>>>>> origin/feature/versioning

    @property
    def model_dir(self):
        """
        Returns the directory where models for this architecture are stored.

        :return: str
        """
<<<<<<< HEAD
        return os.path.join(MODELS_DIR, self.value)
=======
        return os.path.join(WEIGHTS_DIR, self.value)
>>>>>>> origin/feature/versioning

    @property
    def resolution(self) -> Tuple[int, int]:
        """
        Returns the expected spatial dimensions of the input image as a
        `(height, width)` tuple.

        :return: Tuple[int, int]
        """
<<<<<<< HEAD
        return self.get_base_model().input_shape[1:3]
=======
        return self.get_model().input_shape[1:3]
>>>>>>> origin/feature/versioning

    @property
    def embedding_size(self) -> int:
        """
        Returns the dimensionality of the embeddings for this architecture.

        :return: int
        """
<<<<<<< HEAD
        return self.get_base_model().output_shape[1]
=======
        return self.get_model().output_shape[1]
>>>>>>> origin/feature/versioning

    @property
    def source(self) -> str:
        """
        Returns a textual description of where the model comes from.

        :return: str
        """
        deepface_models = [self.VGGFACE,
                           self.FACENET,
                           self.FBDEEPFACE,
                           self.OPENFACE]
        if self in deepface_models:
            return 'deepface'
        raise ValueError("Unknown model source.")
