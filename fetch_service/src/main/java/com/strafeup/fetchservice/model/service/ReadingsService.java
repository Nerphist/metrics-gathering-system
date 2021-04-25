package com.strafeup.fetchservice.model.service;

import com.strafeup.fetchservice.model.dto.ReadingDTO;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@AllArgsConstructor(onConstructor_ = @Autowired)
public class ReadingsService {

    private static final Double DEFAULT_DOUBLE = 0.0;
    private static final Long DEFAULT_LONG = 0L;
    private static final Double MIN_VALUE = 0.0;
    private static final Double MAX_VALUE = 0.0;

    public Double averageValue(List<ReadingDTO> startingData) {
        if (startingData.isEmpty()) {
            return DEFAULT_DOUBLE;
        }
        return startingData.stream()
                .mapToDouble(ReadingDTO::getValue)
                .average()
                .orElse(DEFAULT_DOUBLE);
    }

    public Double maximumValue(List<ReadingDTO> startingData) {
        if (startingData.isEmpty()) {
            return DEFAULT_DOUBLE;
        }
        return startingData.stream()
                .mapToDouble(ReadingDTO::getValue)
                .max()
                .orElse(DEFAULT_DOUBLE);
    }

    public Double minimumValue(List<ReadingDTO> startingData) {
        if (startingData.isEmpty()) {
            return DEFAULT_DOUBLE;
        }
        return startingData.stream()
                .mapToDouble(ReadingDTO::getValue)
                .min()
                .orElse(DEFAULT_DOUBLE);
    }

    public Double medianValue(List<ReadingDTO> startingData) {
        if (startingData.isEmpty()) {
            return DEFAULT_DOUBLE;
        }
        ArrayList<ReadingDTO> workingData = new ArrayList<>(startingData);

        Collections.sort(workingData.stream()
                .mapToDouble(ReadingDTO::getValue)
                .boxed()
                .collect(Collectors.toList()));
        Double median;
        if (workingData.size() % 2 == 0)
            median = (workingData.get(workingData.size() / 2).getValue() + workingData.get(workingData.size() / 2).getValue() / 2);
        else
            median = workingData.get(workingData.size() / 2).getValue();

        return median != null ? median : DEFAULT_DOUBLE;
    }

    public Long modeValue(List<ReadingDTO> startingData) {
        if (startingData.isEmpty()) {
            return DEFAULT_LONG;
        }
        ArrayList<ReadingDTO> workingData = new ArrayList<>(startingData);

        Optional<Map.Entry<ReadingDTO, Long>> mode = workingData.stream()
                .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()))
                .entrySet()
                .stream()
                .max(Map.Entry.comparingByValue());

        return mode.get().getValue();
    }

    public ReadingDTO firstInData(List<ReadingDTO> startingData) {
        if (startingData.isEmpty()) {
            return ReadingDTO.EMPTY_DTO;
        }
        return startingData.get(0);
    }

    public ReadingDTO lastInData(List<ReadingDTO> startingData) {
        if (startingData.isEmpty()) {
            return ReadingDTO.EMPTY_DTO;
        }
        return startingData.get(startingData.size() - 1);
    }

}
