"""StateLens Server — SQL Queries.

All raw SQL lives here. No SQL anywhere else in the backend.
"""

# Get all conversations (aggregated from events table)
LIST_CONVERSATIONS = """
    SELECT
        conversation_id AS id,
        MIN(start_time) AS created_at,
        MAX(end_time) AS updated_at,
        COUNT(*) AS total_events,
        CAST(SUM(latency_ms) AS REAL) AS total_latency_ms,
        CASE
            WHEN SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) > 0
            THEN 'failed'
            ELSE 'success'
        END AS status,
        MIN(input) AS first_input
    FROM events
    GROUP BY conversation_id
    ORDER BY MAX(end_time) DESC
"""

# Get a single conversation by ID
GET_CONVERSATION = """
    SELECT
        conversation_id AS id,
        MIN(start_time) AS created_at,
        MAX(end_time) AS updated_at,
        COUNT(*) AS total_events,
        CAST(SUM(latency_ms) AS REAL) AS total_latency_ms,
        CASE
            WHEN SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) > 0
            THEN 'failed'
            ELSE 'success'
        END AS status,
        MIN(input) AS first_input
    FROM events
    WHERE conversation_id = ?
    GROUP BY conversation_id
"""

# Get all events for a conversation, ordered by start time
GET_EVENTS_BY_CONVERSATION = """
    SELECT
        node_id,
        conversation_id,
        node_name,
        node_type,
        start_time,
        end_time,
        latency_ms,
        status,
        input,
        output,
        state_before,
        state_after,
        error
    FROM events
    WHERE conversation_id = ?
    ORDER BY start_time ASC
"""
