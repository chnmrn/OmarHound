from passport_filter.steps.face import detect_face_box, expand_box


def test_detect_face_box_returns_none_without_a_face(synthetic_face):
    assert detect_face_box(synthetic_face) is None


def test_expand_box_grows_symmetrically_around_center():
    box = (100, 100, 50, 50)
    expanded = expand_box(box, image_size=(256, 256), margin=0.4)

    x, y, w, h = expanded
    assert w == 70
    assert h == 70
    assert x == 90
    assert y == 90


def test_expand_box_clamps_to_image_bounds():
    box = (235, 235, 20, 20)
    expanded = expand_box(box, image_size=(256, 256), margin=0.4)

    x, y, w, h = expanded
    assert x + w <= 256
    assert y + h <= 256
