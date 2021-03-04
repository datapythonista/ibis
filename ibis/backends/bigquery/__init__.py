"""BigQuery public API."""

from typing import Optional

import google.auth.credentials
import google.cloud.bigquery  # noqa: F401, fail early if bigquery is missing
import pydata_google_auth

import ibis.common.exceptions as com
import ibis.config
from ibis.backends.base import BaseBackend
from ibis.config import options  # noqa: F401

from .client import (
    BigQueryClient,
    BigQueryDatabase,
    BigQueryQuery,
    BigQueryTable,
)
from .compiler import BigQueryDialect, BigQueryQueryBuilder, dialect

try:
    from .udf import udf
except ImportError:
    pass


__all__ = ('compile', 'connect', 'verify', 'udf')


with ibis.config.config_prefix('bigquery'):
    ibis.config.register_option('partition_col', 'PARTITIONTIME')


def compile(expr, params=None):
    """Compile an expression for BigQuery.

    Returns
    -------
    compiled : str

    See Also
    --------
    ibis.expr.types.Expr.compile

    """
    from .compiler import to_sql

    return to_sql(expr, dialect.make_context(params=params))


def verify(expr, params=None):
    """Check if an expression can be compiled using BigQuery."""
    try:
        compile(expr, params=params)
        return True
    except com.TranslationError:
        return False


SCOPES = ["https://www.googleapis.com/auth/bigquery"]
CLIENT_ID = (
    "546535678771-gvffde27nd83kfl6qbrnletqvkdmsese.apps.googleusercontent.com"
)
CLIENT_SECRET = "iU5ohAF2qcqrujegE3hQ1cPt"


def connect(
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    credentials: Optional[google.auth.credentials.Credentials] = None,
    application_name: Optional[str] = None,
) -> BigQueryClient:
    """Create a BigQueryClient for use with Ibis.

    Parameters
    ----------
    project_id : str
        A BigQuery project id.
    dataset_id : str
        A dataset id that lives inside of the project indicated by
        `project_id`.
    credentials : google.auth.credentials.Credentials
    application_name : str
        A string identifying your application to Google API endpoints.

    Returns
    -------
    BigQueryClient

    """
    default_project_id = None

    if credentials is None:
        credentials_cache = pydata_google_auth.cache.ReadWriteCredentialsCache(
            filename="ibis.json"
        )
        credentials, default_project_id = pydata_google_auth.default(
            SCOPES,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            credentials_cache=credentials_cache,
        )

    project_id = project_id or default_project_id

    return BigQueryClient(
        backend=Backend,
        project_id=project_id,
        dataset_id=dataset_id,
        credentials=credentials,
        application_name=application_name,
    )


class Backend(BaseBackend):
    name = 'bigquery'
    builder = BigQueryQueryBuilder
    dialect = BigQueryDialect
    query_class = BigQueryQuery
    database_class = BigQueryDatabase
    table_class = BigQueryTable
    connect = connect
