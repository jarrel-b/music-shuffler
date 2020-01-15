from typing import List

from music_shuffler import main


def create_bpm_bucket(bpm: int, length: int) -> List[main.Track]:
    return [
        main.Track(
            title=None,
            artist=None,
            album=None,
            bpm=bpm,
            length=None,
        )
        for _ in range(length)
    ]


def test_explore_graph_empty_graph():
    graph = main.Graph()
    expected = []

    actual = main.explore_graph(graph)

    assert expected == actual


def test_explore_graph_single_node_no_tracks():
    graph = main.Graph()
    graph.add_vertex(100, [])
    expected = []

    actual = main.explore_graph(graph)

    assert expected == actual


def test_explore_graph_single_node_with_tracks():
    bpm100 = create_bpm_bucket(100, 10)
    graph = main.Graph()
    graph.add_vertex(100, bpm100)
    expected = [
        main.Track(
            title=None,
            artist=None,
            album=None,
            bpm=100,
            length=None,
        ) for _ in range(10)
    ]

    actual = main.explore_graph(graph)

    assert expected == actual


def test_explore_graph_with_nested_children():
    bpm100 = create_bpm_bucket(100, 5)
    bpm95 = create_bpm_bucket(95, 5)
    bpm92 = create_bpm_bucket(92, 5)
    bpm90 = create_bpm_bucket(90, 5)
    bpm105 = create_bpm_bucket(105, 5)
    graph = main.Graph()
    graph.add_edge(100, bpm100, 95, bpm95)
    graph.add_edge(95, bpm95, 92, bpm92)
    graph.add_edge(95, bpm95, 90, bpm90)
    graph.add_edge(100, bpm100, 105, bpm105)
    expected = bpm100 + bpm95 + bpm92 + bpm90 + bpm105

    actual = main.explore_graph(graph)
    assert len(expected) == len(actual)
    for track in expected:
        assert track in actual


def test_explore_graph_creates_no_consecutive_artists():
    artist_a = []
    for _ in range(5):
        artist_a.append(main.Track(
            title=None,
            artist="a",
            album=None,
            bpm=100,
            length=None,
        ))
    artist_b = []
    for _ in range(5):
        artist_b.append(main.Track(
            title=None,
            artist="b",
            album=None,
            bpm=100,
            length=None,
        ))
    artist_c = []
    for _ in range(5):
        artist_c.append(main.Track(
            title=None,
            artist="c",
            album=None,
            bpm=100,
            length=None,
        ))
    graph = main.Graph()
    graph.add_vertex(100, artist_a + artist_b + artist_c)

    actual = main.explore_graph(graph)
    prev = None
    for track in actual:
        if prev:
            assert track.artist != prev.artist
        prev = track


def test_create_playlist_with_empty_library_creates_empty_playlist():
    library = {}
    expected = []

    playlist = main.create_playlist(library)

    assert expected == playlist
