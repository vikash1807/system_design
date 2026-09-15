# Database Indexing & Document Databases --- Quick Revision Notes

## 1. RDBMS Indexing

### What is an index?

An index is a separate data structure maintained by the database to help
find rows efficiently.

Think of it like a book's index:

``` text
Without index:
Query → scan table → find matching rows

With index:
Query → index → find row locations → fetch rows
```

### Example

``` sql
CREATE INDEX idx_orders_user_id
ON orders(user_id);

SELECT *
FROM orders
WHERE user_id = 101;
```

If user `101` has only 250 orders out of millions, the index can avoid
scanning the whole `orders` table.

### Important mental model

The index on `orders.user_id` is about the `orders` table. It does
**not** need to scan the `users` table to find user `101`.

Conceptually:

``` text
orders.user_id index
        ↓
find 101
        ↓
matching order row locations
        ↓
fetch actual orders
```

If the query explicitly joins `users`, then indexes on both sides of the
relationship may help.

------------------------------------------------------------------------

## 2. B-Tree Index

A common RDBMS index is a B-tree.

The useful mental model:

``` text
          [40]
         /    \
 [10,20,30]  [50,60,70]
```

To find `50`:

``` text
50 > 40
  ↓
go right
  ↓
find 50
```

The database navigates the tree instead of checking every index entry.

### Complexity

For a typical B-tree lookup, think roughly:

``` text
O(log N)
```

Do not assume every index operation is automatically O(log N); different
operations and index structures have different behavior.

------------------------------------------------------------------------

## 3. Why `IS NOT NULL` Can Be Worse With an Index

Suppose:

``` text
10,000,000 rows
9,999,000 rows have user_id NOT NULL
```

Query:

``` sql
SELECT *
FROM orders
WHERE user_id IS NOT NULL;
```

Almost the whole table matches.

Using the index may mean:

``` text
index
  ↓
millions of matching entries
  ↓
fetch millions of table rows
```

A sequential scan may simply read the table once.

So:

``` text
Few rows match      → index is often useful
Most rows match     → sequential scan may be cheaper
```

This is related to **selectivity**.

### Selectivity

High selectivity / selective condition:

``` text
10,000,000 rows
250 match
```

Index is likely useful.

Low selectivity:

``` text
10,000,000 rows
9,000,000 match
```

Index may not help.

The query planner decides whether to use the index.

------------------------------------------------------------------------

## 4. Indexes Have a Cost

Indexes improve many reads but are not free.

They require:

-   extra disk/storage
-   index maintenance
-   additional work on INSERT
-   additional work on UPDATE
-   additional work on DELETE

Mental model:

``` text
Indexes
  ↓
faster reads
  +
more storage
  +
more write/maintenance cost
```

Do not index every column blindly.

------------------------------------------------------------------------

# 5. Indexing From a System-Design Perspective

Design indexes around **query/access patterns**, not simply around
columns.

Example:

``` sql
SELECT *
FROM orders
WHERE user_id = 101
ORDER BY created_at DESC
LIMIT 20;
```

A useful index may be:

``` sql
CREATE INDEX idx_orders_user_created
ON orders(user_id, created_at DESC);
```

Conceptually:

``` text
user_id     created_at
-----------------------------
101         newest
101         ...
101         oldest
102         newest
102         ...
```

This lets the database find user `101` and already be positioned around
the newest orders.

### Important principle

Ask:

> What queries does my application execute frequently?

Then design indexes to support those queries.

------------------------------------------------------------------------

# 6. Normalization vs Denormalization

### Normalization

Avoid unnecessary duplicate data.

Example:

``` text
users
----------------
id | name | city

orders
----------------
id | user_id
```

User information exists once.

Benefits:

-   less duplication
-   easier updates
-   better data integrity

### Denormalization

Intentionally duplicate data to make reads simpler/faster.

Example:

``` text
orders
--------------------------------
id | user_id | user_name | city
```

Benefits:

-   fewer joins
-   potentially faster/simpler reads

Costs:

-   duplicate data
-   harder updates
-   consistency problems

### Mental model

``` text
Normalization
→ optimize for data integrity / less duplication

Denormalization
→ optimize for read performance / simpler reads
```

Usually start normalized and denormalize selectively when actual
performance/access patterns justify it.

------------------------------------------------------------------------

# 7. Document Databases

A document database stores data as **documents**, usually JSON-like
structures.

Example:

``` json
{
  "id": 1,
  "name": "Vikash",
  "age": 25,
  "city": "Jaipur"
}
```

Rough mapping:

``` text
Relational DB        Document DB

Database          →  Database
Table             →  Collection
Row               →  Document
Column            →  Field
```

A collection can contain documents with somewhat different fields.

Example:

``` json
{
  "id": 1,
  "name": "Vikash",
  "age": 25
}
```

and:

``` json
{
  "id": 2,
  "name": "Rahul",
  "age": 26,
  "phone": "9876543210"
}
```

### Important

"Schema-less" does NOT mean "no schema".

The database may allow flexible document shapes, but the application
still needs a logical schema.

------------------------------------------------------------------------

# 8. Embedding

