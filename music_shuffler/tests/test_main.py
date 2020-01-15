from typing import List

from music_shuffler import shuffler


def create_bpm_bucket(bpm: int, length: int) -> List[shuffler.Track]:
    return [
        shuffler.Track(
            title="title", artist="artist", album="album", bpm=bpm, length=1
        )
        for _ in range(length)
    ]


def test_traverse_graph_empty_graph():
    graph = shuffler.Graph()
    expected = []

    actual = shuffler.traverse_graph(graph)

    assert expected == actual


def test_traverse_graph_single_node_no_tracks():
    graph = shuffler.Graph()
    graph.add_vertex(100, [])
    expected = []

    actual = shuffler.traverse_graph(graph)

    assert expected == actual


def test_traverse_graph_single_node_with_tracks():
    bpm100 = create_bpm_bucket(100, 10)
    graph = shuffler.Graph()
    graph.add_vertex(100, bpm100)
    expected = [
        shuffler.Track(
            title="title", artist="artist", album="album", bpm=100, length=1
        )
        for _ in range(10)
    ]

    actual = shuffler.traverse_graph(graph)

    assert expected == actual


def test_traverse_graph_with_nested_children():
    bpm100 = create_bpm_bucket(100, 5)
    bpm95 = create_bpm_bucket(95, 5)
    bpm92 = create_bpm_bucket(92, 5)
    bpm90 = create_bpm_bucket(90, 5)
    bpm105 = create_bpm_bucket(105, 5)
    graph = shuffler.Graph()
    graph.add_edge(100, bpm100, 95, bpm95)
    graph.add_edge(95, bpm95, 92, bpm92)
    graph.add_edge(95, bpm95, 90, bpm90)
    graph.add_edge(100, bpm100, 105, bpm105)
    expected = bpm100 + bpm95 + bpm92 + bpm90 + bpm105

    actual = shuffler.traverse_graph(graph)
    assert len(expected) == len(actual)
    for track in expected:
        assert track in actual


def test_traverse_graph_creates_no_consecutive_artists():
    artist_a = []
    for _ in range(5):
        artist_a.append(
            shuffler.Track(
                title=None, artist="a", album=None, bpm=100, length=1,
            )
        )
    artist_b = []
    for _ in range(5):
        artist_b.append(
            shuffler.Track(
                title=None, artist="b", album=None, bpm=100, length=1,
            )
        )
    artist_c = []
    for _ in range(5):
        artist_c.append(
            shuffler.Track(
                title=None, artist="c", album=None, bpm=100, length=1,
            )
        )
    graph = shuffler.Graph()
    graph.add_vertex(100, artist_a + artist_b + artist_c)

    actual = shuffler.traverse_graph(graph)
    prev = None
    for track in actual:
        if prev:
            assert track.artist != prev.artist
        prev = track


def test_create_playlist_with_empty_library_creates_empty_playlist():
    library = {}
    expected = []

    playlist = shuffler.create_playlist(library)

    assert expected == playlist
