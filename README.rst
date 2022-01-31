Git Credentials
===============

Simple small library to provide an interface around the ``git credential`` Git command.
No dependencies but ``git`` must in the PATH.

Example
-------

.. code-block:: python

    from git_credentials import GitCredentials, GitCredentialDescription, GitCredentialError, GitCredentialNotStoredError

    def test_creds(user, pw):
        ...

    def ask_for_creds():
        ...

    cred = GitCredentials("/path/to/repo")

    try:
        response = cred.fill(GitCredentialDescription(
            protocol="https",
            host="example.com",
            path="/"
        ))
        print(f"Request was successful. Host: {response.host}, User: {response.username}, Password: {response.password}")
        # Test the credentials
        if test_creds(response.username, response.password):
            # Tell Git the credentials are good.
            cred.approve(response)
        else:
            # Otherwise tell it to reject them.
            cred.reject(response)
    except GitCredentialNotStoredError:
        print("Did not know the PW :(")
        # Ask user for PW. You can store it then (after testing it) using approve:
        (user, pw) = ask_for_creds()
        if test_creds(user, pw):
            # Tell Git the credentials are good.
            cred.approve(GitCredentialDescription(
                protocol="https",
                host="example.com",
                path="/",
                username=user,
                password=pw
            ))
    except GitCredentialError:
        # Another misc. error. GitCredentialNotStoredError subclasses this.
        raise
