import numpy as np


class RadarPreprocessor:

    def __init__(self, config):

        params = config["model_parameters"]

        # convert once → always float32 numpy arrays
        self.rd = np.array(params["RD_map_scaler"], dtype=np.float32)
        self.rcs = np.array(params["RCS_scaler"], dtype=np.float32)
        self.speed = np.array(params["Speed_scaler"], dtype=np.float32)
        self.range = np.array(params["Range_scaler"], dtype=np.float32)
        self.az = np.array(params["Azimuth_scaler"], dtype=np.float32)

    def normalize(self, crops, detections):

        # enforce float32 early (important for ONNX)
        crops = crops.astype(np.float32)
        det = np.array(detections, dtype=np.float32)

        return {

            "Cropped_RD_map":
            (crops - self.rd[0]) / self.rd[1],

            "rcs":
            np.expand_dims(
                (det[:, 2] - self.rcs[0]) / self.rcs[1],
                axis=1
            ),

            "speed":
            np.expand_dims(
                (det[:, 1] - self.speed[0]) / self.speed[1],
                axis=1
            ),

            "range":
            np.expand_dims(
                (det[:, 0] - self.range[0]) / self.range[1],
                axis=1
            ),

            "azimuth":
            np.expand_dims(
                (det[:, 3] - self.az[0]) / self.az[1],
                axis=1
            )
        }