function fix_level(tag, timestamp, record)
    local status = tonumber(record["status"])
    if status ~= nil and status >= 500 then
        record["level"] = "ERROR"
        record["message"] = (record["message"] or "") .. " -> HTTP " .. status .. " " .. (record["statustext"] or "")
    elseif record["log"] and string.find(record["log"], "ERROR") then
        record["level"] = "ERROR"
        record["message"] = record["log"]
    end
    return 1, timestamp, record
end