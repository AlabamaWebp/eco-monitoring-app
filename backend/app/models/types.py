from sqlalchemy import BigInteger, Integer

# In MySQL we keep BIGINT ids, while in SQLite tests this becomes INTEGER so PK autoincrement works.
BIGINT_SQL_TYPE = BigInteger().with_variant(Integer, "sqlite")
