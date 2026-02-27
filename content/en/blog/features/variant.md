---
title: "Variant Type in Apache Parquet for Semi-Structured Data"
date: 2026-02-27
description: "Introducing Native Variant Type in Apache Parquet"
author: "[Aihua Xu](https://github.com/aihuaxu), [Andrew Lamb](https://github.com/alamb)"
categories: ["features"]
---

The Apache Parquet community is excited to announce the addition of the **Variant type**—a feature that brings native support for semi-structured data to Parquet, significantly improving efficiency compared to less efficient formats such as JSON. This marks a significant addition to Parquet, demonstrating how the format continues to evolve to meet modern data engineering needs.

While Apache Parquet has long been the standard for structured data where each value has a fixed and known type, handling heterogeneous, nested data often required a compromise: either store it as a costly-to-parse JSON string or flatten it into a rigid schema. The introduction of the Variant logical type provides a native, high-performance solution for semi-structured data that is already seeing rapid uptake across the ecosystem.

---

## What is Variant?

**Variant** is a self-describing data type designed to efficiently store and process semi-structured data—JSON-like documents with arbitrary and evolving schemas.

---

## Why Variant?

Consider a common scenario: storing logged event data that might evolve as new events are added, or fields are added or removed from specific event types. For example, you might have events like:

```json
{"timestamp": "2026-01-15T10:30:00Z", "user": 5, "event": "login"}
{"timestamp": "2026-01-15T11:45:00Z", "user": 5, "event": "purchase", "amount": 99.99}
{"timestamp": "2026-01-15T12:00:00Z", "user": 7, "event": "login", "device": "mobile"}
```

Traditional approaches that store JSON as text strings require full parsing to access any field, making queries slow and resource-intensive. Variant solves this by storing data in a **structured binary format** that enables direct field access through offset-based navigation. Query engines can jump directly to nested fields without deserializing the entire document, dramatically improving performance.

Binary encodings like BSON improve upon plain JSON by storing data in binary format, but they still redundantly store field names like `"timestamp"`, `"user"`, and `"event"` in every row, wasting storage space. Variant is optimized for the common case where multiple values share a similar structure: it avoids redundantly storing repeated field names and standardizes the best practice of **"shredded storage"** for pre-extracting structured subsets.

### Key Benefits

- **Type-Preserving Storage:** Original data types are maintained in their native formats—data types (integers, strings, booleans, timestamps, etc.) are preserved, unlike JSON which has a limited type system with no native support for types like timestamps or integers.

- **Efficient Encoding:** The binary format uses field name deduplication to minimize storage overhead compared to JSON strings or BSON encoding.

- **Fast Query Performance:** Direct offset-based field access provides performance improvements over JSON string parsing. Optional shredding of frequently accessed fields into typed columns further enhances query pruning and predicate pushdown.

- **Schema Flexibility:** No predefined schema is required, allowing documents with different structures to coexist in the same column. This enables seamless schema evolution while maintaining full queryability across all schema variations, while still taking advantage of common structures when present.

---

## Overview of Variant Type in Parquet

