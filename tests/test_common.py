import os
import logging.config
from unittest import mock

from app.utils import common


@mock.patch("logging.config.fileConfig")
@mock.patch("os.path.normpath")
@mock.patch("os.path.join")
@mock.patch("os.path.dirname")
def test_setup_logging(dirname_mock, join_mock, normpath_mock, file_config_mock):
    # Arrange
    fake_dir = "/fake/dir"
    fake_path = "/fake/dir/logging.conf"
    
    dirname_mock.return_value = fake_dir
    join_mock.return_value = fake_path
    normpath_mock.return_value = fake_path

    # Act
    common.setup_logging()

    # Assert
    dirname_mock.assert_called_once_with(common.__file__)
    join_mock.assert_called_once_with(fake_dir, '..', '..', 'logging.conf')
    normpath_mock.assert_called_once_with(fake_path)
    file_config_mock.assert_called_once_with(fake_path, disable_existing_loggers=False)
