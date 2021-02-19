import pandas as pd
import pytest


@pytest.mark.parametrize('distinct', [False, True])
@pytest.mark.only_on_backends(
    ['bigquery', 'impala', 'pandas', 'postrges', 'pyspark']
)
@pytest.mark.skip_backends(['dask'])  # TODO - pandas - #2553
@pytest.mark.xfail_unsupported
def test_union(backend, alltypes, df, distinct):
    result = alltypes.union(alltypes, distinct=distinct).execute()
    expected = df if distinct else pd.concat([df, df], axis=0)

    # Result is not in original order on PySpark backend when distinct=True
    result = result.sort_values(['id'])
    expected = expected.sort_values(['id'])

    backend.assert_frame_equal(result, expected)
