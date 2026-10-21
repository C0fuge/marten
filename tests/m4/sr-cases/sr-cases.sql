SELECT count(*), sum(l_extendedprice) FROM tpch.lineitem WHERE l_orderkey IN (SELECT o_orderkey FROM tpch.orders WHERE o_orderdate = DATE '1995-03-15')
SELECT count(*), sum(o_totalprice) FROM tpch.orders WHERE o_orderdate >= DATE '1998-07-01'
SELECT o_orderpriority, count(*), sum(o_totalprice) FROM tpch.orders WHERE o_orderdate >= DATE '1997-01-01' GROUP BY o_orderpriority
SELECT count(*) FROM tpch.orders WHERE o_orderdate >= '1998-08-01'
SELECT n_name FROM tpch.nation WHERE (n_name = 'O''Brien')
SELECT n_name FROM tpch.nation WHERE (n_name = 'O\'Brien')
SELECT n_name FROM tpch.nation WHERE (n_name = 'a "tpch" b')
SELECT n_regionkey FROM "tpch"."nation"
SELECT "n_name" FROM "tpch"."nation" WHERE ("n_nationkey" = 5)
SELECT count(*) FROM tpch.orders WHERE o_orderkey < 1000
SELECT count(*) FROM tpch.orders WHERE o_custkey = 370
SELECT count(*) FROM tpch.orders WHERE o_orderdate = DATE '1995-03-15'
SELECT count(*) FROM tpch.orders WHERE o_orderdate >= DATE '1998-08-01'
SELECT count(*) FROM tpch.orders WHERE o_orderdate BETWEEN DATE '1995-01-01' AND DATE '1995-01-31'
SELECT count(*) FROM tpch.orders WHERE o_orderpriority IN ('1-URGENT','2-HIGH')
SELECT count(*) FROM tpch.orders WHERE o_totalprice > 500000.00
SELECT count(*) FROM tpch.orders WHERE o_totalprice BETWEEN 1000.00 AND 1100.50
SELECT count(*) FROM tpch.orders WHERE o_clerk LIKE 'Clerk#00000000%'
SELECT count(*) FROM tpch.orders WHERE o_comment LIKE '%special requests%'
SELECT count(*) FROM tpch.orders WHERE o_comment IS NULL
SELECT o_orderstatus, count(*), sum(o_totalprice), min(o_orderdate), max(o_orderdate) FROM tpch.orders GROUP BY o_orderstatus ORDER BY o_orderstatus
SELECT l_returnflag, l_linestatus, count(*), sum(l_quantity), sum(l_extendedprice), min(l_shipdate), max(l_shipdate), avg(l_discount) FROM tpch.lineitem GROUP BY l_returnflag, l_linestatus ORDER BY 1, 2
SELECT o_orderkey, o_totalprice, o_orderdate FROM tpch.orders ORDER BY o_totalprice DESC, o_orderkey LIMIT 5
SELECT l_orderkey, l_linenumber, l_extendedprice FROM tpch.lineitem ORDER BY l_extendedprice DESC, l_orderkey, l_linenumber LIMIT 5
SELECT n_name, count(*), sum(o_totalprice) FROM tpch.orders JOIN tpch.customer ON o_custkey = c_custkey JOIN tpch.nation ON c_nationkey = n_nationkey WHERE o_orderdate >= DATE '1998-07-01' GROUP BY n_name ORDER BY n_name LIMIT 5
SELECT count(*), sum(l_extendedprice) FROM tpch.lineitem JOIN tpch.orders ON l_orderkey = o_orderkey WHERE o_orderdate = DATE '1995-03-15'
