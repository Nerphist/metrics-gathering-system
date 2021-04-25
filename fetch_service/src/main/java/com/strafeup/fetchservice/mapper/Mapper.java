package com.strafeup.fetchservice.mapper;

import com.strafeup.fetchservice.model.dto.ReadingDTO;
import com.strafeup.fetchservice.model.dto.ResponseListResultDTO;
import com.strafeup.fetchservice.model.dto.ResponseReadingDTO;
import com.strafeup.fetchservice.model.dto.ResponseSingleValueDTO;

import java.util.List;

public interface Mapper {
    ResponseListResultDTO mapList(List<ReadingDTO> result);

    ResponseSingleValueDTO mapSingleValue(Number value);

    ResponseReadingDTO mapValueToReadingDTO(ReadingDTO readingDTO);
}
