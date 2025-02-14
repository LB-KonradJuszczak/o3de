#
# Copyright (c) Contributors to the Open 3D Engine Project.
# For complete copyright and license terms please see the LICENSE at the root of this distribution.
#
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#


from logging import getLogger
from typing import Counter
from test_impact import NativeTestImpact, BaseTestImpact, PythonTestImpact
from tiaf_driver import main
import pytest
logging = getLogger("tiaf")


def assert_list_content_equal(list1, list2):
    assert Counter(list1) == Counter(list2)


class ConcreteBaseTestImpact(BaseTestImpact):
    """
    Concrete implementation of BaseTestImpact so that we can execute unit tests on the functionality of BaseTestImpact individually.
    """

    _runtime_type = "base"
    _default_sequence_type = "regular"

    @property
    def default_sequence_type(self):
        """
        Returns default sequence type, defaulting to "regular" for this example.
        """
        return self._default_sequence_type

    @property
    def runtime_type(self):
        return self._runtime_type


class TestTiafInitialiseStorage():

    def test_create_TestImpact_no_s3_bucket_name(self, caplog, tiaf_args, config_data, mocker):
        # given:
        # Default args.
        expected_storage_args = config_data, tiaf_args['suite'], tiaf_args[
            'commit']
        mock_local = mocker.patch(
            "persistent_storage.PersistentStorageLocal.__init__", side_effect=SystemError(), return_value=None)
        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # PersistentStorageLocal should be called with suite, commit and config data as arguments.
        mock_local.assert_called_with(
            *expected_storage_args)

    @pytest.mark.parametrize("bucket_name,top_level_dir,expected_top_level_dir", [("test_bucket", "test_dir", "test_dir\\base")])
    def test_create_TestImpact_s3_bucket_name_supplied(self, caplog, tiaf_args, mocker, bucket_name, top_level_dir, config_data, expected_top_level_dir):
        # given:
        # Default arguments + s3_bucket and s3_top_level_dir being set to the above parameters,
        # and we patch PersistentStorageS3 to intercept the constructor call.
        tiaf_args['s3_bucket'] = bucket_name
        tiaf_args['s3_top_level_dir'] = top_level_dir
        mock_storage = mocker.patch(
            "persistent_storage.PersistentStorageS3.__init__", side_effect=SystemError())

        expected_storage_args = config_data, tiaf_args['suite'], tiaf_args[
            'commit'], bucket_name, expected_top_level_dir, tiaf_args['src_branch']

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # PersistentStorageS3 should be called with config data, commit, bucket_name, top_level_dir and src branch as arguments.
        mock_storage.assert_called_with(*expected_storage_args)

    def test_create_TestImpact_s3_bucket_name_not_supplied(self, caplog, tiaf_args, mock_runtime, default_runtime_args, mocker, config_data):
        # given:
        # Default arguments + s3_bucket and s3_top_level_dir arguments set to none.
        tiaf_args['s3_bucket'] = None
        tiaf_args['s3_top_level_dir'] = None
        mock_storage = mocker.patch(
            "persistent_storage.PersistentStorageS3.__init__", return_value=None)

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # PersistentStorageS3 should not be called.
        mock_storage.assert_not_called()

    def test_create_TestImpact_s3_top_level_dir_bucket_name_not_supplied(self, caplog, tiaf_args, mock_runtime, default_runtime_args, mocker, config_data):
        # given:
        # Default arguments + s3_bucket set to none and s3_top_level_dir is defined.
        tiaf_args['s3_bucket'] = None
        tiaf_args['s3_top_level_dir'] = "test_dir"
        mock_storage = mocker.patch(
            "persistent_storage.PersistentStorageS3.__init__", return_value=None)

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # PersistentStorageS3 should not be called.
        mock_storage.assert_not_called()


