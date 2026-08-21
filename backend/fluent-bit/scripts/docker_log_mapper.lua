function map_docker_log(tag, timestamp, record)

    -- Docker JSON log fields
    local message = record["message"] or record["log"] or ""
    local stream = record["stream"] or "stdout"

    -- Fluent Bit/Docker parsed timestamp
    local docker_time = record["time"]

    -- Convert stream to API level
    local level = "INFO"

    if string.find(string.upper(message), "ERROR") then
        level = "ERROR"
    elseif string.find(string.upper(message), "WARN") then
        level = "WARNING"
    elseif string.find(string.upper(message), "WARNING") then
        level = "WARNING"
    elseif string.find(string.upper(message), "DEBUG") then
        level = "DEBUG"
    end

    -- IMPORTANT:
    -- API expects `timestamp`, not `time`.
    record["timestamp"] = docker_time

    -- API expects `message`
    record["message"] = message

    -- API expects `level`
    record["level"] = level

    -- Keep stream if useful for debugging
    record["stream"] = stream

    -- Remove fields that are not required by LogIngestRequest
    record["log"] = nil
    record["time"] = nil
    record["date"] = nil

    return 1, timestamp, record
end