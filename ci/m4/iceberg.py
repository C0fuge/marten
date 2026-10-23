#!/usr/bin/env python3
"""Iceberg helpers for the m4 Iceberg variant (ci/m4/stack.sh iceberg, m4.py check 11).

    iceberg.py setup TPCH_DIR      namespace `ice` in the REST catalog (warehouse s3://lake/parquet/_iceberg on MinIO):
                                   ice.lineitem, ice.orders (TPC-H SF1, rewritten by pyiceberg, several snapshots),
                                   ice.ren (column renamed between two appends), ice.t (1 row, check 11 commits to it);
                                   ice.del (position deletes) is written by Spark in `stack.sh iceberg`

REST catalog on http://127.0.0.1:8181 (apache/iceberg-rest-fixture), MinIO on http://127.0.0.1:9000 with
$MINIO_ROOT_USER / $MINIO_ROOT_PASSWORD.
"""
import os, sys

URL = os.environ.get("M4_ICEBERG_URL", "http://127.0.0.1:8181")
NS = "ice"


def cat():
    from pyiceberg.catalog import load_catalog
    return load_catalog("m4", **{"type": "rest", "uri": URL, "s3.endpoint": "http://127.0.0.1:9000",
                                 "s3.access-key-id": os.environ["MINIO_ROOT_USER"],
                                 "s3.secret-access-key": os.environ["MINIO_ROOT_PASSWORD"],
                                 "s3.region": "us-east-1", "s3.path-style-access": "true"})


def rows(ids):
    import pyarrow as pa
    return pa.table({"id": pa.array(ids, pa.int64()), "v": pa.array([f"v{i}" for i in ids])})


def append_t(ids):
    """Commit rows to ice.t (one snapshot); returns the new snapshot id."""
    t = cat().load_table(f"{NS}.t")
    t.append(rows(ids))
    return t.current_snapshot().snapshot_id


def load_tpch(c, src, name, batch_rows):
    import pyarrow.dataset as ds
    d = ds.dataset(os.path.join(src, name), format="parquet")
    t = c.create_table(f"{NS}.{name}", schema=d.schema)
    n = 0
    for b in d.to_batches(batch_size=batch_rows):
        import pyarrow as pa
        t.append(pa.Table.from_batches([b]))
        n += b.num_rows
    print(f"{NS}.{name}: {n} rows, {len(t.snapshots())} snapshots, location {t.location()}")


def setup(tpch):
    import pyarrow as pa
    c = cat()
    c.create_namespace_if_not_exists(NS)
    load_tpch(c, tpch, "orders", 600_000)
    load_tpch(c, tpch, "lineitem", 1_500_000)
    # ice.ren: rows 1-3 written as (id, old_name), the column renamed to new_name, rows 4-5 written after it
    t = c.create_table(f"{NS}.ren", schema=pa.schema([("id", pa.int64()), ("old_name", pa.string())]))
    t.append(pa.table({"id": pa.array([1, 2, 3], pa.int64()), "old_name": ["a", "b", "c"]}))
    with t.update_schema() as u:
        u.rename_column("old_name", "new_name")
    t = c.load_table(f"{NS}.ren")
    t.append(pa.table({"id": pa.array([4, 5], pa.int64()), "new_name": ["d", "e"]}))
    t = c.create_table(f"{NS}.t", schema=rows([1]).schema)
    t.append(rows([1]))
    print("iceberg tables:", sorted(".".join(i) for i in c.list_tables(NS)))


def summary(name):
    """Summary of the current snapshot of ice.<name> (check 11 notes; delete-file counts)."""
    s = cat().load_table(f"{NS}.{name}").current_snapshot()
    return dict(s.summary.additional_properties, operation=s.summary.operation.value) if s else {}


if __name__ == "__main__":
    if sys.argv[1:2] == ["setup"]:
        setup(sys.argv[2])
    elif sys.argv[1:2] == ["summary"]:
        print(summary(sys.argv[2]))
    else:
        sys.exit(__doc__)
