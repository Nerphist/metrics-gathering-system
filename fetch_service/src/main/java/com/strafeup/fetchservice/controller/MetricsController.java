package com.strafeup.fetchservice.controller;

import com.strafeup.fetchservice.mapper.Mapper;
import com.strafeup.fetchservice.model.dto.ReadingDTO;
import com.strafeup.fetchservice.model.files.ReadingListToCSVExporter;
import com.strafeup.fetchservice.model.files.ReadingListToExcelExporter;
import com.strafeup.fetchservice.model.service.InterpolatorCommand;
import com.strafeup.fetchservice.model.service.ReadingsService;
import com.strafeup.fetchservice.util.Utils;
import lombok.AllArgsConstructor;
import lombok.SneakyThrows;
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
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

@RestController
@RequestMapping("/metrics")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class MetricsController {

    private static final String SERVER_URL_CONTAINER = "http://172.28.0.4:8002/metrics/readings/?";
    private static final String SERVER_URL_LOCALHOST = "http://localhost:8002/metrics/readings/?";

    private static final boolean debug = true;

    private RestTemplate restTemplate;
    private ReadingsService readingsService;
    private InterpolatorCommand interpolatorCommand;
    private Mapper resultToResponseMapper;

    private List<ReadingDTO> fetchDataFromMetricsService(String type, LocalDateTime startTimestamp, LocalDateTime endTimestamp) {
        String requestUrl = debug ? SERVER_URL_LOCALHOST : SERVER_URL_CONTAINER;
        if (type != null && !type.equals("")) {
            String refinedType = Utils.capitalizeWord(type.toLowerCase());
            requestUrl += ("type_name=" + refinedType);
            if (startTimestamp != null) {
                requestUrl += ("&date_start=" + startTimestamp);
                if (endTimestamp != null) {
                    requestUrl += ("&date_end=" + startTimestamp);
                }
            }
        }
        return Arrays.asList(restTemplate.getForObject(requestUrl, ReadingDTO[].class));
    }

    @GetMapping("/stat")
    private ResponseEntity<?> fetchDataStats(@RequestParam(value = "operation", required = false) String operation,
                                             @RequestParam(value = "type", required = false) String type,
                                             @RequestParam(value = "startDate", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTimestamp,
                                             @RequestParam(value = "endDate", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTimestamp,
                                             @RequestParam(value = "timeDelta", required = false) String timeDelta,
                                             @RequestParam(value = "fileName", required = false) String fileName,
                                             @RequestParam(value = "fileType", required = false) String fileType,
                                             @RequestParam(value = "interpolate", required = false, defaultValue = "true") boolean interpolate) {

        ResponseEntity responseEntity = new ResponseEntity(HttpStatus.NOT_FOUND);
        List<ReadingDTO> interpolatedData;

        if (operation == null || operation.equals("")) {
            return new ResponseEntity<>(Collections.emptyList(), HttpStatus.NOT_FOUND);
        }
        if (type != null && !type.equals("")) {

            List<ReadingDTO> readingDTOS = fetchDataFromMetricsService(type, startTimestamp, endTimestamp);

            if (!readingDTOS.isEmpty() && interpolate) {
                interpolatedData = interpolatorCommand.execute(readingDTOS);
            } else {
                interpolatedData = readingDTOS;
            }

            String refinedOperation = operation.toLowerCase();
            responseEntity = performOperation(interpolatedData, refinedOperation);
            if(fileName != null && !fileName.equals("") || fileType != null && !fileType.equals("")){
                switch (fileType) {
                    case "csv":
                        responseEntity = new ReadingListToCSVExporter().execute(interpolatedData, fileName);
                        break;
                    case "xlsx":
                        responseEntity = new ReadingListToExcelExporter().execute(interpolatedData, fileName);
                        break;
                }
                return responseEntity;
            }
        }
        return responseEntity;
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
            case "all":
                return new ResponseEntity(interpolatedData, HttpStatus.OK);
        }

        return new ResponseEntity<>(Collections.EMPTY_LIST, HttpStatus.NOT_FOUND);
    }
}
