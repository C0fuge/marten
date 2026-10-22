#!/usr/bin/env python3
"""lakeFS helpers for the m4 lakeFS variant (ci/m4/stack.sh lakefs, m4.py check 10).

    lakefs.py setup TPCH_DIR TYPES_DIR     create repository m4 (storage namespace s3://lakefs/m4 on MinIO), upload the
                                           tables to branch main under parquet/<schema>/, plus lfs/t (1 row), commit

lakeFS on http://127.0.0.1:8000 (API /api/v1, S3 gateway at the root); credentials from $LAKEFS_KEY / $LAKEFS_SECRET,
MinIO's from $MINIO_ROOT_USER / $MINIO_ROOT_PASSWORD.
"""
import base64, io, json, os, sys, urllib.error, urllib.request

URL = os.environ.get("M4_LAKEFS_URL", "http://127.0.0.1:8000")
REPO, BRANCH, PREFIX = "m4", "main", "parquet"


def api(method, path, body=None, ok=(200, 201, 204)):
    auth = base64.b64encode(f"{os.environ['LAKEFS_KEY']}:{os.environ['LAKEFS_SECRET']}".encode()).decode()
    req = urllib.request.Request(URL + "/api/v1" + path, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
            return json.loads(data) if data else None
    except urllib.error.HTTPError as e:
        if e.code in ok:
            return None
        raise RuntimeError(f"lakeFS {method} {path}: {e.code} {e.read()[:500]!r}") from None


def s3(endpoint, key, secret):
    import boto3
    from botocore.config import Config
    try:
        cfg = Config(s3={"addressing_style": "path"}, request_checksum_calculation="when_required",
                     response_checksum_validation="when_required")
    except TypeError:
        cfg = Config(s3={"addressing_style": "path"})
    return boto3.client("s3", endpoint_url=endpoint, region_name="us-east-1", config=cfg,
                        aws_access_key_id=key, aws_secret_access_key=secret)


def gateway():
    return s3(URL, os.environ["LAKEFS_KEY"], os.environ["LAKEFS_SECRET"])


def put(key, body):
    """Upload (stage) bytes to branch main at parquet/<key>."""
    gateway().put_object(Bucket=REPO, Key=f"{BRANCH}/{PREFIX}/{key}", Body=body, ContentLength=len(body))


def delete(key):
    gateway().delete_object(Bucket=REPO, Key=f"{BRANCH}/{PREFIX}/{key}")


def commit(message):
    return api("POST", f"/repositories/{REPO}/branches/{BRANCH}/commits", {"message": message})["id"]


def head():
    return api("GET", f"/repositories/{REPO}/branches/{BRANCH}")["commit_id"]


def parquet_rows(ids):
    """Parquet bytes of table lfs.t (id BIGINT, v VARCHAR) with the given ids."""
    import pyarrow as pa, pyarrow.parquet as pq
    buf = io.BytesIO()
    pq.write_table(pa.table({"id": pa.array(ids, pa.int64()), "v": pa.array([f"v{i}" for i in ids])}), buf)
    return buf.getvalue()


def setup(tpch, types):
    try:
        api("GET", "/user")      # installation.* created the admin user at the first start
    except RuntimeError as e:
        print(f"{e}; running setup_lakefs")
        api("POST", "/setup_lakefs", {"username": "m4", "key": {"access_key_id": os.environ["LAKEFS_KEY"],
                                                                "secret_access_key": os.environ["LAKEFS_SECRET"]}})
        api("GET", "/user")
    m = s3("http://127.0.0.1:9000", os.environ["MINIO_ROOT_USER"], os.environ["MINIO_ROOT_PASSWORD"])
    try:
        m.create_bucket(Bucket="lakefs")
    except m.exceptions.BucketAlreadyOwnedByYou:
        pass
    api("POST", "/repositories", {"name": REPO, "storage_namespace": f"s3://lakefs/{REPO}",
                                  "default_branch": BRANCH}, ok=(409,))
    n = 0
    for src in (tpch, types):
        schema = os.path.basename(src.rstrip("/"))
        for root, _, files in os.walk(src):
            for f in files:
                p = os.path.join(root, f)
                with open(p, "rb") as fh:
                    put(f"{schema}/{os.path.relpath(p, src)}", fh.read())
                n += 1
    put("lfs/t/part-0.parquet", parquet_rows([1]))
    c = commit("m4 data: tpch sf1, types, lfs.t (1 row)")
    print(f"lakeFS repository {REPO}: {n + 1} files on {BRANCH}, commit {c}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["setup"]:
        setup(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