class TestTIAFNativeUnitTests():

    @pytest.mark.parametrize("safemode, arg_val", [("on", "on")])
    def test_create_NativeTestImpact_safe_mode_arguments(self, caplog, tiaf_args, mock_runtime, cpp_default_runtime_args, safemode, arg_val):
        # given:
        # Default args + safe_mode set.
        tiaf_args['safe_mode'] = safemode
        cpp_default_runtime_args['safemode'] = "--safemode="+arg_val

        # when:
        # We create a TestImpact object.
        tiaf = NativeTestImpact(tiaf_args)

        # then:
        # tiaf.runtime_args should equal expected args.
        assert_list_content_equal(
            tiaf.runtime_args, cpp_default_runtime_args.values())

    def test_create_NativeTestImpact_no_safe_mode(self, caplog, tiaf_args, mock_runtime, cpp_default_runtime_args):
        # given:
        # Default args + safe_mode set.

        # when:
        # We create a TestImpact object.
        tiaf = NativeTestImpact(tiaf_args)

        # then:
        # tiaf.runtime_args should equal expected args.
        assert_list_content_equal(
            tiaf.runtime_args, cpp_default_runtime_args.values())

    @pytest.mark.parametrize("bucket_name,top_level_dir,expected_top_level_dir", [("test_bucket", "test_dir", "test_dir\\native")])
    def test_create_NativeTestImpact_correct_s3_dir_runtime_type(self, config_data, caplog, tiaf_args, mock_runtime, cpp_default_runtime_args, mocker, bucket_name, top_level_dir, expected_top_level_dir):
        # given:
        # Default args + s3_bucket and s3_top_level_dir set
        tiaf_args['s3_bucket'] = bucket_name
        tiaf_args['s3_top_level_dir'] = top_level_dir
        mock_storage = mocker.patch(
            "persistent_storage.PersistentStorageS3.__init__", side_effect=SystemError())
        expected_storage_args = config_data, tiaf_args['suite'], tiaf_args[
            'commit'], bucket_name, expected_top_level_dir, tiaf_args['src_branch']

        # when:
        # We create a NativeTestImpact object
        tiaf = NativeTestImpact(tiaf_args)

        # then:
        # PersistentStorageS3.__init__ should be called with config data, suite, commit, bucket_name, modified top level dir and src_branch as arguments
        mock_storage.assert_called_with(*expected_storage_args)


class TestTIAFPythonUnitTests():

    @pytest.mark.parametrize("bucket_name,top_level_dir,expected_top_level_dir", [("test_bucket", "test_dir", "test_dir\\python")])
    def test_create_PythonTestImpact_correct_s3_dir_runtime_type(self, config_data, caplog, tiaf_args, mock_runtime, mocker, bucket_name, top_level_dir, expected_top_level_dir):
        # given:
        # Default args + s3_bucket and s3_top_level_dir set
        tiaf_args['s3_bucket'] = bucket_name
        tiaf_args['s3_top_level_dir'] = top_level_dir
        mock_storage = mocker.patch(
            "persistent_storage.PersistentStorageS3.__init__", side_effect=SystemError())
        expected_storage_args = config_data, tiaf_args['suite'], tiaf_args[
            'commit'], bucket_name, expected_top_level_dir, tiaf_args['src_branch']

        # when:
        # We create a PythonTestImpact object
        tiaf = PythonTestImpact(tiaf_args)

        # then:
        # PersistentStorageS3.__init__ should be called with config data, suite, commit, bucket_name, modified top level dir and src_branch as arguments
        mock_storage.assert_called_with(*expected_storage_args)


