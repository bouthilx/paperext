from paperext.config import CFG


def auth_headers():
    """Authorization headers for the Paperoni API.

    The Bearer token is read from ``CFG.paperoni.token``. Keep that empty in the
    tracked config and provide the value at runtime via the
    ``PAPEREXT_PAPERONI_TOKEN`` environment variable. Obtain the token from a
    logged-in Paperoni session.
    """
    token = CFG.paperoni.token
    assert token, (
        "No Paperoni API token set. Export PAPEREXT_PAPERONI_TOKEN with a Bearer "
        "token from a logged-in Paperoni session (see config.mdl.ini [paperoni])."
    )
    return {"Authorization": f"Bearer {token}"}
