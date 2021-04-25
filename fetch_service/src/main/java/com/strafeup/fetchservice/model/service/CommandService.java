package com.strafeup.fetchservice.model.service;

import com.strafeup.fetchservice.command.Command;
import com.strafeup.fetchservice.command.impl.statistics.*;

import javax.annotation.PostConstruct;
import java.util.Map;


public class CommandService {
    private Map<String, Command> commandMap;

    @PostConstruct
    private void setUp() {
        commandMap.put("average", new AverageValueCommand());
        commandMap.put("first", new FirstInCommand());
        commandMap.put("last", new LastInCommand());
        commandMap.put("max", new MaximumValueCommand());
        commandMap.put("min", new MinumumCommand());
        commandMap.put("median", new MedianValueCommand());
        commandMap.put("mode", new ModeValueCommand());
    }
}
