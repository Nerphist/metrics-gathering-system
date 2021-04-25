package com.strafeup.fetchservice.model.service;

import com.strafeup.fetchservice.command.Command;
import com.strafeup.fetchservice.model.dto.ReadingDTO;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@AllArgsConstructor(onConstructor_ = @Autowired)
public class ExecutionService {

    Command interpolatorCommand;

    public List<ReadingDTO> executePipeline(List<ReadingDTO> startingData, Command statisticsCommand) {
        List<ReadingDTO> interpolatedData = interpolatorCommand.execute(startingData);

        List<ReadingDTO> execute = statisticsCommand.execute(interpolatedData);

        return execute;
    }
}
