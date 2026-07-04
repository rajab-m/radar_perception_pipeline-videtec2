import onnxruntime as ort
import numpy as np


class RadarInference:

    def __init__(self,model_path):

        self.session=ort.InferenceSession(
            model_path,
            providers=[
            "CUDAExecutionProvider"
            ]
        )

    def predict(self,inputs):

        logits=self.session.run(
            None,
            inputs
        )

        logits=np.squeeze(
            logits
        ).reshape(
            -1,
            4
        )

        return np.argmax(
            logits,
            axis=1
        )