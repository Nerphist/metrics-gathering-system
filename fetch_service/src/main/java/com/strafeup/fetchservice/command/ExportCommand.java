package com.strafeup.fetchservice.command;

import com.strafeup.fetchservice.model.dto.ReadingDTO;
import org.springframework.http.ResponseEntity;

import java.util.List;

public interface ExportCommand {
    ResponseEntity<?> execute(List<ReadingDTO> readingDTOList, String fileName);
}
