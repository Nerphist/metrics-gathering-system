package com.strafeup.fetchservice.command;

import com.strafeup.fetchservice.model.dto.ReadingDTO;

import java.util.List;

public interface Command {
    List<ReadingDTO> execute(List<ReadingDTO> startingData);
}
