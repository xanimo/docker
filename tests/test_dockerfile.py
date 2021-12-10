import sys
import os
import pytest
from entrypoint_hook import CommandNotFound

EXECUTABLES_FOLDER = "/usr/local/bin/"

def abs_path(executable):
    """Build manually (expected) executable absolute path"""
    return os.path.join(EXECUTABLES_FOLDER, executable)

def test_entrypoint_executables(hook):
    """
    Basic test without configuration to check
    if entrypoint run each dogecoin executables.
    """
    ## Constant variable for test
    test_environ = {
        "DATADIR" : "/dogecoin/.dogecoin",
        "USER" : "dogecoin",
        "PATH" : os.environ["PATH"],
            }

    result_environ = {
        "USER" : "dogecoin",
        "PATH" : os.environ["PATH"],
            }

    ## Test basic command with `dogecoind`
    test_args = ["dogecoind"]

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-printtoconsole",
            ]
    hook.test(test_args, test_environ, result_args, result_environ)
    assert hook.result == hook.reference, hook.error_msg()
    
    ## Test empty command with `dogecoin-qt`
    test_args = ["dogecoin-qt"]

    result_args = [
            abs_path("dogecoin-qt"),
            "-datadir=/dogecoin/.dogecoin",
            "-printtoconsole",
            ]

    hook.test(test_args, test_environ, result_args, result_environ)
    assert hook.result == hook.reference, hook.error_msg()

    ## Test empty command with `dogecoin-cli`
    test_args = ["dogecoin-cli"]

    result_args = [
            abs_path("dogecoin-cli"),
            "-datadir=/dogecoin/.dogecoin",
            ]

    hook.test(test_args, test_environ, result_args, result_environ)
    assert hook.result == hook.reference, hook.error_msg()

    ## Test basic command with `dogecoin-tx`
    tx_result_env = {
        "USER" : "dogecoin",
        "PATH" : os.environ["PATH"],
        "DATADIR" : "/dogecoin/.dogecoin",
            }

    test_args = ["dogecoin-tx"]

    result_args = [
            abs_path("dogecoin-tx"),
            ]
    hook.test(test_args, test_environ, result_args, tx_result_env)
    assert hook.result == hook.reference, hook.error_msg()

def test_invalid_command(hook):
    test_args = ["dogecoindx"]

    with pytest.raises(CommandNotFound):
        hook.entrypoint(test_args, os.environ)

def test_environ(hook):
    """
    Verify if environment is converted to arguments,
    control that arguments are removed from the environment.
    """
    #Control environment variables with values
    test_args = ["dogecoind"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            "MAXCONNECTIONS" : "150",
            "PAYTXFEE" : "0.01"
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-paytxfee=0.01",
            "-maxconnections=150",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

    #Control environment variables with empty values
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            "TESTNET" : "",
            "DAEMON" : "",
            }

    result_args = [
            abs_path("dogecoind"),
            "-daemon",
            "-datadir=/dogecoin/.dogecoin",
            "-testnet",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

def test_arguments(hook):
    """Verifying arguments are being kept appropriatly"""
    #Verify arguments with values
    test_args = ["dogecoind", "-maxconnections=150", "-paytxfee=0.01"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-maxconnections=150",
            "-paytxfee=0.01",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

    #Verify arguments without values
    test_args = ["dogecoind", "-daemon", "-testnet"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-daemon",
            "-testnet",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

    #Mixing arguments with and without values
    test_args = ["dogecoind", "-daemon", "-maxconnections=150"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-daemon",
            "-maxconnections=150",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

def test_arguments_double_dash(hook):
    """Check arguments formates with double-dash like `--testnet`"""
    test_args = ["dogecoind", "--maxconnections=150", "--paytxfee=0.01"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "--maxconnections=150",
            "--paytxfee=0.01",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

def test_mixing_argument_and_env(hook):
    """Configure container with arguments and environment variables"""
    test_args = ["dogecoind", "-maxconnections=150", "-daemon"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            "TESTNET" : "",
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-maxconnections=150",
            "-daemon",
            "-testnet",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

def test_equal_argv_and_env(hook):
    """Check arguments and environment with identical variables"""
    test_args = ["dogecoind", "-maxconnections=150", "-daemon"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            "MAXCONNECTIONS" : "150",
            "DAEMON" : "",
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-maxconnections=150",
            "-maxconnections=150",
            "-daemon",
            "-daemon",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

    #Same variable with different value for env & arguments.
    test_args = ["dogecoind", "-maxconnections=130", "-daemon"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            "MAXCONNECTIONS" : "150",
            "DAEMON" : "1",
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-maxconnections=130",
            "-maxconnections=150",
            "-daemon",
            "-daemon=1",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

def test_help_debug(hook):
    """
    Test option with dash like `-help-debug` if working
    properly in environment.
    """
    test_args = ["dogecoind"]
    test_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            "DATADIR" : "/dogecoin/.dogecoin",
            "HELP_DEBUG" : "",
            }

    result_args = [
            abs_path("dogecoind"),
            "-datadir=/dogecoin/.dogecoin",
            "-help-debug",
            "-printtoconsole",
            ]
    result_env = {
            "USER" : "dogecoin",
            "PATH" : os.environ['PATH'],
            }
    hook.test(test_args, test_env, result_args, result_env)
    assert hook.result == hook.reference, hook.error_msg()

def test_files_metadata(host):
    """Verify all image files generated by the Dockerfile"""
    dogecoind = host.file(abs_path("dogecoind"))
    assert dogecoind.user == "dogecoin"
    assert dogecoind.group == "dogecoin"
    assert dogecoind.mode == 0o4555

    dogecoinqt = host.file(abs_path("dogecoin-qt"))
    assert dogecoinqt.user == "dogecoin"
    assert dogecoinqt.group == "dogecoin"
    assert dogecoinqt.mode == 0o4555

    dogecointx = host.file(abs_path("dogecoin-tx"))
    assert dogecointx.user == "dogecoin"
    assert dogecointx.group == "dogecoin"
    assert dogecointx.mode == 0o4555

    dogecoincli = host.file(abs_path("dogecoin-cli"))
    assert dogecoincli.user == "dogecoin"
    assert dogecoincli.group == "dogecoin"
    assert dogecoincli.mode == 0o4555

    entrypoint_script = host.file(abs_path("entrypoint.py"))
    assert entrypoint_script.user == "root"
    assert entrypoint_script.group == "root"
    assert entrypoint_script.mode == 0o500

def test_datadir(hook, host):
    """
    Verify if datadir can be changed and created proprely.

    Verify datadir metada, if it's owned by script user (dogecoin).
    """
    #Use a unique directory for this test
    test_datadir = "/tmp/datadir_test"
    datadir_argument = f"-datadir={test_datadir}"

    test_args = ["dogecoind", datadir_argument]
    test_environ = {
        "USER" : "dogecoin",
        "PATH" : os.environ["PATH"],
            }

    result_args = [
            abs_path("dogecoind"),
            datadir_argument,
            "-printtoconsole",
            ]
    result_environ = {
        "USER" : "dogecoin",
        "PATH" : os.environ["PATH"],
            }

    #Run test to generate datadir
    hook.test(test_args, test_environ, result_args, result_environ)
    assert hook.result == hook.reference, hook.error_msg()

    #Test datadir metadata
    datadir_folder = host.file(test_datadir)
    assert datadir_folder.user == "dogecoin"
    assert datadir_folder.group == "dogecoin"
    assert datadir_folder.mode == 0o755
