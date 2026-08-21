function transform_traefik(tag, timestamp, record)

    -- ==========================================================
    -- DEFAULT METRIC VALUES
    -- ==========================================================

    local api_latency = 0
    local http_4xx_count = 0
    local http_5xx_count = 0

    -- ==========================================================
    -- API LATENCY
    -- ==========================================================

    if record["duration"] ~= nil then

        api_latency = tonumber(record["duration"]) or 0

    end

    -- ==========================================================
    -- HTTP STATUS CODE
    -- ==========================================================

    local status_code = tonumber(
        record["status_code"]
    ) or 0

    if status_code >= 400 and status_code < 500 then

        http_4xx_count = 1

    elseif status_code >= 500 and status_code < 600 then

        http_5xx_count = 1

    end

    -- ==========================================================
    -- REQUEST COUNT
    --
    -- One Traefik event = one request.
    --
    -- Backend aggregation will calculate the actual
    -- request-per-second value.
    -- ==========================================================

    local request_count = 1

    -- ==========================================================
    -- BUILD METRIC RECORD
    -- ==========================================================

    local metric = {}

    metric["api_latency"] = api_latency

    metric["http_4xx_count"] = http_4xx_count

    metric["http_5xx_count"] = http_5xx_count

    metric["request_count"] = request_count

    return 1, timestamp, metric

end