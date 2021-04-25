package com.strafeup.fetchservice.command.impl.statistics;

import com.strafeup.fetchservice.command.Command;
import com.strafeup.fetchservice.model.dto.ReadingDTO;
import com.strafeup.fetchservice.model.service.ReadingsService;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.Collections;
import java.util.List;

public class MinumumCommand implements Command {
    @Autowired
    ReadingsService service;

    @Override
    public List<ReadingDTO> execute(List<ReadingDTO> startingData) {
        return Collections.singletonList(new ReadingDTO(service.minimumValue(startingData)));
    }
}
