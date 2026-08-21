function convert_stats(tag, timestamp, record)

    if record["CPUPerc"] then
        record["cpu_usage"] =
            tonumber(string.gsub(record["CPUPerc"], "%%", ""))
    end

    if record["MemPerc"] then
        record["memory_usage"] =
            tonumber(string.gsub(record["MemPerc"], "%%", ""))
    end

    return 1, timestamp, record
end