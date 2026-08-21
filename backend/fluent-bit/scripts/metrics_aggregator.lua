local metrics = {}

function aggregate_metrics(tag, timestamp, record)

    local key = os.date("%Y-%m-%dT%H:%M", timestamp)

    if metrics[key] == nil then
        metrics[key] = {
            timestamp = timestamp,
            cpu_usage = nil,
            memory_usage = nil,
            disk_usage = nil,
            disk_io_wait = nil,
            api_latency = nil,
            http_5xx_count = nil,
            http_4xx_count = nil,
            request_per_second = nil,
            request_count = nil
        }
    end

    local data = metrics[key]

    if tag == "system.metrics.cpu" then

        if record.cpu_p then
            data.cpu_usage = tonumber(record.cpu_p)
        elseif record.cpu_usage then
            data.cpu_usage = tonumber(record.cpu_usage)
        end

    elseif tag == "system.metrics.memory" then

        if record.Mem_Used_PCT then
            data.memory_usage = tonumber(record.Mem_Used_PCT)
        elseif record.memory_usage then
            data.memory_usage = tonumber(record.memory_usage)
        end

    elseif tag == "system.metrics.disk" then

        if record.disk_usage then
            data.disk_usage = tonumber(record.disk_usage)
        end

        if record.disk_io_wait then
            data.disk_io_wait = tonumber(record.disk_io_wait)
        end
    end

    -- Emit once CPU + Memory + Disk are available
    if data.cpu_usage ~= nil
       and data.memory_usage ~= nil
       and data.disk_usage ~= nil then

        local output = {
            timestamp = data.timestamp,

            cpu_usage = data.cpu_usage,
            memory_usage = data.memory_usage,
            disk_usage = data.disk_usage,
            disk_io_wait = data.disk_io_wait,

            api_latency = data.api_latency,
            http_5xx_count = data.http_5xx_count,
            http_4xx_count = data.http_4xx_count,
            request_per_second = data.request_per_second,
            request_count = data.request_count
        }

        metrics[key] = nil

        return 1, timestamp, output
    end

    return -1, timestamp, record
end