class TorrentListing:
    def __init__(self, title: str, progress: float, state: str, seeds: int) -> None:
        self.__title = title
        self.__progress = round(progress, 2)
        self.__state = "paused" if state == "pausedDL" else "downloading"
        self.__seeds = seeds

    @property
    def title(self) -> str:
        return self.__title

    @property
    def progress(self) -> float:
        return self.__progress

    @property
    def state(self) -> str:
        return self.__state

    @property
    def seeds(self) -> int:
        return self.__seeds

    