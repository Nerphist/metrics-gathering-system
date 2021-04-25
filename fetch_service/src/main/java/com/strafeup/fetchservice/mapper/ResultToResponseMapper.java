package com.strafeup.fetchservice.mapper;

import com.strafeup.fetchservice.model.dto.ReadingDTO;
import com.strafeup.fetchservice.model.dto.ResponseListResultDTO;
import com.strafeup.fetchservice.model.dto.ResponseReadingDTO;
import com.strafeup.fetchservice.model.dto.ResponseSingleValueDTO;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;

@AllArgsConstructor(onConstructor_ = @Autowired)
public class ResultToResponseMapper implements Mapper {

    public ResponseListResultDTO mapList(List<ReadingDTO> result) {
        return new ResponseListResultDTO(result);
    }

    public ResponseSingleValueDTO mapSingleValue(Number value) {
        return new ResponseSingleValueDTO(value);
    }

    public ResponseSingleValueDTO mapSingleValueFromList(List<ReadingDTO> result) {
        return new ResponseSingleValueDTO(result.get(0).getValue());
    }

    public ResponseReadingDTO mapValueToReadingDTO(ReadingDTO readingDTO) {
        return new ResponseReadingDTO(readingDTO);
    }

}
