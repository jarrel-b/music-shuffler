import argparse
from collections import defaultdict

from typing import Optional, Dict, NamedTuple, List, Set

THRESHOLD = 0.05
DELIMITER = "\t"
HEADERS = ["title", "artist", "album", "bpm", "length"]

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
        self.predeccesor: Optional[Vertex] = None

    def add_neighbor(self, neighbor) -> None:
        self.neighbors[neighbor.key] = neighbor


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
        self.vertices[from_key].add_neighbor(self.vertices[to_key])

    def __getitem__(self, key):
        return self.vertices[key]

    def __iter__(self):
        return iter(self.vertices.values())


def score(track: Track, count: int, playlist: List[Track]) -> float:
    last_artist = playlist[-1].artist if playlist else ""
    score = 0.7 * (track.artist == last_artist)
    score += (0.3 * (count / len(playlist))) if playlist else 0
    return score


def dfs(
    vertex: Vertex,
    playlist: List[Track],
    penalty: Dict[str, int],
    duration: Optional[int] = None,
    total: int = 0,
) -> None:
    if vertex.value:
        if duration and total >= duration:
            return
        vertex.value = sorted(
            vertex.value,
            key=lambda i: score(i, penalty[i.artist], playlist),
            reverse=True,
        )
        to_add = vertex.value.pop()
        playlist.append(to_add)
        total += to_add.length
        penalty[to_add.artist] += 1
    if not vertex.value:
        return
    for neighbor in vertex.neighbors.values():
        if vertex.value:
            dfs(neighbor, playlist, penalty, duration=duration, total=total)


def in_bpm_range(bpm_a: int, bpm_b: int) -> bool:
    return bpm_a * (1 - THRESHOLD) <= bpm_b <= bpm_a * (1 + THRESHOLD)


def traverse_graph(graph: Graph, duration: Optional[int] = None) -> List[Track]:
    playlist: List[Track] = []
    vertex = None
    penalty: Dict[str, int] = defaultdict(int)
    while any(v for v in graph if v.value):
        # First start at the center, then try to find a vertex
        # within the range of the last added track's BPM.
        if not vertex:
            sorted_keys = sorted(graph.vertices)
            vertex = graph[sorted_keys[len(sorted_keys) // 2]]
        else:
            sorted_keys = sorted(
                (v.key for v in graph if v.value),
                key=lambda i: in_bpm_range(playlist[-1].bpm, i),
                reverse=True,
            )
            vertex = graph[sorted_keys[0]]
        dfs(vertex, playlist, penalty, duration=duration)
    return playlist


def create_playlist(library: Set, duration: int = Optional[int]):
    buckets: Dict[int, List[Track]] = defaultdict(list)
    graph = Graph()
    # Partition tracks by their BPM.
    for track in library:
        buckets[int(track.bpm)].append(track)
    for bpm_a in buckets:
        for bpm_b in buckets:
            if bpm_a == bpm_b:
                continue
            if in_bpm_range(bpm_a, bpm_b):
                graph.add_edge(bpm_a, buckets[bpm_a], bpm_b, buckets[bpm_b])
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
        dest="duration",
        type=int,
        help="Playlist length in minutes",
    )
    return parser


def parse_file(track_file: str) -> Set:
    library = set()
    with open(track_file, "r") as f:
        for line in f:
            args = line.split(DELIMITER)
            track = Track(
                title=args[0],
                artist=args[1],
                album=args[2],
                bpm=int(args[3]),
                length=int(args[4]),
            )
            library.add(track)
    return library


def write_playlist(playlist: List[Track], out_file: str) -> None:
    with open(out_file, "w") as f:
        f.write(DELIMITER.join(HEADERS) + "\n")
        for track in playlist:
            line = DELIMITER.join([
                track.title,
                track.artist,
                track.album,
                str(track.bpm),
                str(track.length),
            ]) + "\n"
            f.write(line)


def main() -> None:
    args = create_args().parse_args()
    library = parse_file(args.track_file)
    playlist = create_playlist(library, args.duration)
    write_playlist(playlist, args.out_file)


if __name__ == "__main__":
    main()
