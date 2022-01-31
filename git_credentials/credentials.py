import os
import shutil
import subprocess
import tempfile
from configparser import ConfigParser
from typing import Optional, NamedTuple, Dict


class GitCredentialError(Exception):
    pass


class GitCredentialNotStoredError(GitCredentialError):
    pass


class GitCredentialDescription(NamedTuple):
    protocol: str
    host: str
    path: Optional[str] = None

    username: Optional[str] = None
    password: Optional[str] = None


class GitCredentials:
    """A class to wrap around git-credentials. See it's man page for more info."""
    def __init__(self, repository_path: str, env: Optional[Dict[str, str]] = None):
        """Creates a new environment for git-credential commands to run in."""
        self.repository_path = repository_path
        self.env = env if env else os.environ.copy()
        self.env['GIT_TERMINAL_PROMPT'] = '0'

    def fill(self, description: GitCredentialDescription) -> GitCredentialDescription:
        """
        Request a password from Git. The user is NOT interactively asked for the password.
        This command either...

        ... returns a GitCredentialDescription containing the output of `git credential fill`, which
            should contain the requested username and password

        ... raises GitCredentialNotStoredError if the credentials were not stored by Git, meaning
            there was no credential helper configured, the call to the credential helper failed
            or the credential helper did not know the password.

        ... raises GitCredentialError on any other issue invoking Git (probably missing `git` executable,
            self.repository_path not being a repository etc). See the causing exception for details.
        """
        return self._parse_description(str(self._run_credential_cmd("fill", description), 'utf-8'))

    def reject(self, description: GitCredentialDescription) -> None:
        """Turns Git to reject the provided credentials. See the man page for more information."""
        self._run_credential_cmd("reject", description)

    def approve(self, description: GitCredentialDescription) -> None:
        """Turns Git to approve the provided credentials. See the man page for more information."""
        self._run_credential_cmd("approve", description)

    def _run_credential_cmd(self, cmd: str, description: GitCredentialDescription) -> bytes:
        git = shutil.which("git")
        if git is None:
            raise OSError("git not found in PATH.")
        fullcmd = [git, "-C", self.repository_path, "credential", cmd]
        proc = None
        try:
            with tempfile.TemporaryFile('w+b') as stdout:
                with tempfile.TemporaryFile('w+b') as stderr:
                    with tempfile.TemporaryFile('w+b') as stdin:
                        stdin.write(bytes(self._convert_description(description), 'utf-8'))
                        stdin.seek(0)
                        proc = subprocess.Popen(fullcmd, stdin=stdin, stdout=stdout, stderr=stderr, env=self.env)
                        retcode = proc.wait()
                        stderr.seek(0)
                        stdout.seek(0)
                        if cmd == "fill" and retcode == 128:
                            # The command may have failed retrieving the PW from the helper
                            failed_reading = b"terminal prompts disabled" in stderr.read()
                            stderr.seek(0)
                            if failed_reading:
                                raise GitCredentialNotStoredError(description.host)
                        if retcode != 0:
                            raise subprocess.CalledProcessError(retcode, fullcmd, stdout.read(), stderr.read())
                        return stdout.read()
        except subprocess.CalledProcessError as e:
            raise GitCredentialError("The 'git' command returned a non-zero exit code.") from e
        except OSError as e:
            raise GitCredentialError("Failed invoking the 'git' command.") from e
        finally:
            try:
                if proc is not None:
                    proc.kill()
            except Exception:
                pass

    @staticmethod
    def _convert_description(description: GitCredentialDescription) -> str:
        s = f"protocol={description.protocol}\n"
        s += f"host={description.host}\n"
        if description.path:
            s += f"path={description.path}\n"
        if description.username:
            s += f"username={description.username}\n"
        if description.password:
            s += f"password={description.password}\n"
        return s + "\n"

    @staticmethod
    def _parse_description(description_str: str) -> GitCredentialDescription:
        cp = ConfigParser()
        cp.read_string("[desc]\n" + description_str)
        sec = cp["desc"]
        return GitCredentialDescription(
            protocol=sec.get('protocol'),
            host=sec.get('host'),
            path=sec.get('path', None),
            username=sec.get('username', None),
            password=sec.get('password', None),
        )