Document databases can put related data inside the same document.

Example:

``` json
{
  "id": 1,
  "name": "Vikash",
  "addresses": [
    {
      "type": "home",
      "city": "Jaipur"
    },
    {
      "type": "work",
      "city": "Delhi"
    }
  ]
}
```

This is **embedding**.

The key question is:

> What data is usually read/written together?

If related data is naturally accessed together and has bounded growth,
embedding can be useful.

------------------------------------------------------------------------

# 9. References

Instead of embedding, data can be stored in separate documents.

User:

``` json
{
  "_id": 101,
  "name": "Vikash"
}
```

Order:

``` json
{
  "_id": 5001,
  "user_id": 101,
  "amount": 1500
}
```

This is **referencing**.

Conceptually similar to a foreign-key relationship:

``` text
users._id
    ↑
    |
orders.user_id
```

Use references when:

-   related data grows very large
-   data is independently accessed
-   data is shared by many entities
-   embedding would create unbounded documents

Example:

``` text
User → few addresses
       → embedding may be reasonable

User → millions of orders
       → referencing is better
```

------------------------------------------------------------------------

# 10. Embedding vs Referencing

The most useful question:

> Will this data usually be read together?

If yes:

``` text
consider embedding
```

If no, or if the nested data can grow without bound:

``` text
consider referencing
```

Trade-off:

``` text
Embedding
→ fewer reads/joins
→ simpler access
→ duplication possible
→ large/unbounded documents are problematic

Referencing
→ independent data
→ less duplication
→ more queries/coordination
```

------------------------------------------------------------------------

# 11. Querying a Document Database --- MongoDB Examples

Use MongoDB as the concrete example.

### Equality

SQL:

``` sql
SELECT *
FROM users
WHERE age = 25;
```

MongoDB:

``` javascript
db.users.find({
  age: 25
})
```

### Multiple conditions

SQL:

``` sql
SELECT *
FROM users
WHERE age > 25
  AND city = 'Delhi';
```

MongoDB:

``` javascript
db.users.find({
  age: { $gt: 25 },
  city: "Delhi"
})
```

Common operators:

``` text
$gt   → >
$gte  → >=
$lt   → <
$lte  → <=
$eq   → =
$ne   → !=
$in   → IN
```

### Nested fields

Document:

``` json
{
  "name": "Vikash",
  "address": {
    "city": "Jaipur"
  }
}
```

Query:

``` javascript
db.users.find({
  "address.city": "Jaipur"
})
```

### Arrays

Document:

``` json
{
  "name": "Vikash",
  "skills": ["Python", "Go", "Redis"]
}
```

Query:

``` javascript
db.users.find({
  skills: "Redis"
})
```

### Update

``` javascript
db.users.updateOne(
  { _id: 1 },
  { $set: { age: 26 } }
)
```

Increment:

``` javascript
db.users.updateOne(
  { _id: 1 },
  { $inc: { age: 1 } }
)
```

------------------------------------------------------------------------

# 12. Indexes in Document Databases

The core idea is the same as relational databases.

Without an index:

``` text
collection
   ↓
scan documents
   ↓
find matches
```

With an index:

``` text
query
  ↓
index
  ↓
matching documents
```

Example:

``` javascript
db.users.createIndex({
  age: 1
})
```

Query:

``` javascript
db.users.find({
  age: 25
})
```

### Nested-field index

``` javascript
db.users.createIndex({
  "address.city": 1
})
```

Then:

``` javascript
db.users.find({
  "address.city": "Jaipur"
})
```

### Array index

MongoDB can create a **multikey index** for array fields.

``` javascript
db.users.createIndex({
  skills: 1
})
```

Conceptually:

``` text
Python → document
Go     → document
Redis  → document
```

------------------------------------------------------------------------

# 13. Atomicity in Document Databases

If related data is embedded in one document:

``` json
{
  "order_id": 101,
  "status": "confirmed",
  "items": [...]
}
```

an update to that single document can be atomic.

If related data is split:

``` text
orders document
payments document
```

then updating both creates a multi-document consistency problem.

Example:

``` text
Update order → succeeds
Update payment → fails
```

Potential state:

``` text
order   → shipped
payment → pending
```

Modern document databases such as MongoDB support multi-document
transactions, so this can be handled transactionally.

But good document modeling can reduce the need for multi-document
transactions.

------------------------------------------------------------------------

# 14. Replication

Replication means keeping multiple copies of data.

``` text
             Primary
             /      \
            ↓        ↓
       Secondary  Secondary
```

Writes commonly go to the primary.

Changes are replicated to secondaries.

### Why?

-   high availability
-   failover
-   potentially distributing reads

If primary fails:

``` text
Primary
   X
   ↓
Secondary elected as new primary
```

### Replication lag

After a write:

``` text
Primary    → new value
Secondary  → old value
```

for some period.

The secondary eventually catches up.

This creates possible stale reads.

------------------------------------------------------------------------

# 15. Strong vs Eventual Consistency

### Strong consistency

After a successful write:

``` text
WRITE
 ↓
READ
 ↓
latest value
```

### Eventual consistency

Temporarily:

