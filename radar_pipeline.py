from utils.io import load_json
from network.udp_receiver import UDPReceiver
from decoder.radar_decoder import RadarDecoder
from perception.preprocessing import RadarPreprocessor
from perception.inference import RadarInference
from config.Radar_cube import Radar_cube


class RadarPipeline:

    def __init__(self):

        environment_file = "config/environment.json"
        model_config = "config/model_config.json"
        model_path = "models/radar_east.onnx"

        self.sensor_id = 1

        self.environment = load_json(environment_file)
        self.config = load_json(model_config)

        radar_cube = (
            self.environment["sensors"]
            [str(self.sensor_id)]
            ["RadarParam"]["RadarCube"]
        )

        self.range_bins = Radar_cube[radar_cube]["Range Bins"]
        self.doppler_bins = Radar_cube[radar_cube]["Chirp"]

        self.receiver = UDPReceiver()

        self.decoder = RadarDecoder(
            environment=self.environment,
            sensor_id=self.sensor_id,
            range_bins=self.range_bins,
            doppler_bins=self.doppler_bins,
            config=self.config
        )

        self.preprocessor = RadarPreprocessor(
            self.config
        )

        self.inference = RadarInference(
            model_path
        )

        self.labels = [
            "pedestrian",
            "cyclist",
            "vehicle",
            "truck"
        ]

    def run(self):

        print("Starting radar pipeline")

        while True:

            packet = self.receiver.receive()

            if packet is None:
                continue

            rd_map, crops, detections, stamp = \
                self.decoder.decode(
                    packet["measurements"]
                )

            if len(detections) == 0:
                continue

            inputs = self.preprocessor.normalize(
                crops,
                detections
            )

            labels = self.inference.predict(
                inputs
            )

            result = []

            for i, det in enumerate(detections):

                result.append({

                    "range":
                    int(det[0]),

                    "doppler":
                    int(det[1]),

                    "magnitude":
                    int(det[2]),

                    "azimuth":
                    int(det[3]),

                    "elevation":
                    int(det[4]),

                    "label":
                    self.labels[
                        labels[i]
                    ],

                    "timestamp":
                    stamp
                })

            print(result, "\n")