Parquet introduced the [Variant logical type](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#variant) in [August 2025](https://github.com/apache/parquet-format/pull/509).

### Variant Encoding

In Parquet, Variant is represented as a logical type and stored physically as a struct with two binary fields. The encoding is [designed](https://github.com/apache/parquet-format/blob/master/VariantEncoding.md) so engines can efficiently navigate nested structures and extract only the fields they need, rather than parsing the entire binary blob.

```parquet
optional group event_data (VARIANT(1)) {
  required binary metadata;
  required binary value;
}
```

- **`metadata`:** Encodes type information and shared dictionaries (for example, field-name dictionaries for objects). This avoids repeatedly storing the same strings and enables efficient navigation.
- **`value`:** Encodes the actual data in a compact binary form, supporting primitive values as well as arrays and objects.

#### Example

A web access event can be stored in a single Variant column while preserving the original data types:

```json
{
  "userId": 12345,
  "events": [
    {"eType": "login", "timestamp": "2026-01-15T10:30:00Z"},
    {"eType": "purchase", "timestamp": "2026-01-15T11:45:00Z", "amount": 99.99}
  ]
}
```

Compared with storing the same payload as a JSON string, Variant retains type information (for example, timestamp values are stored as integers rather than being stored as strings), which improves correctness, enables more efficient querying and requires fewer bytes to store.

Just as importantly, Variant supports **schema variability**: records with different shapes can coexist in the same column without requiring schema migrations. For example, the following record can be stored alongside the event record above:

```json
{
  "userId": 12345,
  "error": "auth_failure" 
}
```

---

## Shredding Encoding

To enhance query performance and storage efficiency, Variant data can be **shredded** by extracting frequently accessed fields into separate, strongly-typed columns, as described in the [detailed shredding specification](https://github.com/apache/parquet-format/blob/master/VariantShredding.md). For each shredded field:

- If the field **matches the expected schema**, its value is written to the strongly typed field.
- If the field **does not match**, the original representation is written as a Variant-encoded binary field and the corresponding strongly typed field is left NULL.

![Shredding Variant Visualization](/blog/variant/variant_shredding.png)

The Parquet writer, typically a query engine, decides which fields to shred based on access patterns and workload characteristics. Once shredded, the standard Parquet columnar optimizations (encoding, compression, statistics) are used for the typed columns.

### Implementation Considerations

- **Schema Inference:** Engines can infer the shredding schema from sample data by selecting the most frequently occurring type for each field. For example, if `event.id` is predominantly an integer, the engine shreds it to an INT64 column.

- **Type Promotion:** To maximize shredding coverage, engines can promote types within the same type family. For example, if integer values vary in size (INT8, INT32, INT64), selecting INT64 as the shredded type ensures all integer values can be shredded rather than falling back to the unshredded representation.

- **Metadata Control:** To control metadata overhead, engines may limit the number of shredded fields, since each field contributes statistics (min/max values, null counts) to the file footer and column stats.

- **Explicit Shredding Schema:** When read patterns are known in advance, engines can specify an explicit shredding schema at write time, ensuring that frequently accessed fields are shredded for optimal query performance.

### Performance Characteristics

- **Selective field access:** When queries access only the shredded fields, only those columns are read from Parquet, skipping the rest, benefiting from column pruning and predicate pushdown.

- **Full Variant reconstruction:** When queries require access to the complete Variant object, there is a performance overhead as the engine must reconstruct the Variant by merging data from the shredded typed fields and the base Variant column.

### Examples of Shredded Parquet Schemas

The following example shows shredding non-nested Variant values. In this case, the writer chose to shred string values as the `typed_value` column. Rows that do not contain strings are stored in the `value` column with binary Variant encoding.

```parquet
optional group SIMPLE_DATA (VARIANT(1)) = 1 { 
    required binary metadata;             # variant metadata
    optional binary value;                # non-shredded value  	
    optional binary typed_value (STRING); # the shredded value 
}
```

The series of variant values `"Jim"`, `100`, `{"name": "Jim"}` are encoded as:

| Variant Value | `value` | `typed_value` |
|---------------|---------|---------------|
| `"Jim"` | `null` | `"Jim"` |
| `100` | `100` | `null` |
| `{"name": "Jim"}` | `{"name": "Jim"}` | `null` |

---

Shredding nested Variant values is similar, with shredding applied recursively, as shown in the following example. In this case, the `userId` field is shredded as an integer and stored in two columns: `typed_value.userId.typed_value` when the value is an integer, and `typed_value.userId.value` otherwise. Similarly, the `eType` field is shredded as a string and stored in `typed_value.eType.typed_value` and `typed_value.eType.value`.

```parquet
optional group EVENT_DATA (VARIANT(1)) = 1 {
    required binary metadata;                 # variant metadata
    optional binary value;                    # non-shredded value 	
    optional group typed_value {
      required group userId {                 # userId field
        optional binary value;                # non-shredded value
        optional int32 typed_value;           # the shredded value
      }
      required group eType {                  # eType field
        optional binary value;                # non-shredded value
        optional binary typed_value (STRING); # the shredded value
      }
    }
}
```

**The table below illustrates how the data is stored:**

| Variant Value                       | `value`          | `typed_value`<br/>`.userId`<br/>`.value` | `typed_value`<br/>`.userId`<br/>`.typed_value` | `typed_value`<br/>`.eType`<br/>`.value` | `typed_value`<br/>`.eType`<br/>`.typed_value` |
|-------------------------------------|------------------|-----------------------------------------|------------------------------------------------|-----------------------------------------|----------------------------------------------|
| `{"userId": 100, "eType": "login"}` | `null`           | `null`                                  | `100`                                          | `null`                                  | `"login"`                                    |
| `100`                               | `100`            | `null`                                  | `null`                                         | `null`                                  | `null`                                       |
| `{"userId": "Jim"}`                 | `null`           | `"Jim"`                                 | `null`                                         | `null`                                  | `null`                                       |
| `{"userId": 200, "amount": 99}`     | `{"amount": 99}` | `null`                                  | `200`                                          | `null`                                  | `null`                                       |

---

## Ecosystem Adoption: A Success Story

One of the most remarkable aspects of Variant's addition to Parquet is the rapid and widespread ecosystem adoption, demonstrating the strength of collaboration within the Apache Parquet community.

Variant support has been implemented across multiple Parquet libraries including **Java**, **Rust**, and **Go**. For the most current implementation status across all languages and platforms, refer to the [official Parquet implementation status page](https://parquet.apache.org/docs/file-format/implementationstatus/).

Major query engines have also integrated Variant support, including **DuckDB**, **[Apache Spark](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.types.VariantType.html)**, and **[Snowflake](https://docs.snowflake.com/en/sql-reference/data-types-semistructured)**. This cross-ecosystem adoption highlights both the value of the Variant type and the Parquet community's commitment to evolving the format to meet modern data challenges.

---

## Real-World Examples

This section illustrates how users can interact with Variant using [Apache Spark 4.0]

[Apache Spark 4.0]: https://spark.apache.org/releases/spark-release-4-0-0.html

### Event Stream Analytics

Event streaming applications often handle events with evolving schemas, where different event types contain varying fields. Variant provides a flexible solution for storing heterogeneous event data without requiring schema migrations.

**Example: User Activity Events**

```sql
-- Create table with Variant column
CREATE TABLE event_stream (
    event_id INTEGER,
    event_data VARIANT
);

-- Insert events with different schemas
INSERT INTO event_stream VALUES
    (1, PARSE_JSON('{"user": {"id": 100, "country": "US"}, "actions": ["login", "view_dashboard"]}')),
    (2, PARSE_JSON('{"user": {"id": 101, "country": "UK", "premium": true}, "actions": ["login", "upgrade"]}')),
    (3, PARSE_JSON('{"user": {"id": 102, "country": "CA"}, "session_duration": 3600}'));

-- Query events with path notation - handles different schemas gracefully
SELECT 
    event_id,
    event_data:user.id::INTEGER as user_id,
    event_data:user.country::STRING as country,
    event_data:user.premium::BOOLEAN as is_premium
FROM event_stream;
```

---

### IoT Sensor Data

IoT deployments often involve diverse sensor types, each producing data with unique structures. Traditional approaches require either separate tables per sensor type or complex union schemas, or inefficient JSON / BSON encoding. Variant enables unified storage while maintaining type safety.

**Example: Multi-Sensor Data Pipeline**

```sql
-- Create unified sensor table
CREATE TABLE sensor_readings (
    reading_id INTEGER,
    timestamp TIMESTAMP,
    sensor_data VARIANT
);

-- Insert data from different sensor types
INSERT INTO sensor_readings VALUES
    (1, '2026-01-28 10:00:00'::timestamp, 
     PARSE_JSON('{"sensor_id": "T001", "temp": 72.5, "unit": "F", "battery": 95}')),
    (2, '2026-01-28 10:00:05'::timestamp, 
     PARSE_JSON('{"sensor_id": "M001", "motion_detected": true, "confidence": 0.95, "zone": "entrance"}')),
    (3, '2026-01-28 10:00:10'::timestamp, 
     PARSE_JSON('{"sensor_id": "C001", "image_url": "s3://bucket/img_001.jpg", "objects_detected": ["person", "vehicle"]}'));

-- Query temperature sensors only
SELECT 
    reading_id,
    sensor_data:sensor_id::STRING as sensor_id,
    sensor_data:temp::FLOAT as temperature,
    sensor_data:unit::STRING as unit,
    sensor_data:battery::INTEGER as battery_level
FROM sensor_readings
WHERE sensor_data:sensor_id LIKE 'T%';
```

---

## Conclusion

The addition of Variant to Apache Parquet represents a significant milestone in the format's evolution. By standardizing Variant as a logical type within Apache Parquet, the format now provides efficient storage for semi-structured data, enables meaningful statistics collection, and ensures cross-engine interoperability.

The well-documented specification has catalyzed broad ecosystem adoption, with multiple reference implementations now available across languages. This cross-language support ensures that Variant can be seamlessly integrated into diverse data processing environments, from analytical databases to streaming platforms, making it a universal solution for handling evolving schemas in modern data architectures.

---

## Resources

- **Apache Parquet Format Specification:** https://github.com/apache/parquet-format
- **Variant Type Specification:** [Variant Logical Type](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#variant)
- **Variant Encoding Specification:** [Variant Binary Encoding](https://github.com/apache/parquet-format/blob/master/VariantEncoding.md)
- **Variant Shredding Specification:** [Variant Shredding](https://github.com/apache/parquet-format/blob/master/VariantShredding.md)
- **Community Discussions:** dev@parquet.apache.org
