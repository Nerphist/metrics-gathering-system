package com.strafeup.fetchservice.controller;

import com.strafeup.fetchservice.mapper.Mapper;
import com.strafeup.fetchservice.model.dto.ReadingDTO;
import com.strafeup.fetchservice.model.service.InterpolatorCommand;
import com.strafeup.fetchservice.model.service.ReadingsService;
import com.strafeup.fetchservice.util.Utils;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/metrics")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class MetricsController {

    private static final String SERVER_URL = "http://localhost:8002/metrics/readings/";
    private RestTemplate restTemplate;
    private ReadingsService readingsService;
    private InterpolatorCommand interpolatorCommand;
    private Mapper resultToResponseMapper;

    private List<ReadingDTO> fetchDataFromMetricsService() {
        return Arrays.asList(restTemplate.getForObject(SERVER_URL, ReadingDTO[].class));
    }

    @GetMapping("/all")
    private ResponseEntity<?> fetchAllDataByParameter(@RequestParam(value = "type", required = false) String type) {
        if (type == null || type.equals("")) {
            return new ResponseEntity<>(fetchDataFromMetricsService(), HttpStatus.OK);
        }
        String refinedType = Utils.capitalizeWord(type.toLowerCase());

        List<ReadingDTO> readingDTOS = Collections.EMPTY_LIST;

        switch (refinedType) {
            case "Temperature": {
                readingDTOS = fetchAllTemperature();
            }
        }

        return readingDTOS.isEmpty()
                ? new ResponseEntity<>(readingDTOS, HttpStatus.NOT_FOUND)
                : new ResponseEntity<>(readingDTOS, HttpStatus.OK);
    }

    @GetMapping("/stat")
    private ResponseEntity<?> fetchDataStats(@RequestParam(value = "operation", required = false) String operation,
                                             @RequestParam(value = "type", required = false) String type,
                                             @RequestParam(value = "startDate", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTimestamp,
                                             @RequestParam(value = "endDate", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTimestamp,
                                             @RequestParam(value = "timeDelta", required = false) String timeDelta) {

        ResponseEntity responseEntity = new ResponseEntity(HttpStatus.NOT_FOUND);
        List<ReadingDTO> interpolatedData;

        if (operation == null || operation.equals("")) {
            return new ResponseEntity<>(Collections.emptyList(), HttpStatus.NOT_FOUND);
        }
        if (type != null && !type.equals("")) {
            String refinedType = Utils.capitalizeWord(type.toLowerCase());

            List<ReadingDTO> readingDTOS = selectMetric(refinedType);

            if (!readingDTOS.isEmpty()) {
                interpolatedData = interpolatorCommand.execute(readingDTOS);
            } else {
                interpolatedData = readingDTOS;
            }

            if (startTimestamp != null) {
                if (endTimestamp != null) {
                    interpolatedData = filterByTwoDates(startTimestamp, endTimestamp, interpolatedData);
                } else {
                    interpolatedData = filterByOneDate(interpolatedData, startTimestamp, timeDelta);
                }
            }

            String refinedOperation = operation.toLowerCase();

            responseEntity = performOperation(interpolatedData, refinedOperation);
        }
        return responseEntity;
    }

    private List<ReadingDTO> filterByOneDate(List<ReadingDTO> interpolatedData, LocalDateTime startTimestamp, String timeDelta) {
        LocalDateTime endOfDay = LocalDateTime.of(startTimestamp.toLocalDate(), LocalTime.MAX);
        return interpolatedData.stream()
                .filter(readingDTO -> readingDTO.getDate().toLocalDate().equals(startTimestamp.toLocalDate()))
                .filter(readingDTO -> readingDTO.getDate().isBefore(endOfDay))
                .collect(Collectors.toList());

    }

    private List<ReadingDTO> filterByTwoDates(LocalDateTime startTimestamp, LocalDateTime endTimestamp, List<ReadingDTO> interpolatedData) {
        return interpolatedData.stream()
                .filter(readingDTO -> readingDTO.getDate().isBefore(endTimestamp))
                .filter(readingDTO -> readingDTO.getDate().isAfter(startTimestamp)).collect(Collectors.toList());
    }

    private ResponseEntity performOperation(List<ReadingDTO> interpolatedData, String type) {

        switch (type) {
            case "average":
                Double average = readingsService.averageValue(interpolatedData);
                return new ResponseEntity<>(resultToResponseMapper.mapSingleValue(average), HttpStatus.OK);
            case "first":
                ReadingDTO firstInData = readingsService.firstInData(interpolatedData);
                return new ResponseEntity<>(resultToResponseMapper.mapValueToReadingDTO(firstInData), HttpStatus.OK);
            case "last":
                ReadingDTO lastInData = readingsService.lastInData(interpolatedData);
                return new ResponseEntity<>(resultToResponseMapper.mapValueToReadingDTO(lastInData), HttpStatus.OK);
            case "max":
                Double max = readingsService.maximumValue(interpolatedData);
                return new ResponseEntity<>(resultToResponseMapper.mapSingleValue(max), HttpStatus.OK);
            case "min":
                Double min = readingsService.minimumValue(interpolatedData);
                return new ResponseEntity<>(resultToResponseMapper.mapSingleValue(min), HttpStatus.OK);
            case "median":
                Double median = readingsService.medianValue(interpolatedData);
                return new ResponseEntity<>(resultToResponseMapper.mapSingleValue(median), HttpStatus.OK);
            case "mode":
                Long mode = readingsService.modeValue(interpolatedData);
                return new ResponseEntity<>(resultToResponseMapper.mapSingleValue(mode), HttpStatus.OK);
        }

        return new ResponseEntity<>(Collections.EMPTY_LIST, HttpStatus.NOT_FOUND);
    }

    private List<ReadingDTO> selectMetric(String type) {
        List<ReadingDTO> readingDTOS = Collections.EMPTY_LIST;
        switch (type) {
            case "Temperature": {
                readingDTOS = fetchAllTemperature();
            }
        }
        return readingDTOS;
    }

    private List<ReadingDTO> fetchAllTemperature() {
        List<ReadingDTO> allData = fetchDataFromMetricsService();
        return allData.stream()
                .filter(readingDTO -> readingDTO.getType().equalsIgnoreCase("temperature"))
                .collect(Collectors.toList());
    }
}
