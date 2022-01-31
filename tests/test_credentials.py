import os.path
import shutil
import subprocess
import sys
import tempfile

import pytest

from git_credentials import GitCredentials, GitCredentialDescription, GitCredentialNotStoredError, GitCredentialError

PROTOCOL = "https"
HOST = "example.org"
PATH = "/test123"
USERNAME = "success"
PASSWORD = "youwin"
HELPER_SUCCESS_FILL = "ok_fill"
HELPER_FAIL_FILL = "fail_fill"
HELPER_SUCCESS_STORE =  'protocol=https\n' \
                        'host=example.org\n' \
                        'path=/test123\n' \
                        'username=success\n' \
                        'password=youwin\n'
HELPER_SUCCESS_ERASE = "reject\n" + HELPER_SUCCESS_STORE


@pytest.fixture
def credentials():
    with tempfile.TemporaryDirectory() as dirname:
        cred_helper_py_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'bin', 'dummy_credential_helper.py'
        ))
        debug_helper_outfile = os.path.join(dirname, "out.log")
        credential_helper_path = f"!{sys.executable} '{cred_helper_py_path}' '{debug_helper_outfile}' $@"

        # Create the Git repo
        gitp = (shutil.which("git"), "-C", dirname)
        gitkw = {"check": True, "stderr": subprocess.DEVNULL, "stdout": subprocess.DEVNULL}
        subprocess.run([*gitp, "init"], **gitkw)
        subprocess.run([*gitp, "config", "credential.helper", credential_helper_path])
        subprocess.run([*gitp, "config", "credential.useHttpPath", "1"])

        credentials = GitCredentials(dirname)
        yield credentials, debug_helper_outfile


def _read(path):
    with open(path) as f:
        return f.read()


def test_fill_success(credentials):
    (credentials, helper_out_path) = credentials
    req = credentials.fill(GitCredentialDescription(
        protocol=PROTOCOL,
        host=HOST,
        path=PATH
    ))

    assert req.protocol == PROTOCOL
    assert req.host == HOST
    assert req.path == PATH
    assert req.username == USERNAME
    assert req.password == PASSWORD
    assert HELPER_SUCCESS_FILL == _read(helper_out_path)


def test_fill_unknown(credentials):
    (credentials, helper_out_path) = credentials
    with pytest.raises(GitCredentialNotStoredError):
        credentials.fill(GitCredentialDescription(
            protocol=PROTOCOL,
            host="invalid",
            path=PATH
        ))
    assert HELPER_FAIL_FILL == _read(helper_out_path)


def test_fill_error(credentials):
    (credentials, helper_out_path) = credentials
    with pytest.raises(GitCredentialError) as excinfo:
        credentials.fill(GitCredentialDescription(
            protocol="\n",
            host="\n\n"
        ))
    assert not isinstance(excinfo.value, GitCredentialNotStoredError)
    assert not os.path.exists(helper_out_path)


def test_approve(credentials):
    (credentials, helper_out_path) = credentials
    credentials.approve(GitCredentialDescription(
        protocol=PROTOCOL,
        host=HOST,
        path=PATH,
        username=USERNAME,
        password=PASSWORD
    ))

    assert HELPER_SUCCESS_STORE == _read(helper_out_path)


def test_reject(credentials):
    (credentials, helper_out_path) = credentials
    credentials.reject(GitCredentialDescription(
        protocol=PROTOCOL,
        host=HOST,
        path=PATH,
        username=USERNAME,
        password=PASSWORD
    ))

    assert HELPER_SUCCESS_ERASE == _read(helper_out_path)
