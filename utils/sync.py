def find_sync_word(
    data,
    magic_word
):

    length=len(
        magic_word
    )

    for i in range(
        len(data)
        -length+1
    ):

        if data[
            i:i+length
        ]==magic_word:

            return i

    return -1