class TestTIAFBaseUnitTests():

    def test_create_TestImpact_valid_config(self, caplog, tiaf_args, mock_runtime, mocker, default_runtime_args):
        """
        Given default arguments, when we create a TestImpact object, tiaf.runtime_args should be eqaul
        """
        # given:
        # Default arguments.

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.runtime_args should equal our default_runtime_args values.
        assert_list_content_equal(
            tiaf.runtime_args, default_runtime_args.values())

    def test_create_TestImpact_invalid_config(self, caplog, tiaf_args, mock_runtime, tmp_path_factory, default_runtime_args):
        # given:
        # Invalid config file at invalid_file,
        # and setting tiaf_args.config to that path.
        invalid_file = tmp_path_factory.mktemp("test") / "test_file.txt"
        with open(invalid_file, 'w+') as f:
            f.write("fake json")
        tiaf_args['config'] = invalid_file

        # when:
        # We create a TestImpact object.
        # then:
        # It should raise a SystemError.
        with pytest.raises(SystemError) as exc_info:
            tiaf = ConcreteBaseTestImpact(tiaf_args)

    @ pytest.mark.parametrize("branch_name", ["development", "not_a_real_branch"])
    def test_create_TestImpact_src_branch(self, caplog, tiaf_args, mock_runtime, default_runtime_args, branch_name):
        # given:
        # Default args + src_branch set to branch_name.
        tiaf_args['src_branch'] = branch_name

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.source_branch shoudl equal our branch name.
        assert tiaf.source_branch == branch_name

    @ pytest.mark.parametrize("branch_name", ["development", "not_a_real_branch"])
    def test_create_TestImpact_dst_branch(self, caplog, tiaf_args, mock_runtime, default_runtime_args, branch_name):
        # given:
        # Default args + dst_branch set to branch_name.
        tiaf_args['dst_branch'] = branch_name

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.destination_branch should equal our branch name parameter.
        assert tiaf.destination_branch == branch_name

    @ pytest.mark.parametrize("commit", ["9a15f038807ba8b987c9e689952d9271ef7fd086", "foobar"])
    def test_create_TestImpact_commit(self, caplog, tiaf_args, mock_runtime, default_runtime_args, commit):
        # given:
        # Default args + commit set to commit.
        tiaf_args['commit'] = commit

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.destination_commit should equal our commit parameter.
        assert tiaf.destination_commit == commit

    def test_run_Tiaf_mars_index_prefix_is_supplied(self, caplog, tiaf_args, mock_runtime, mocker):
        # given:
        # Default args + mars_index_prefix being provided,
        # and transmit_report_to_mars is patched to intercept the call.
        tiaf_args['mars_index_prefix'] = "test_prefix"
        mock_mars = mocker.patch("mars_utils.transmit_report_to_mars")

        # when:
        # We run Tiaf through the driver.
        with pytest.raises(SystemExit):
            main(tiaf_args)

        # then:
        # Tiaf should call the transmit function.
        mock_mars.assert_called()

    def test_run_Tiaf_mars_index_prefix_is_not_supplied(self, caplog, tiaf_args, mock_runtime, mocker):
        # given:
        # Default_args - mars index is not supplied.
        mock_mars = mocker.patch("mars_utils.transmit_report_to_mars")

        # when:
        # We run tiaf through the driver.
        with pytest.raises(SystemExit):
            main(tiaf_args)

        # then:
        # Tiaf should not call the transmit function.
        mock_mars.assert_not_called()

    def test_create_TestImpact_valid_test_suite_name(self, caplog, tiaf_args, mock_runtime, default_runtime_args):
        # given:
        # Default args

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.runtime_args should equal our default_runtime_ars.
        assert_list_content_equal(
            tiaf.runtime_args, default_runtime_args.values())

    def test_create_TestImpact_invalid_test_suite_name(self, caplog, tiaf_args, mock_runtime, default_runtime_args):
        # given:
        # Default args + suite defined as "foobar" in given args and expected args.
        tiaf_args['suite'] = "foobar"
        default_runtime_args['suite'] = "--suite=foobar"

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.runtime_args should equal expected args.
        assert_list_content_equal(
            tiaf.runtime_args, default_runtime_args.values())

    @ pytest.mark.parametrize("policy", ["continue", "abort", "ignore"])
    def test_create_TestImpact_valid_failure_policy(self, caplog, tiaf_args, mock_runtime, default_runtime_args, policy):
        # given:
        # Default args + test_failure_policy set to policy parameter.
        tiaf_args['test_failure_policy'] = policy
        default_runtime_args['test_failure_policy'] = "--fpolicy="+policy

        # Set src branch to be different than dst branch so that we can get a regular sequence, otherwise TIAF will default to a see sequence and overwrite our failure policy.
        tiaf_args['src_branch'] = 122
        default_runtime_args['sequence'] = "--sequence=regular"
        default_runtime_args['ipolicy'] = "--ipolicy=continue"

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.runtime_args should equal expected args.
        assert_list_content_equal(
            tiaf.runtime_args, default_runtime_args.values())

    def test_create_TestImpact_exclude_file_not_supplied(self, caplog, tiaf_args, mock_runtime, default_runtime_args):
        # given:
        # Default args.

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.runtime_args should equal expected args.
        assert_list_content_equal(
            tiaf.runtime_args, default_runtime_args.values())

    def test_create_TestImpact_exclude_file_supplied(self, caplog, tiaf_args, mock_runtime, default_runtime_args):
        # given:
        # Default args + exclude_file set.
        tiaf_args['exclude_file'] = "testpath"
        default_runtime_args['exclude'] = "--exclude=testpath"

        # when:
        # We create a TestImpact object.
        tiaf = ConcreteBaseTestImpact(tiaf_args)

        # then:
        # tiaf.runtime_args should equal expected args.
        assert_list_content_equal(
            tiaf.runtime_args, default_runtime_args.values())
