import importlib
from unittest.mock import patch

from pytest import CaptureFixture

from linodecli.plugins import PluginContext

# Non-importable package name
plugin = importlib.import_module("linodecli.plugins.image-upload")


def test_print_help(capsys: CaptureFixture):
    try:
        plugin.call(["--help"], None)
    except SystemExit as err:
        assert err.code == 0

    captured_text = capsys.readouterr().out
    assert "The image file to upload" in captured_text
    assert "The region to upload the image to" in captured_text


def test_no_file(mock_cli, capsys: CaptureFixture):
    try:
        plugin.call(
            ["--label", "cool", "blah.txt"],
            PluginContext("REALTOKEN", mock_cli),
        )
    except SystemExit as err:
        assert err.code == 2

    captured_text = capsys.readouterr().out
    assert "No file at blah.txt" in captured_text


@patch("os.path.isfile", lambda a: True)
@patch("os.path.getsize", lambda a: plugin.MAX_UPLOAD_SIZE + 1)
def test_file_too_large(mock_cli, capsys: CaptureFixture):
    args = ["--label", "cool", "blah.txt"]
    ctx = PluginContext("REALTOKEN", mock_cli)

    try:
        plugin.call(args, ctx)
    except SystemExit as err:
        assert err.code == 2

    captured_text = capsys.readouterr().out
    assert "File blah.txt is too large" in captured_text


@patch("os.path.isfile", lambda a: True)
@patch("os.path.getsize", lambda a: 1)
def test_unauthorized(mock_cli, capsys: CaptureFixture):
    args = ["--label", "cool", "blah.txt"]

    mock_cli.call_operation = lambda *a: (401, None)

    ctx = PluginContext("REALTOKEN", mock_cli)

    try:
        plugin.call(args, ctx)
    except SystemExit as err:
        assert err.code == 3

    captured_text = capsys.readouterr().out
    assert "Your token was not authorized to use this endpoint" in captured_text


@patch("os.path.isfile", lambda a: True)
@patch("os.path.getsize", lambda a: 1)
def test_non_beta(mock_cli, capsys: CaptureFixture):
    args = ["--label", "cool", "blah.txt"]

    mock_cli.call_operation = lambda *a: (404, None)

    ctx = PluginContext("REALTOKEN", mock_cli)

    try:
        plugin.call(args, ctx)
    except SystemExit as err:
        assert err.code == 4

    captured_text = capsys.readouterr().out
    assert (
        "It looks like you are not in the Machine Images Beta" in captured_text
    )


@patch("os.path.isfile", lambda a: True)
@patch("os.path.getsize", lambda a: 1)
def test_non_beta(mock_cli, capsys: CaptureFixture):
    args = ["--label", "cool", "blah.txt"]

    mock_cli.call_operation = lambda *a: (404, None)

    ctx = PluginContext("REALTOKEN", mock_cli)

    try:
        plugin.call(args, ctx)
    except SystemExit as err:
        assert err.code == 4

    captured_text = capsys.readouterr().out
    assert (
        "It looks like you are not in the Machine Images Beta" in captured_text
    )


@patch("os.path.isfile", lambda a: True)
@patch("os.path.getsize", lambda a: 1)
def test_failed_upload(mock_cli, capsys: CaptureFixture):
    args = ["--label", "cool", "blah.txt"]
    mock_cli.call_operation = lambda *a: (500, "it borked :(")

    ctx = PluginContext("REALTOKEN", mock_cli)

    try:
        plugin.call(args, ctx)
    except SystemExit as err:
        assert err.code == 3

    captured_text = capsys.readouterr().out
    assert (
        "Upload failed with status 500; response was it borked :("
        in captured_text
    )
