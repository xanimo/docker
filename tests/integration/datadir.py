#!/usr/bin/env python3
# Copyright (c) 2021 The Dogecoin Core developers
"""
Test datadir creation, and that files keep the operator's ownership
"""

import contextlib
import os
import shutil
import stat
import tempfile

from .framework.test_runner import TestRunner

# Mount point used inside the container for the host directory under test.
# Not the default datadir, so that creation is actually exercised.
MOUNT_POINT = "/mnt/host"

class DatadirTest(TestRunner):
    """Datadir creation and runtime ownership test"""

    def run_test(self):
        """Check runtime privileges, datadir creation and its ownership"""
        runtime_uid = self.get_runtime_uid()

        if runtime_uid == 0:
            raise AssertionError("container runs as root")

        # Default runtime user owns what it creates.
        self.ensure_datadir_created(None, runtime_uid)

        # An operator overriding the uid keeps ownership of their own files,
        # which is the whole point of not shipping setuid binaries.
        self.ensure_datadir_created("1001:0", 1001)

    def get_runtime_uid(self):
        """Return the uid the container runs as by default"""
        result = self.run_command([], ["sh", "-c", "id -u"])
        return int(result.stdout.decode("utf-8").strip())

    def ensure_datadir_created(self, user, expected_uid):
        """
        Run a dogecoin executable with a datadir that does not exist yet and
        assert the entrypoint created it as expected_uid.
        """
        with self.host_directory() as host_dir:
            datadir = f"{ MOUNT_POINT }/datadir"

            # `-?` makes the executable print help and exit, after the
            # entrypoint has already created the datadir.
            self.run_command([], ["dogecoin-cli", f"-datadir={ datadir }", "-?"],
                    user=user,
                    volumes=[f"{ host_dir }:{ MOUNT_POINT }"])

            created = os.path.join(host_dir, "datadir")

            if not os.path.isdir(created):
                raise AssertionError(f"entrypoint did not create { datadir }")

            owner = os.stat(created).st_uid

            if owner != expected_uid:
                text = (f"datadir created by uid { owner }, "
                        f"expected { expected_uid }")
                raise AssertionError(text)

    @staticmethod
    @contextlib.contextmanager
    def host_directory():
        """
        Provide a world-writable host directory for the container to write
        into, and remove it afterwards regardless of who owns its contents.
        """
        host_dir = tempfile.mkdtemp()

        try:
            # The container writes as a uid unrelated to the test runner.
            os.chmod(host_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            yield host_dir
        finally:
            shutil.rmtree(host_dir, ignore_errors=True)

if __name__ == '__main__':
    DatadirTest().main()
