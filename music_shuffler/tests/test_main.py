import random
from typing import List
from unittest import mock

import pytest

from music_shuffler import shuffler


def create_bpm_bucket(bpm: int, length: int) -> List[shuffler.Track]:
    return [
        shuffler.Track(
            title="title", artist="artist", album="album", bpm=bpm, length=1
        )
        for _ in range(length)
    ]


@pytest.mark.parametrize(
    "time, expected",
    [
        (None, 0),
        ("", 0),
        (0, 0),
        (":0", 0),
        (":00", 0),
        ("0:00", 0),
        ("00:00", 0),
        ("00:00:00", 0),
        ("5", 5),
        (":5", 5),
        (":05", 5),
        (":12", 12),
        ("12:05", 725),
        ("01:00", 60),
        ("12:10:05", 43805),
    ],
)
def test_parse_time_to_int(time, expected):
    actual = shuffler.parse_length(time)

    assert expected == actual


def test_parse_time_invalid_format_raises_error():
    with pytest.raises(ValueError):
        shuffler.parse_length("18:12:10:00")


def test_smoke():
    with mock.patch(
        "music_shuffler.shuffler.create_args", autospec=True
    ) as mock_create_args, mock.patch(
        "music_shuffler.shuffler.parse_file", autospec=True
    ) as mock_parse_file, mock.patch(
        "music_shuffler.shuffler.write_playlist", autospec=True
    ):
        mock_parser = mock.Mock()
        mock_parser.parse_args.return_value = mock.Mock(duration=None)
        mock_create_args.return_value = mock_parser
        library = set()
        for i in range(1000):
            library.add(
                shuffler.Track(
                    title=str(i),
                    artist=str(i),
                    album=str(i),
                    bpm=random.randint(10, 100),
                    length=1,
                )
            )
        mock_parse_file.return_value = library

        shuffler.main()


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
    library = set()
    expected = []

    playlist = shuffler.create_playlist(library)

    assert expected == playlist


def test_create_playlist_with_single_bucket_returns_entire_library():
    library = set()
    for i in "abcdefghijklmnopqrstuvwxyz":
        library.add(
            shuffler.Track(title=i, artist=i, album=i, bpm=100, length=1)
        )

    playlist = shuffler.create_playlist(library)

    for track in library:
        assert track in playlist


def test_create_playlist_with_no_overlapping_bpms_returns_entire_library():
    library = set()
    bpm = 10
    for i in "abcdefghijklmnopqrstuvwxyz":
        library.add(
            shuffler.Track(title=i, artist=i, album=i, bpm=bpm, length=1)
        )
        bpm += 10 * (1 + shuffler.THRESHOLD)

    playlist = shuffler.create_playlist(library)

    for track in library:
        assert track in playlist


def test_create_playlist_duration_lt_library_length_returns_expected():
    library = set()
    for i in range(50):
        library.add(
            shuffler.Track(title=i, artist=i, album=i, bpm=100, length=1)
        )
    duration = 10

    playlist = shuffler.create_playlist(library, duration=10)

    playlist_duration = sum(track.length for track in playlist)
    assert playlist_duration == duration


def test_create_playlist_duration_gt_than_library_length_returns_expected():
    library = set()
    for i in range(50):
        library.add(
            shuffler.Track(title=i, artist=i, album=i, bpm=100, length=1)
        )
    duration = 100

    playlist = shuffler.create_playlist(library, duration=duration)

    playlist_duration = sum(track.length for track in playlist)
    assert playlist_duration == len(library)
