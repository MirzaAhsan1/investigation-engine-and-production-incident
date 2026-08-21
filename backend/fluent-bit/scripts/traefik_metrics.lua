-- ==========================================================
-- Traefik Metrics Aggregator
-- ==========================================================

local WINDOW_SECONDS = 10

local request_count = 0
local total_latency = 0
local count_4xx = 0
local count_5xx = 0

local window_start = os.time()


-- ==========================================================
-- Aggregate Traefik Request
-- ==========================================================

function aggregate_traefik(tag, timestamp, record)

    -- ------------------------------------------------------
    -- Read values
    -- ------------------------------------------------------

    local status_code = tonumber(record["status_code"])
    local duration = tonumber(record["duration"])


    -- ------------------------------------------------------
    -- Validate status code
    -- ------------------------------------------------------

    if status_code == nil then
        return 0, timestamp, record
    end


    -- ------------------------------------------------------
    -- Validate duration
    -- ------------------------------------------------------

    if duration == nil then
        duration = 0
    end


    -- ------------------------------------------------------
    -- Update counters
    -- ------------------------------------------------------

    request_count = request_count + 1

    total_latency = total_latency + duration


    -- ------------------------------------------------------
    -- HTTP 4xx
    -- ------------------------------------------------------

    if status_code >= 400 and status_code < 500 then
        count_4xx = count_4xx + 1
    end


    -- ------------------------------------------------------
    -- HTTP 5xx
    -- ------------------------------------------------------

    if status_code >= 500 and status_code < 600 then
        count_5xx = count_5xx + 1
    end


    -- ------------------------------------------------------
    -- Check aggregation window
    -- ------------------------------------------------------

    local current_time = os.time()

    local elapsed = current_time - window_start


    -- ------------------------------------------------------
    -- Window not finished
    -- ------------------------------------------------------

    if elapsed < WINDOW_SECONDS then

        -- Drop individual Traefik log.
        -- We only want aggregated metrics.

        return -1, timestamp, record
    end


    -- ======================================================
    -- Calculate metrics
    -- ======================================================

    local api_latency = 0

    local request_per_second = 0


    if request_count > 0 then

        api_latency =
            total_latency / request_count

    end


    if elapsed > 0 then

        request_per_second =
            request_count / elapsed

    end


    -- ======================================================
    -- Create aggregated metric
    -- ======================================================

    local metric = {

        api_key = record["api_key"],

        host = record["host"],

        container_name =
            record["container_name"],

        timestamp = timestamp,

        api_latency = api_latency,

        http_4xx_count = count_4xx,

        http_5xx_count = count_5xx,

        request_per_second =
            request_per_second,
    }


    -- ======================================================
    -- Reset aggregation window
    -- ======================================================

    request_count = 0

    total_latency = 0

    count_4xx = 0

    count_5xx = 0

    window_start = current_time


    -- ======================================================
    -- Return aggregated metric
    -- ======================================================

    return 1, timestamp, metric

end