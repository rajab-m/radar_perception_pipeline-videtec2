import numpy as np

from perception.cropping import crop_rd_map


class RadarDecoder:

    def __init__(
        self,
        environment,
        sensor_id,
        range_bins,
        doppler_bins,
        config
    ):

        self.environment=environment
        self.sensor_id=sensor_id
        self.range_bins=range_bins
        self.doppler_bins=doppler_bins

        self.range_crop=\
            config[
            "cropping_thresholds"
            ]["range_threshold"]

        self.doppler_crop=\
            config[
            "cropping_thresholds"
            ]["doppler_threshold"]


    def decode(self,content):

        min_dopp=(
            self.environment[
            "sensors"
            ][str(
            self.sensor_id
            )]["RadarParam"]
            ["MinDopplerBin"]
        )

        rd_bytes=(
            self.range_bins
            *self.doppler_bins
            *2
        )

        rd=content[:rd_bytes]

        rd_map=np.frombuffer(
            rd,
            dtype=">H"
        ).reshape(
            (
            self.range_bins,
            self.doppler_bins
            )
        )

        rd_map=np.fft.fftshift(
            rd_map,
            axes=1
        )

        counter=rd_bytes

        detections=[]

        n=int.from_bytes(
            content[
            counter:
            counter+2
            ],
            "big"
        )

        counter+=2

        crops=[]

        for _ in range(n):

            values=np.frombuffer(
                content[
                counter:
                counter+10
                ],
                dtype=">h"
            )

            counter+=10

            detections.append(values)

            crop=crop_rd_map(
                rd_map,
                (
                    values[0],
                    values[1]-min_dopp
                ),
                self.doppler_bins,
                (
                self.range_crop,
                self.doppler_crop
                )
            )

            crops.append(crop)

        crops=np.array(
            crops
        ).reshape(
            len(crops),
            1,
            self.range_crop*2+1,
            self.doppler_crop*2+1
        )

        return rd_map,crops,detections,0