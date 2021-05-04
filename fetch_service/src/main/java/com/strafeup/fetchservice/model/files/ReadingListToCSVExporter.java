package com.strafeup.fetchservice.model.files;

import com.opencsv.CSVWriter;
import com.strafeup.fetchservice.command.ExportCommand;
import com.strafeup.fetchservice.model.dto.ReadingDTO;
import lombok.SneakyThrows;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;

import java.io.FileInputStream;
import java.io.FileWriter;
import java.util.List;
import java.util.stream.Collectors;

public class ReadingListToCSVExporter implements ExportCommand {

    @Override
    @SneakyThrows
    public ResponseEntity<?> execute(List<ReadingDTO> readingDTOList, String fileName) {
        List<String[]> lines = convertModelsToCSVLines(readingDTOList);

        // default all fields are enclosed in double quotes
        // default separator is a comma

        try (CSVWriter writer = new CSVWriter(new FileWriter(fileName + ".csv"))) {
            writer.writeAll(lines);
        }
        InputStreamResource resourceCSV = new InputStreamResource(new FileInputStream(fileName + ".csv"));


        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=\"" + fileName + ".csv\"")
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .body(resourceCSV);
    }

    private List<String[]> convertModelsToCSVLines(List<ReadingDTO> readingDTOList) {
        return readingDTOList
                .stream()
                .map(ReadingDTO::toCSV)
                .collect(Collectors.toList());
    }
}
