
# Enterprise System Design & Scalability (System Design Primer)

Comprehensive engineering patterns for architecting distributed, fault-tolerant, high-concurrency systems, based on standard production benchmarks and the *System Design Primer*.

## 1. Scalability Foundations
- **Vertical Scaling (Scale Up):** Simple, no code changes; limited by hardware cost and single point of failure (SPOF).
- **Horizontal Scaling (Scale Out):** Commodity hardware, high availability; requires stateless application tier, load balancing, and distributed data layers.

## 2. Load Balancing & Traffic Routing
- **Layer 4 (Transport):** Routes TCP/UDP packets by IP and Port (e.g., HAProxy, AWS NLB). Extremely fast, low compute overhead.
- **Layer 7 (Application):** Inspects HTTP headers, cookies, URL paths (e.g., Nginx, Envoy, AWS ALB). Enables smart routing, SSL termination, and rate limiting.
- **Algorithms:** Round Robin, Least Connections, IP Hash / Consistent Hashing (essential for distributed caching to minimize key remapping).

## 3. Caching Architecture
- **Layers:** Client (browser) → CDN (Edge assets) → Reverse Proxy (Varnish/Nginx) → Application Memory → Distributed Cache (Redis/Memcached) → Database Buffer.
- **Cache Invalidation Patterns:**
  - **Cache-Aside (Lazy Loading):** App queries cache; on miss, queries DB and writes to cache. Pros: only requested data is cached. Cons: cache miss penalty, potential stale data.
  - **Write-Through:** App writes to cache, cache writes synchronously to DB. Pros: high data consistency. Cons: write latency.
  - **Write-Behind (Write-Back):** App writes to cache; cache asynchronously writes to DB in batches. Pros: lowest write latency. Cons: data loss risk on cache node crash.
- **Eviction Policies:** LRU (Least Recently Used), LFU (Least Frequently Used), TTL (Time to Live).
- **Pitfalls to Avoid:**
  - **Cache Stampede (Thundering Herd):** Use mutex locks (singleflight) or pre-warming before expiry.
  - **Cache Penetration:** Cache null/empty results or use Bloom Filters for non-existent keys.

## 4. Database Scaling & Data Partitioning
- **Replication:** Primary (Master) handles Writes; Replicas (Slaves) handle Reads. Replication lag must be handled for read-after-write consistency.
- **Federation (Functional Partitioning):** Splitting databases by domain (e.g., Users DB, Orders DB, Products DB).
- **Sharding (Horizontal Partitioning):** Distributing rows across multiple DB instances using a shard key (Hash-based, Range-based, or Directory-based).
  - *Shard Key Rules:* Must ensure uniform distribution; avoid hot shards (e.g., do not shard only by timestamp).
- **CAP Theorem & PACELC:**
  - In a partition (P), choose between Consistency (C) and Availability (A).
  - In normal state (Else), choose between Latency (L) and Consistency (C).

## 5. Asynchronous Processing & Messaging
- **Message Queues:** Decouple producer and consumer, absorb traffic spikes (e.g., RabbitMQ, Celery, Redis Streams).
- **Distributed Event Streams:** High-throughput, persistent, replayable event log (e.g., Apache Kafka).
- **Idempotency:** Guarantee that processing a message multiple times yields the same result (crucial for payment, inventory, and notifications).

## 6. System Design Interview / Architecture Blueprint
When asked to design any system:
1. **Requirements Clarification:** Functional (Core user actions) vs. Non-Functional (QPS, DAU, Latency SLA, Availability 99.99%, Storage growth).
2. **Back-of-the-envelope Estimations:** Calculate Read QPS, Write QPS, Bandwidth (MB/s), and 5-year storage capacity.
3. **High-Level Diagram:** Clients → CDN/DNS → Load Balancer → API Gateway / Stateless Services → Caches & Queues → Sharded DBs / Object Storage.
4. **Deep Dive & Bottleneck Mitigation:** Address single points of failure, redundancy, monitoring, circuit breaking (Hystrix pattern), and rate limiting.
