-- ==========================================================
-- CPU METRIC
-- ==========================================================

function process_cpu(tag, timestamp, record)

    local cpu_usage = record["cpu_p"]

    if cpu_usage == nil then
        cpu_usage = 0
    end

    record["cpu_usage"] = tonumber(cpu_usage)

    record["metric_type"] = "system"

    return 1, timestamp, record
end


-- ==========================================================
-- MEMORY METRIC
-- ==========================================================

function process_memory(tag, timestamp, record)

    local total = tonumber(record["Mem.total"])
    local used = tonumber(record["Mem.used"])

    local memory_usage = 0

    if total ~= nil and used ~= nil and total > 0 then
        memory_usage = (used / total) * 100
    end

    record["memory_usage"] = memory_usage

    record["metric_type"] = "system"

    return 1, timestamp, record
end


-- ==========================================================
-- DISK METRIC
-- ==========================================================

function process_disk(tag, timestamp, record)

    local disk_usage = tonumber(record["disk_usage"])
    local disk_io_wait = tonumber(record["disk_io_wait"])

    if disk_usage == nil then
        disk_usage = 0
    end

    if disk_io_wait == nil then
        disk_io_wait = 0
    end

    record["disk_usage"] = disk_usage
    record["disk_io_wait"] = disk_io_wait

    record["metric_type"] = "system"

    return 1, timestamp, record
end