import numpy as np


def crop_rd_map(
    array,
    index,
    doppler_bins,
    subarray_shape
):

    thresholds=subarray_shape

    shape=array.shape

    zero_speed=int(
        doppler_bins/2
    )

    start_row=max(
        0,
        index[0]-thresholds[0]
    )

    end_row=min(
        shape[0],
        index[0]
        +thresholds[0]
        +1
    )

    start_col=max(
        0,
        index[1]
        -thresholds[1]
    )

    end_col=min(
        shape[1],
        index[1]
        +thresholds[1]
        +1
    )

    sub=array[
        start_row:end_row,
        start_col:end_col
    ]

    return np.pad(
        sub,
        (
            (0,
            thresholds[0]*2+1
            -sub.shape[0]),
            (0,
            thresholds[1]*2+1
            -sub.shape[1])
        )
    )