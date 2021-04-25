package com.strafeup.fetchservice.model.service;

import com.strafeup.fetchservice.command.Command;
import com.strafeup.fetchservice.model.dto.ReadingDTO;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class InterpolatorCommand implements Command {

    public List<ReadingDTO> execute(List<ReadingDTO> startingData) {

        //If there's an empty list or there are insufficient number of elements for interpolation, return empty list.
        if (startingData.isEmpty()) {
            return startingData;
        }
        if (startingData.size() < 3) {
            return startingData;
        }

        ArrayList<ReadingDTO> workingData = new ArrayList<>(startingData);

        for (int i = 0; i < workingData.size() - 1; i++) {
            if (workingData.get(i).getValue() == null) {
                ReadingDTO readingDTOBefore = workingData.get(i - 1);
                ReadingDTO readingDTOAfter = workingData.get(i + 1);

                workingData.get(i).setValue((readingDTOBefore.getValue() - readingDTOAfter.getValue()) / 2);
            }
        }

        if (workingData.get(workingData.size() - 1).getValue() == null) {
            workingData.get(workingData.size() - 1).setValue(workingData.get(workingData.size() - 2).getValue());
        }

        return workingData;
    }
}
