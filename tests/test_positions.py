from stegx.core.positions import generate_positions


def test_positions_are_deterministic():

    positions_one = generate_positions(
        1000,
        100,
        "mysecretkey",
    )

    positions_two = generate_positions(
        1000,
        100,
        "mysecretkey",
    )

    assert positions_one == positions_two


def test_different_keys_generate_different_positions():

    positions_one = generate_positions(
        1000,
        100,
        "key_one",
    )

    positions_two = generate_positions(
        1000,
        100,
        "key_two",
    )

    assert positions_one != positions_two


def test_correct_number_of_positions():

    positions = generate_positions(
        1000,
        100,
        "mysecretkey",
    )

    assert len(positions) == 100


def test_positions_are_unique():

    positions = generate_positions(
        1000,
        100,
        "mysecretkey",
    )

    assert len(positions) == len(set(positions))


def test_positions_are_within_bounds():

    total_positions = 1000

    positions = generate_positions(
        total_positions,
        100,
        "mysecretkey",
    )

    assert all(
        0 <= position < total_positions
        for position in positions
    )