``` text
WRITE
 ↓
Primary has new value
Replica may have old value
 ↓
replication
 ↓
eventually all replicas agree
```

Eventual consistency can be acceptable for things like:

-   analytics
-   recommendation feeds
-   view counts
-   social activity counters

It is more problematic for things like financial balances.

------------------------------------------------------------------------

# 16. Sharding

Replication:

``` text
creates copies
```

Sharding:

``` text
splits data across machines
```

Example:

``` text
100 million documents

Shard A → part of data
Shard B → part of data
Shard C → part of data
```

Sharding is a form of horizontal scaling.

------------------------------------------------------------------------

# 17. Shard Key

A **shard key** determines how data is distributed/routed across shards.

Example:

``` text
user_id
```

Conceptually:

``` text
user_id = 101
    ↓
Shard B
```

### Important distinction

An index answers:

> How do I find the data efficiently within a database server?

A shard key helps answer:

> Which database server/shard should handle this data/query?

------------------------------------------------------------------------

# 18. Choosing a Shard Key

Do NOT blindly assume:

``` text
user_id is always a good shard key
```

Consider:

1.  data distribution
2.  write distribution
3.  common queries
4.  hotspots
5.  query routing/locality

Example:

``` text
user_id
```

may be good for:

``` text
orders for user 101
```

but bad if one user generates enormous traffic.

Similarly:

``` text
country
```

can be bad if:

``` text
India → 70% of data
USA   → 15%
others → 15%
```

because one shard may become overloaded.

------------------------------------------------------------------------

# 19. Compound Shard Keys

You can use multiple fields as a **compound shard key** in systems that
support them.

Example:

``` text
(user_id, created_at)
```

This is one combined shard key.

It does NOT mean:

``` text
shard independently by user_id
AND
shard independently by created_at
```

Shard-key design still needs to consider both:

``` text
query locality
+
even distribution
```

These goals can conflict.

------------------------------------------------------------------------

# 20. Hashed Sharding

Instead of using the raw value:

``` text
user_id = 101
```

the system can use a hash:

``` text
hash(user_id)
```

Conceptually:

``` text
101 → hash → Shard B
102 → hash → Shard A
103 → hash → Shard C
```

Hashing can improve distribution.

But it may reduce natural locality for queries that want a range or
related keys together.

### Mental model

``` text
Range sharding
→ better locality
→ possible hotspots

Hash sharding
→ better distribution
→ less natural locality
```

------------------------------------------------------------------------

# 21. Scatter-Gather

Suppose the shard key is:

``` text
user_id
```

Query:

``` javascript
db.orders.find({
  user_id: 101
})
```

The system can often route directly:

``` text
user_id = 101
       ↓
Shard B
```

Good.

But:

``` javascript
db.orders.find({
  status: "pending"
})
```

may not tell the system which shard contains the matching documents.

It may need:

``` text
        Query
       /  |  \
      ↓   ↓   ↓
   Shard A B   C
      \   |   /
       \  |  /
        results
          ↓
       merge
```

This is **scatter-gather**.

It can be more expensive.

------------------------------------------------------------------------

# 22. Complete Request Path

For a sharded document database:

``` text
Client
  ↓
API server
  ↓
Database router
  ↓
Shard selection
  ↓
Correct shard
  ↓
Index
  ↓
Documents
  ↓
API
  ↓
Client
```

Two different optimization layers:

``` text
Sharding
→ choose machine(s)

Indexing
→ find data efficiently on those machine(s)
```

------------------------------------------------------------------------

# 23. Most Important Mental Models

### Index

``` text
Index → find rows/documents efficiently
```

### Normalization

``` text
Normalization → reduce duplication
```

### Denormalization

``` text
Denormalization → intentionally duplicate for read/access benefits
```

### Document

``` text
Document → self-contained JSON-like data structure
```

### Embedding

``` text
Embedding → related data lives inside the document
```

### Reference

``` text
Reference → related data lives in another document
```

### Replication

``` text
Replication → copies of data
```

### Sharding

``` text
Sharding → data split across machines
```

### Shard key

``` text
Shard key → determines/routs where data belongs
```

### Consistency

``` text
Strong → reads see latest committed state according to the consistency guarantee

Eventual → replicas may temporarily disagree, but converge
```

------------------------------------------------------------------------

# 24. One Final Architecture Picture

Keep this picture in your head:

``` text
                         APPLICATION
                              |
                              ↓
                    DATABASE ROUTER
                              |
                 ┌────────────┼────────────┐
                 ↓            ↓            ↓
              SHARD A      SHARD B      SHARD C
                 |            |            |
              Primary       Primary       Primary
               /  \          /  \          /  \
              S    S        S    S        S    S
              |    |        |    |        |    |
              └────┴────────┴────┴────────┴────┘
                       REPLICAS
```

Within each shard:

``` text
Query
  ↓
Index
  ↓
Documents
```

So the layers are:

``` text
Sharding
  → distributes data

Replication
  → copies data

Indexes
  → locate data efficiently

Document modeling
  → determines what data lives together
```

This is the core foundation you need before going deeper into
distributed databases.
