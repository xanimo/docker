#!/usr/bin/env python3
# Copyright (c) 2021 The Dogecoin Core developers
"""
Test ownership and permissions of the files installed by the Dockerfile
"""

from .framework.test_runner import TestRunner

# path -> (uid, gid, octal mode)
#
# Everything is root-owned and not writable by the runtime user, so a
# compromised daemon cannot rewrite the binaries it was started from.
# A setuid or setgid bit would appear here as a fourth octal digit.
EXPECTED_METADATA = {
        "/usr/local/bin/dogecoind": (0, 0, "555"),
        "/usr/local/bin/dogecoin-cli": (0, 0, "555"),
        "/usr/local/bin/dogecoin-tx": (0, 0, "555"),
        "/usr/local/bin/entrypoint.py": (0, 0, "555"),
        }

class FilesMetadataTest(TestRunner):
    """Installed files metadata test"""

    def run_test(self):
        """Stat every installed file and compare against expectations"""
        paths = sorted(EXPECTED_METADATA)
        stat_format = "stat -c '%n %u %g %a' " + " ".join(paths)

        result = self.run_command([], ["sh", "-c", stat_format])
        found = self.parse_stat(result.stdout)

        for path, expected in EXPECTED_METADATA.items():
            if path not in found:
                raise AssertionError(f"{ path } is missing from the image")

            if found[path] != expected:
                text = f"{ path }: expected { expected }, found { found[path] }"
                raise AssertionError(text)

        self.ensure_no_special_bits(found)

    @staticmethod
    def parse_stat(cmd_output):
        """Turn stat output into a map of path -> (uid, gid, mode)"""
        found = {}

        for line in cmd_output.decode("utf-8").splitlines():
            if not line.strip():
                continue

            name, uid, gid, mode = line.split()
            found[name] = (int(uid), int(gid), mode)

        return found

    @staticmethod
    def ensure_no_special_bits(found):
        """Assert no file carries a setuid or setgid bit"""
        for path, metadata in found.items():
            mode = metadata[2]

            if len(mode) > 3 and int(mode, 8) & 0o6000:
                text = f"{ path } carries a setuid/setgid bit: mode { mode }"
                raise AssertionError(text)

if __name__ == '__main__':
    FilesMetadataTest().main()
