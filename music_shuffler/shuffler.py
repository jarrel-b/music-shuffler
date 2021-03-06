import argparse
import csv
from collections import defaultdict
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set


THRESHOLD = 0.05
DELIMITER = "\t"


class Track(NamedTuple):
    title: str
    artist: str
    album: str
    bpm: int
    length: int


class Vertex:
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.neighbors: Dict[int, Vertex] = {}


class Graph:
    def __init__(self) -> None:
        self.vertices: Dict[int, Vertex] = {}

    def add_vertex(self, key, value) -> None:
        self.vertices[key] = Vertex(key, value)

    def add_edge(self, from_key, from_val, to_key, to_val) -> None:
        if from_key not in self.vertices:
            self.add_vertex(from_key, from_val)
        if to_key not in self.vertices:
            self.add_vertex(to_key, to_val)
        self.vertices[from_key].neighbors[to_key] = self.vertices[to_key]

    def __getitem__(self, key):
        return self.vertices[key]

    def __iter__(self):
        return iter(self.vertices.values())


def length_to_seconds(time: str) -> int:
    if not time:
        return 0
    seconds = 0
    for i, part in enumerate(time.split(":")[::-1]):
        if i > 2:
            raise ValueError(f"Expected format: hh:mm:ss. Received {time}.")
        seconds += int(part or 0) * (60 ** i)
    return seconds


def seconds_to_length(seconds: int) -> str:
    i = 2
    parts = []
    while i >= 0:
        parts.append(str(seconds // (60 ** i)).zfill(2))
        seconds = seconds % (60 ** i)
        i -= 1
    return ":".join(parts)


def penalty_score(track: Track, count: int, playlist: List[Track]) -> float:
    last_artist = playlist[-1].artist if playlist else ""
    score = 0.7 * (track.artist == last_artist)
    score += (0.3 * (count / len(playlist))) if playlist else 0
    return score


def dfs(
    vertex: Vertex,
    playlist: List[Track],
    penalty: Dict[str, int],
    duration: Optional[int] = None,
) -> None:
    if duration and sum(t.length for t in playlist) >= duration:
        return
    if vertex.value:
        vertex.value = sorted(
            vertex.value,
            key=lambda i: penalty_score(i, penalty[i.artist], playlist),
            reverse=True,
        )
        to_add = vertex.value.pop()
        playlist.append(to_add)
        penalty[to_add.artist] += 1
    if not vertex.value:
        return
    for neighbor in vertex.neighbors.values():
        if vertex.value:
            dfs(neighbor, playlist, penalty, duration=duration)


def score_bpm(current: int, last: int) -> float:
    outside = current > (1 + THRESHOLD) or current < (1 - THRESHOLD)
    return outside * abs(last - current)


def traverse_graph(
    graph: Graph, duration: Optional[int] = None
) -> List[Track]:
    playlist: List[Track] = []
    vertex = None
    penalty: Dict[str, int] = defaultdict(int)
    while any(v for v in graph if v.value):
        # First start at the center, then try to find a vertex
        # within the range of the last added track's BPM.
        if duration and sum(t.length for t in playlist) >= duration:
            break
        if not vertex:
            sorted_keys = sorted(graph.vertices)
            vertex = graph[sorted_keys[len(sorted_keys) // 2]]
        else:
            sorted_keys = sorted(
                [v.key for v in graph if v.value],
                key=lambda i: score_bpm(i, playlist[-1].bpm),
            )
            vertex = graph[sorted_keys[0]]
        dfs(vertex, playlist, penalty, duration=duration)
    return playlist


def create_playlist(library: Set, duration: Optional[int] = None):
    buckets: Dict[int, List[Track]] = defaultdict(list)
    graph = Graph()
    # Partition tracks by their BPM.
    for track in library:
        buckets[int(track.bpm)].append(track)
    for bpm_a in buckets:
        for bpm_b in buckets:
            if bpm_a * (1 - THRESHOLD) <= bpm_b <= bpm_a * (1 + THRESHOLD):
                graph.add_edge(bpm_a, buckets[bpm_a], bpm_b, buckets[bpm_b])
            else:
                graph.add_vertex(bpm_a, buckets[bpm_a])
                graph.add_vertex(bpm_b, buckets[bpm_b])
    playlist = traverse_graph(graph, duration=duration)
    return playlist


def create_args():
    parser = argparse.ArgumentParser(
        description="Create a playlist sorted by BPM"
    )
    parser.add_argument("library_file", type=str, help="Path to library file")
    parser.add_argument("out_file", type=str, help="Outfile to save results")
    parser.add_argument(
        "--duration",
        type=lambda i: int(i) * 60,
        help="Playlist length in minutes",
    )
    return parser


def parse_file(track_file: str) -> Set:
    library = set()
    with open(track_file, "r") as f:
        reader = csv.reader(f, delimiter=DELIMITER)
        for line in reader:
            track = Track(
                title=line[0],
                artist=line[1],
                album=line[2],
                bpm=int(line[3]),
                length=length_to_seconds(line[4]),
            )
            library.add(track)
    return library


def write_playlist(playlist: List[Track], out_file: str) -> None:
    with open(out_file, "w") as f:
        writer = csv.writer(f, delimiter=DELIMITER)
        writer.writerow(["title", "artist", "album", "bpm", "length"])
        for track in playlist:
            line = [
                track.title,
                track.artist,
                track.album,
                str(track.bpm),
                seconds_to_length(track.length),
            ]
            writer.writerow(line)


def main() -> None:
    args = create_args().parse_args()
    library = parse_file(args.track_file)
    playlist = create_playlist(library, args.duration)
    write_playlist(playlist, args.out_file)


if __name__ == "__main__":
    main()
